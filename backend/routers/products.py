from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Product, Merchant
from ..schemas.base import ProductCreate, ProductDisplay, ProductUpdate
from ..services.auth import SECRET_KEY, ALGORITHM # Simple way to get merchant_id for now
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(tags=["Products"])

def get_current_merchant_id(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        merchant_id: int = payload.get("merchant_id")
        if merchant_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return merchant_id
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.get("/", response_model=List[ProductDisplay])
async def list_products(merchant_id: int = Query(...), db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.merchant_id == merchant_id).all()

@router.post("/", response_model=ProductDisplay, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db), 
    merchant_id: int = Depends(get_current_merchant_id)
):
    new_product = Product(
        **product_in.dict(),
        merchant_id=merchant_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=ProductDisplay)
async def update_product(
    product_id: int, 
    product_in: ProductUpdate, 
    db: Session = Depends(get_db),
    merchant_id: int = Depends(get_current_merchant_id)
):
    product = db.query(Product).filter(Product.id == product_id, Product.merchant_id == merchant_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or access denied")
    
    update_data = product_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.get("/barcode/{barcode}", response_model=ProductDisplay)
async def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
