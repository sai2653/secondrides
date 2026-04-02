from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from sqlalchemy.orm import Session
from typing import Optional
import models, schemas, database
import shutil, os

models.Base.metadata.create_all(bind=database.engine)
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Used Cars E-commerce API",
    docs_url=None,
    redoc_url=None
)

@app.get("/docs", include_in_schema=False)
def custom_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Used Cars API")

@app.get("/redoc", include_in_schema=False)
def custom_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="Used Cars API")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin(username: str, password: str, db: Session):
    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if not admin or admin.password != password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return admin

def get_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid user credentials")
    return user

@app.get("/")
def root():
    return {"message": "API running"}

# ========================
# ADMIN
# ========================

@app.post("/admin/register")
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    db.add(models.Admin(username=admin.username, password=admin.password))
    db.commit()
    return {"message": "Admin created successfully"}

@app.post("/admin/login")
def login_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if not db_admin or db_admin.password != admin.password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"message": "Admin login successful", "username": db_admin.username}

# ========================
# CARS
# ========================

@app.post("/cars/", response_model=schemas.Car)
def create_car(
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    price: float = Form(...),
    mileage: int = Form(...),
    fuel_type: str = Form(...),
    transmission: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    get_admin(username, password, db)
    image_path = f"uploads/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    car = models.Car(
        brand=brand, model=model, year=year, price=price,
        mileage=mileage, fuel_type=fuel_type, transmission=transmission,
        description=description, image_path=image_path
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

@app.get("/cars/", response_model=list[schemas.Car])
def get_cars(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Car).filter(models.Car.is_available == True)
    if min_price:
        query = query.filter(models.Car.price >= min_price)
    if max_price:
        query = query.filter(models.Car.price <= max_price)
    return query.all()

@app.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.patch("/cars/{car_id}/price", response_model=schemas.Car)
def update_price(
    car_id: int,
    data: schemas.CarUpdatePrice,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    get_admin(username, password, db)
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    car.price = data.price
    db.commit()
    db.refresh(car)
    return car

@app.delete("/cars/{car_id}")
def delete_car(
    car_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    get_admin(username, password, db)
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.image_path and os.path.exists(car.image_path):
        os.remove(car.image_path)
    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully"}

# ========================
# USERS
# ========================

@app.post("/users/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username exists")
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/users/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login success", "username": db_user.username}

# ========================
# ENQUIRIES
# ========================

@app.post("/cars/{car_id}/enquiry", response_model=schemas.Enquiry)
def submit_enquiry(
    car_id: int,
    data: schemas.EnquiryCreate,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = get_user(username, password, db)
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    enquiry = models.Enquiry(user_id=user.id, car_id=car_id, message=data.message, phone=data.phone)
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry

@app.get("/admin/enquiries")
def get_all_enquiries(username: str, password: str, db: Session = Depends(get_db)):
    get_admin(username, password, db)
    return db.query(models.Enquiry).all()

# ========================
# WISHLIST
# ========================

@app.post("/cars/{car_id}/wishlist")
def add_to_wishlist(
    car_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = get_user(username, password, db)
    existing = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == user.id,
        models.Wishlist.car_id == car_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in wishlist")
    db.add(models.Wishlist(user_id=user.id, car_id=car_id))
    db.commit()
    return {"message": "Added to wishlist"}

@app.get("/users/wishlist", response_model=list[schemas.WishlistItem])
def get_wishlist(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user(username, password, db)
    return db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).all()

@app.delete("/cars/{car_id}/wishlist")
def remove_from_wishlist(
    car_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = get_user(username, password, db)
    item = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == user.id,
        models.Wishlist.car_id == car_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not in wishlist")
    db.delete(item)
    db.commit()
    return {"message": "Removed from wishlist"}
@app.delete("/admin/enquiries/{enquiry_id}")
def delete_enquiry(
    enquiry_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    get_admin(username, password, db)
    enquiry = db.query(models.Enquiry).filter(models.Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    db.delete(enquiry)
    db.commit()
    return {"message": "Enquiry deleted"}