import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, products, cart, dashboard
from seed import seed_db

app = FastAPI(title="Scan & Go API", version="1.0.0")

# Auto-initialize database tables & seed data on startup
@app.on_event("startup")
def startup_db_check():
    Base.metadata.create_all(bind=engine)
    try:
        seed_db()
    except Exception as e:
        print(f"Seed check: {e}")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(cart.router, prefix="/cart")
app.include_router(dashboard.router, prefix="/dashboard")

@app.get("/")
async def root():
    return {"message": "Welcome to Scan & Go Platform API"}
