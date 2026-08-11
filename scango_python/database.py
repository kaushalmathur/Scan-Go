import os
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Table
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
    name = Column(String, nullable=False, default="Demo Store #01")
    location = Column(String, default="123 Retail Ave, Suite 100")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="merchant")
    products = relationship("Product", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")

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
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=100)
    category = Column(String, default="General Grocery")
    barcode = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    scans = relationship("Scan", back_populates="product")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    barcode = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    product = relationship("Product", back_populates="scans")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    merchant_id = Column(Integer, ForeignKey("merchants.id"), default=1)
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_method = Column(String, default="card")
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
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
        merchant = Merchant(id=1, name="Demo Store #01", location="123 Retail Ave, Suite 100")
        db.add(merchant)
        db.commit()

    # 2. Ensure Admin User exists
    admin_user = db.query(User).filter(User.email == "test@scango.com").first()
    if not admin_user:
        admin_user = User(
            merchant_id=1,
            email="test@scango.com",
            hashed_password=hash_password("password123"),
            role="merchant"
        )
        db.add(admin_user)
        db.commit()

    # 3. Seed Sample Store Inventory Products
    sample_products = [
        {"sku": "SKU-101", "name": "Scan & Go Energy Drink", "price": 3.99, "stock": 120, "category": "Beverages", "barcode": "123456789012"},
        {"sku": "SKU-102", "name": "Organic Whole Milk 1L", "price": 2.49, "stock": 45, "category": "Dairy", "barcode": "8901030953613"},
        {"sku": "SKU-103", "name": "Crunchy Potato Chips 150g", "price": 1.99, "stock": 180, "category": "Snacks", "barcode": "079238237012"},
        {"sku": "SKU-104", "name": "Dark Chocolate Bar 85%", "price": 4.50, "stock": 90, "category": "Confectionery", "barcode": "5000159461122"},
        {"sku": "SKU-105", "name": "Sparkling Mineral Water 500ml", "price": 1.29, "stock": 250, "category": "Beverages", "barcode": "3057640100473"},
        {"sku": "SKU-106", "name": "Arabica Espresso Coffee Beans 250g", "price": 8.99, "stock": 35, "category": "Pantry", "barcode": "8000070010567"},
    ]

    for p in sample_products:
        existing = db.query(Product).filter(Product.barcode == p["barcode"]).first()
        if not existing:
            new_prod = Product(
                merchant_id=1,
                sku=p["sku"],
                name=p["name"],
                price=p["price"],
                stock=p["stock"],
                category=p["category"],
                barcode=p["barcode"]
            )
            db.add(new_prod)
            db.commit()

    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized & seeded successfully!")
