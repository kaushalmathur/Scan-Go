from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    merchant_id: Optional[int] = None

class MerchantCreate(BaseModel):
    name: str
    location: Optional[str] = None
    plan: str = "basic"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    store_id: int
    is_merchant: bool = False

class UserDisplay(BaseModel):
    id: int
    email: str
    store_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    sku: str
    name: str
    price: Decimal
    stock: int
    category: str
    barcode: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    name: Optional[str] = None
    category: Optional[str] = None

class ProductDisplay(ProductBase):
    id: int
    merchant_id: int
    class Config:
        from_attributes = True

# --- Cart Schemas ---
class CartScanRequest(BaseModel):
    barcode: str
    user_id: int

class CartItemDisplay(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

class CartDisplay(BaseModel):
    user_id: int
    items: List[CartItemDisplay]
    total_amount: Decimal

# --- Checkout Schemas ---
class CheckoutRequest(BaseModel):
    user_id: int
    payment_method: str = "app"

class CheckoutResponse(BaseModel):
    transaction_id: int
    status: str
    total_amount: Decimal

# --- Dashboard Schemas ---
class DashboardSummary(BaseModel):
    total_revenue: Decimal
    active_shoppers: int
    scans_per_hour: float
    avg_basket_value: Decimal

class SalesDataPoint(BaseModel):
    date: str
    sales: Decimal

class SalesReport(BaseModel):
    period: str
    data: List[SalesDataPoint]
