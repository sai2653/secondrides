from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    price = Column(Float)
    mileage = Column(Integer)
    fuel_type = Column(String)
    transmission = Column(String)
    description = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    enquiries = relationship("Enquiry", back_populates="car")
    wishlists = relationship("Wishlist", back_populates="car")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    enquiries = relationship("Enquiry", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user")

class Enquiry(Base):
    __tablename__ = "enquiries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    message = Column(String)
    phone = Column(String)
    user = relationship("User", back_populates="enquiries")
    car = relationship("Car", back_populates="enquiries")

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    user = relationship("User", back_populates="wishlists")
    car = relationship("Car", back_populates="wishlists")