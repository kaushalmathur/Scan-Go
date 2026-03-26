from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime, Table, CheckConstraint, text # type: ignore
from sqlalchemy.dialects.postgresql import UUID # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.sql import func # type: ignore
from database import Base # type: ignore

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="basic")
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="merchant")
    products = relationship("Product", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    session_token = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    merchant = relationship("Merchant", back_populates="users")
    scans = relationship("Scan", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), index=True)
    sku = Column(String(100))
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(12, 2), nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String(100))
    barcode = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    merchant = relationship("Merchant", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    scans = relationship("Scan", back_populates="product")

    __table_args__ = (
        CheckConstraint('price >= 0', name='price_check'),
        CheckConstraint('stock >= 0', name='stock_check'),
    )

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    barcode = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scans")
    product = relationship("Product", back_populates="scans")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), index=True)
    amount = Column(DECIMAL(12, 2), default=0)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    items = relationship("CartItem", back_populates="transaction")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='quantity_check'),
    )
