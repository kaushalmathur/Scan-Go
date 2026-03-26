from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta
import time

# ----------------------------------------------------------------------
# 1. API Configuration & Logging Setup
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger("ML_Inference")

app = FastAPI(title="Scan & Go ML Inference Engine", version="1.0.0")

# Model Paths
MODEL_DIR = "models"
SALES_MODEL_PATH = os.path.join(MODEL_DIR, "sales_model.pkl")

# In-memory Model Cache
loaded_models = {
    "sales_forecast": None,  # Random Forest
    "churn": None,           # Logistic Regression (placeholder)
    "recommendation": None   # Collaborative Filtering (placeholder)
}

startup_time = None

# Pydantic Schemas
class SalesRequest(BaseModel):
    store_id: int
    date_range: int = 30  # Default 30-day forecast

class ChurnRequest(BaseModel):
    user_id: int

class RecommendRequest(BaseModel):
    user_id: int
    cart_items: List[int]  # List of product IDs

# ----------------------------------------------------------------------
# 2. Application Startup (Model Loading)
# ----------------------------------------------------------------------
@app.on_event("startup")
async def load_models():
    """Load machine learning models into memory at server startup."""
    global startup_time
    startup_time = datetime.now()
    
    logger.info("Initializing ML Inference Engine...")
    
    # 1. Load Sales Forecast Model
    if os.path.exists(SALES_MODEL_PATH):
        try:
            loaded_models["sales_forecast"] = joblib.load(SALES_MODEL_PATH)
            logger.info(f"Loaded Sales Model from {SALES_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load Sales Model: {e}")
    else:
        logger.warning(f"Sales Model not found at {SALES_MODEL_PATH}. Inference will fail.")

    # 2. Mocking Churn & Recommendation Models for now
    # In a full pipeline, you'd load joblib.load(CHURN_PATH) here
    logger.info("Mocking Churn & Recommendation engines for demonstration.")
    loaded_models["churn"] = "mock_logistic_regression"
    loaded_models["recommendation"] = "mock_collab_filtering"

# ----------------------------------------------------------------------
# 3. API Endpoints
# ----------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Returns model loading status and engine uptime."""
    status = {
        "engine_uptime_seconds": (datetime.now() - startup_time).total_seconds(),
        "models": {
            "sales": "Available" if loaded_models["sales_forecast"] else "Missing",
            "churn": "Available" if loaded_models["churn"] else "Missing",
            "recommendation": "Available" if loaded_models["recommendation"] else "Missing",
        },
        "last_refresh": str(startup_time)
    }
    return status

@app.post("/predict/sales")
async def forecast_sales(request: SalesRequest):
    """Predicts future N-day sales using the trained Random Forest."""
    start_time = time.time()
    
    model = loaded_models["sales_forecast"]
    if not model:
        raise HTTPException(status_code=503, detail="Sales forecasting model is currently unavailable.")
    
    try:
        # Generate dummy future feature sets since we don't hold state here
        # X features required: ['avg_rolling', 'day_of_week', 'is_weekend']
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, request.date_range + 1)]
        
        # We assume the rolling 7-day average sales sits around 150 globally
        features = [{
            'avg_rolling': 150.0,
            'day_of_week': d.weekday(),
            'is_weekend': 1 if d.weekday() >= 5 else 0
        } for d in future_dates]
        
        future_df = pd.DataFrame(features)
        
        # Inference
        predictions = model.predict(future_df)
        
        results = [
            {"date": d.strftime("%Y-%m-%d"), "predicted_sales": max(0, int(p))} 
            for d, p in zip(future_dates, predictions)
        ]
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return {
            "store_id": request.store_id,
            "forecast_days": request.date_range,
            "predictions": results,
            "processing_time_ms": round(processing_time_ms, 2)
        }
        
    except Exception as e:
        logger.error(f"Sales inference failed: {e}")
        raise HTTPException(status_code=500, detail="Internal inference error.")


@app.post("/predict/churn")
async def predict_churn(request: ChurnRequest):
    """Calculates customer churn probability based on session drops."""
    start_time = time.time()
    
    if not loaded_models["churn"]:
        raise HTTPException(status_code=503, detail="Churn prediction model is unavailable.")
        
    # Mocking a Logistic Regression Probability Calculation based on User ID parity
    # Simulated logical pattern: Even ID = low risk, Odd ID = high risk
    probability = 0.85 if request.user_id % 2 == 1 else 0.15
    threshold = 0.5
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    return {
        "user_id": request.user_id,
        "churn_probability": probability,
        "is_at_risk": probability > threshold,
        "processing_time_ms": round(processing_time_ms, 2)
    }


@app.post("/recommend")
async def product_recommendations(request: RecommendRequest):
    """Yields 3 next-best-action products for a scanning cart context."""
    start_time = time.time()
    
    if not loaded_models["recommendation"]:
         raise HTTPException(status_code=503, detail="Recommendation engine is unavailable.")
    
    # Collaborative filtering mock: we pretend we mapped their cart items to nearest neighbors
    # For now, return generic top products that pair with their cart.
    mock_suggestions = [101, 204, 305]  # Product IDs
    cross_sell_matrix = {
        "recommendations": mock_suggestions,
        "confidence_scores": [0.92, 0.76, 0.65]
    }
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    return {
        "user_id": request.user_id,
        "context_cart": request.cart_items,
        "suggested_product_ids": cross_sell_matrix["recommendations"],
        "confidence_scores": cross_sell_matrix["confidence_scores"],
        "processing_time_ms": round(processing_time_ms, 2)
    }

# Entry block for uvicorn rapid testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("inference_api:app", host="0.0.0.0", port=8001, reload=True)
