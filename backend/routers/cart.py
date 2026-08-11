from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Transaction, CartItem, User, Scan, Merchant
from schemas.base import CartScanRequest, CartDisplay, CheckoutRequest, CheckoutResponse, CartItemDisplay
from decimal import Decimal

router = APIRouter(tags=["Cart & Checkout"])

@router.post("/scan", response_model=CartDisplay)
async def scan_item(request: CartScanRequest, db: Session = Depends(get_db)):
    # 1. Lookup Product or auto-register scanned barcode
    product = db.query(Product).filter(Product.barcode == request.barcode).first()
    if not product:
        merchant = db.query(Merchant).first()
        merchant_id = merchant.id if merchant else 1
        product = Product(
            merchant_id=merchant_id,
            sku=f"ITEM-{request.barcode[-4:] if len(request.barcode)>=4 else '000'}",
            name=f"Scanned Item (#{request.barcode[-6:] if len(request.barcode)>=6 else request.barcode})",
            price=Decimal("4.99"),
            stock=100,
            category="General Grocery",
            barcode=request.barcode
        )
        db.add(product)
        db.commit()
        db.refresh(product)
    
    # 2. Log Scan
    new_scan = Scan(user_id=request.user_id, barcode=request.barcode, product_id=product.id)
    db.add(new_scan)

    # 3. Find or Create Pending Transaction (The Cart)
    transaction = db.query(Transaction).filter(
        Transaction.user_id == request.user_id, 
        Transaction.status == "pending"
    ).first()

    if not transaction:
        transaction = Transaction(
            user_id=request.user_id, 
            merchant_id=product.merchant_id, 
            status="pending",
            amount=0
        )
        db.add(transaction)
        db.flush() # Get transaction ID

    # 4. Add to CartItems
    cart_item = db.query(CartItem).filter(
        CartItem.transaction_id == transaction.id, 
        CartItem.product_id == product.id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            transaction_id=transaction.id,
            product_id=product.id,
            quantity=1,
            unit_price=product.price
        )
        db.add(cart_item)

    # 5. Update Transaction Amount
    transaction.amount += product.price
    db.commit()

    return await get_cart(request.user_id, db)

@router.get("/{user_id}", response_model=CartDisplay)
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(
        Transaction.user_id == user_id, 
        Transaction.status == "pending"
    ).first()

    if not transaction:
        return {"user_id": user_id, "items": [], "total_amount": 0}

    items = []
    for item in transaction.items:
        items.append(CartItemDisplay(
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price
        ))

    return {
        "user_id": user_id,
        "items": items,
        "total_amount": transaction.amount
    }

@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(
        Transaction.user_id == request.user_id, 
        Transaction.status == "pending"
    ).first()

    if not transaction or not transaction.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Deduct stock and finalize
    for item in transaction.items:
        product = item.product
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        product.stock -= item.quantity
    
    transaction.status = "completed"
    db.commit()

    return {
        "transaction_id": transaction.id,
        "status": "completed",
        "total_amount": transaction.amount
    }
