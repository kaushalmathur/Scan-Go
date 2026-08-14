import os
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from passlib.context import CryptContext

# Database File Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scango_pure.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

# --- SQLAlchemy ORM Models ---

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="Retail Enterprise Corp")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="merchant")
    outlets = relationship("Outlet", back_populates="merchant")
    products = relationship("Product", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")

class Outlet(Base):
    __tablename__ = "outlets"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), default=1)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, default="Central City")
    distance_km = Column(Float, default=1.2)
    opening_hours = Column(String, default="08:00 AM - 10:00 PM")
    contact_phone = Column(String, default="+1 (555) 019-2834")
    image_url = Column(String, default="https://images.unsplash.com/photo-1578916171728-46686eac8d58")
    created_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="outlets")
    products = relationship("Product", back_populates="outlet")
    transactions = relationship("Transaction", back_populates="outlet")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), default=1)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="shopper") # shopper / merchant
    created_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="users")
    transactions = relationship("Transaction", back_populates="user")
    scans = relationship("Scan", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), default=1)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), default=1)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percent = Column(Float, default=0.0) # e.g. 15.0 for 15% off
    stock = Column(Integer, default=100)
    is_in_stock = Column(Boolean, default=True)
    is_new_launch = Column(Boolean, default=False)
    category = Column(String, default="General Grocery")
    barcode = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="products")
    outlet = relationship("Outlet", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    scans = relationship("Scan", back_populates="product")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    outlet_id = Column(Integer, ForeignKey("outlets.id"), default=1)
    barcode = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    product = relationship("Product", back_populates="scans")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    merchant_id = Column(Integer, ForeignKey("merchants.id"), default=1)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), default=1)
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_method = Column(String, default="card")
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    outlet = relationship("Outlet", back_populates="transactions")
    items = relationship("CartItem", back_populates="transaction")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

