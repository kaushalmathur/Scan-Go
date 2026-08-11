from database import SessionLocal, engine, Base  # type: ignore
from models import Merchant, User, Product  # type: ignore
from services.auth import get_password_hash  # type: ignore
import sys

def seed_db():
    print("Setting up database structure...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Create a Merchant if it doesn't exist
    merchant = db.query(Merchant).filter(Merchant.name == "Demo Store").first()
    if not merchant:
        merchant = Merchant(name="Demo Store", location="123 Test Ave")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        print("Created Demo Store.")

    # 2. Create an admin user to login
    user = db.query(User).filter(User.email == "test@scango.com").first()
    if not user:
        user = User(
            store_id=merchant.id,
            email="test@scango.com",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        print("Created User: test@scango.com / password123")
        
    # 3. Create Sample Products
    sample_products = [
        {"sku": "DEMO-01", "name": "Scan & Go Energy Drink", "price": 3.99, "stock": 100, "category": "Beverages", "barcode": "123456789012"},
        {"sku": "DEMO-02", "name": "Organic Whole Milk 1L", "price": 2.49, "stock": 50, "category": "Dairy", "barcode": "8901030953613"},
        {"sku": "DEMO-03", "name": "Crunchy Potato Chips 150g", "price": 1.99, "stock": 150, "category": "Snacks", "barcode": "079238237012"},
        {"sku": "DEMO-04", "name": "Dark Chocolate Bar 85%", "price": 4.50, "stock": 80, "category": "Confectionery", "barcode": "5000159461122"},
        {"sku": "DEMO-05", "name": "Sparkling Mineral Water 500ml", "price": 1.29, "stock": 200, "category": "Beverages", "barcode": "3057640100473"},
        {"sku": "DEMO-06", "name": "Arabica Espresso Coffee Beans 250g", "price": 8.99, "stock": 40, "category": "Pantry", "barcode": "8000070010567"},
    ]

    for p_data in sample_products:
        product = db.query(Product).filter(Product.barcode == p_data["barcode"]).first()
        if not product:
            product = Product(
                merchant_id=merchant.id,
                sku=p_data["sku"],
                name=p_data["name"],
                price=p_data["price"],
                stock=p_data["stock"],
                category=p_data["category"],
                barcode=p_data["barcode"]
            )
            db.add(product)
            db.commit()
            print(f"Created Product '{product.name}' (Barcode: {product.barcode})")

    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_db()
