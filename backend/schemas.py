from pydantic import BaseModel, EmailStr
from typing import Optional, List

# --- Car ---
class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    price: float
    mileage: int
    fuel_type: str
    transmission: str
    description: Optional[str] = None

class CarUpdatePrice(BaseModel):
    price: float

class Car(CarBase):
    id: int
    image_path: Optional[str] = None
    is_available: bool

    class Config:
        from_attributes = True

# --- User ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# --- Admin ---
class AdminCreate(BaseModel):
    username: str
    password: str

# --- Enquiry ---
class EnquiryCreate(BaseModel):
    message: str
    phone: str

class Enquiry(BaseModel):
    id: int
    car_id: int
    message: str
    phone: str

    class Config:
        from_attributes = True

# --- Wishlist ---
class WishlistItem(BaseModel):
    id: int
    car_id: int

    class Config:
        from_attributes = True