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
        
    # 3. Create a Demo Product mapping to a standard barcode you might scan on your desk
    demo_barcode = "123456789012"
    product = db.query(Product).filter(Product.barcode == demo_barcode).first()
    if not product:
        product = Product(
            merchant_id=merchant.id,
            sku="DEMO-01",
            name="Scan & Go Energy Drink",
            price=3.99,
            stock=100,
            category="Beverages",
            barcode=demo_barcode
        )
        db.add(product)
        db.commit()
        print(f"Created Product '{product.name}' with barcode {demo_barcode}")

    db.close()
    print("Seeding complete! You are ready to test.")

if __name__ == "__main__":
    seed_db()