# --- Database Initialization & Seeding ---

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Ensure Merchant exists
    merchant = db.query(Merchant).filter(Merchant.id == 1).first()
    if not merchant:
        merchant = Merchant(id=1, name="Retail Enterprise Corp")
        db.add(merchant)
        db.commit()

    # 2. Seed Physical Outlets
    sample_outlets = [
        {
            "id": 1,
            "name": "Downtown Superstore Outlet #01",
            "address": "123 Main Street, Suite 100",
            "city": "Central City",
            "distance_km": 0.8,
            "opening_hours": "08:00 AM - 10:00 PM",
            "contact_phone": "+1 (555) 019-2834"
        },
        {
            "id": 2,
            "name": "Westside Express Retail Outlet #02",
            "address": "456 West Avenue, Plaza Mall",
            "city": "Metro Center",
            "distance_km": 2.4,
            "opening_hours": "07:30 AM - 11:00 PM",
            "contact_phone": "+1 (555) 019-5821"
        },
        {
            "id": 3,
            "name": "Suburban Hypermarket Outlet #03",
            "address": "789 Oak Road, Sector 5",
            "city": "Greenfield",
            "distance_km": 4.1,
            "opening_hours": "09:00 AM - 09:30 PM",
            "contact_phone": "+1 (555) 019-9942"
        }
    ]

    for o in sample_outlets:
        existing_o = db.query(Outlet).filter(Outlet.id == o["id"]).first()
        if not existing_o:
            new_o = Outlet(
                id=o["id"],
                merchant_id=1,
                name=o["name"],
                address=o["address"],
                city=o["city"],
                distance_km=o["distance_km"],
                opening_hours=o["opening_hours"],
                contact_phone=o["contact_phone"]
            )
            db.add(new_o)
            db.commit()

    # 3. Ensure Default Users exist
    shopper_user = db.query(User).filter(User.email == "customer@scango.com").first()
    if not shopper_user:
        shopper_user = User(
            merchant_id=1,
            email="customer@scango.com",
            hashed_password=hash_password("password123"),
            role="shopper"
        )
        db.add(shopper_user)

    merchant_user = db.query(User).filter(User.email == "test@scango.com").first()
    if not merchant_user:
        merchant_user = User(
            merchant_id=1,
            email="test@scango.com",
            hashed_password=hash_password("password123"),
            role="merchant"
        )
        db.add(merchant_user)
    
    db.commit()

    # 4. Seed Physical Store Products (Linked to Outlets with Offers & New Launches)
    sample_products = [
        # Outlet 1 Products
        {"outlet_id": 1, "sku": "SKU-101", "name": "Scan & Go Energy Drink 330ml", "price": 3.49, "original_price": 3.99, "discount_percent": 12.5, "stock": 120, "is_in_stock": True, "is_new_launch": True, "category": "Beverages", "barcode": "123456789012"},
        {"outlet_id": 1, "sku": "SKU-102", "name": "Organic Whole Milk 1L", "price": 2.49, "original_price": 2.99, "discount_percent": 16.7, "stock": 45, "is_in_stock": True, "is_new_launch": False, "category": "Dairy", "barcode": "8901030953613"},
        {"outlet_id": 1, "sku": "SKU-103", "name": "Crunchy Potato Chips 150g", "price": 1.99, "original_price": 1.99, "discount_percent": 0.0, "stock": 0, "is_in_stock": False, "is_new_launch": False, "category": "Snacks", "barcode": "079238237012"},
        {"outlet_id": 1, "sku": "SKU-104", "name": "Dark Chocolate Bar 85%", "price": 3.60, "original_price": 4.50, "discount_percent": 20.0, "stock": 90, "is_in_stock": True, "is_new_launch": True, "category": "Confectionery", "barcode": "5000159461122"},
        {"outlet_id": 1, "sku": "SKU-105", "name": "Sparkling Mineral Water 500ml", "price": 1.29, "original_price": 1.29, "discount_percent": 0.0, "stock": 250, "is_in_stock": True, "is_new_launch": False, "category": "Beverages", "barcode": "3057640100473"},
        {"outlet_id": 1, "sku": "SKU-106", "name": "Arabica Espresso Coffee Beans 250g", "price": 7.19, "original_price": 8.99, "discount_percent": 20.0, "stock": 35, "is_in_stock": True, "is_new_launch": True, "category": "Pantry", "barcode": "8000070010567"},

        # Outlet 2 Products
        {"outlet_id": 2, "sku": "SKU-201", "name": "Artisanal Sourdough Bread", "price": 4.99, "original_price": 5.99, "discount_percent": 16.6, "stock": 25, "is_in_stock": True, "is_new_launch": True, "category": "Bakery", "barcode": "9780201379624"},
        {"outlet_id": 2, "sku": "SKU-202", "name": "Greek Yogurt Vanilla 500g", "price": 3.29, "original_price": 3.99, "discount_percent": 17.5, "stock": 60, "is_in_stock": True, "is_new_launch": False, "category": "Dairy", "barcode": "012345678905"},
        {"outlet_id": 2, "sku": "SKU-203", "name": "Cold Brew Iced Coffee 400ml", "price": 2.99, "original_price": 3.99, "discount_percent": 25.0, "stock": 0, "is_in_stock": False, "is_new_launch": True, "category": "Beverages", "barcode": "5012345678900"},
    ]

    for p in sample_products:
        existing = db.query(Product).filter(Product.barcode == p["barcode"]).first()
        if not existing:
            new_prod = Product(
                merchant_id=1,
                outlet_id=p["outlet_id"],
                sku=p["sku"],
                name=p["name"],
                price=p["price"],
                original_price=p["original_price"],
                discount_percent=p["discount_percent"],
                stock=p["stock"],
                is_in_stock=p["is_in_stock"],
                is_new_launch=p["is_new_launch"],
                category=p["category"],
                barcode=p["barcode"]
            )
            db.add(new_prod)
            db.commit()

    db.close()

if __name__ == "__main__":
    init_db()
    print("Multi-Outlet Database Schema initialized & seeded successfully!")
