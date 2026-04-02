from database import SessionLocal
from models import Admin   # ✅ use Admin, not User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

admin = Admin(
    username="admin",
    password=pwd_context.hash("admin123")
)

db.add(admin)
db.commit()
db.close()

print("Admin created")