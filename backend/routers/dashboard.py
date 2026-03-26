from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Transaction, Scan, Product
from ..schemas.base import DashboardSummary, SalesReport, SalesDataPoint
from datetime import datetime, timedelta

router = APIRouter(tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: Session = Depends(get_db)):
    # In a real app, query by merchant_id from token
    revenue = db.query(func.sum(Transaction.amount)).filter(Transaction.status == "completed").scalar() or 0
    active_shoppers = db.query(func.count(func.distinct(Scan.user_id))).filter(Scan.timestamp >= datetime.now() - timedelta(hours=24)).scalar() or 0
    
    # Mock data for complex metrics for now
    return {
        "total_revenue": revenue,
        "active_shoppers": active_shoppers,
        "scans_per_hour": 15.5,
        "avg_basket_value": revenue / 10 if revenue > 0 else 0
    }

@router.get("/sales", response_model=SalesReport)
async def get_sales_report(period: str = "7d", db: Session = Depends(get_db)):
    # Mock time-series data
    data = [
        SalesDataPoint(date="2026-03-20", sales=1200),
        SalesDataPoint(date="2026-03-21", sales=1500),
        SalesDataPoint(date="2026-03-22", sales=900),
        SalesDataPoint(date="2026-03-23", sales=2200),
        SalesDataPoint(date="2026-03-24", sales=1800),
        SalesDataPoint(date="2026-03-25", sales=2500),
        SalesDataPoint(date="2026-03-26", sales=2100),
    ]
    return {"period": period, "data": data}
