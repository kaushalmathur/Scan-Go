import pandas as pd
import numpy as np
import logging
import os
import joblib
from datetime import timedelta

# ML Metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Models
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# ----------------------------------------------------------------------
# 1. Setup & Configuration
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_PATH = "data/features.csv"
MODEL_PATH = "models/sales_model.pkl"
FORECAST_PATH = "output/forecast.csv"

def load_and_prep_data():
    """Loads feature matrix and aggregates to daily total sales."""
    logger.info(f"Loading data from {INPUT_PATH}...")
    
    # We create a dummy dataframe structure if it does not exist purely for testing script syntax locally without DB
    if not os.path.exists(INPUT_PATH):
        logger.warning(f"{INPUT_PATH} not found. Creating dummy data for training.")
        dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'scan_time': dates,
            'purchased': np.random.choice([0, 1], size=100, p=[0.2, 0.8])
        })
        df['hour_of_day'] = 12
        df['day_of_week'] = df['scan_time'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['product_category_encoded'] = np.random.randint(0, 5, size=100)
        df['rolling_7d_sales'] = np.random.randint(10, 100, size=100)
    else:
        df = pd.read_csv(INPUT_PATH)
        df['scan_time'] = pd.to_datetime(df['scan_time'])

    logger.info("Aggregating sales by date to form a univariate time series + external regressors.")
    
    # Extract date
    df['date'] = df['scan_time'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    
    # Aggregate daily sales (Total items purchased per day)
    sales_daily = df.groupby('date').agg(
        daily_sales=('purchased', 'sum'),
        avg_rolling=('rolling_7d_sales', 'mean'),
        day_of_week=('day_of_week', 'first'),
        is_weekend=('is_weekend', 'first')
    ).reset_index()

    sales_daily.sort_values('date', inplace=True)
    sales_daily.set_index('date', inplace=True)
    
    # Ensure there is NO missing dates in index
    sales_daily = sales_daily.asfreq('D').fillna(method='ffill').fillna(0)
    
    return sales_daily

def evaluate_model(y_true, y_pred, model_name="Model"):
    """Calculates forecasting metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return {"Model": model_name, "MAE": mae, "RMSE": rmse, "R2": r2}

def train_arima(train, test):
    """Trains an ARIMA model on daily_sales."""
    logger.info("Training ARIMA...")
    # Order (p,d,q) chosen arbitrarily for automated script.
    model = ARIMA(train['daily_sales'], order=(5, 1, 0))
    model_fit = model.fit()
    
    predictions = model_fit.forecast(steps=len(test))
    return evaluate_model(test['daily_sales'], predictions, "ARIMA")

def train_prophet(train, test):
    """Trains a Prophet model."""
    logger.info("Training Prophet...")
    
    # Prophet requires columns 'ds' and 'y'
    df_train = train.reset_index().rename(columns={'date': 'ds', 'daily_sales': 'y'})
    df_test = test.reset_index().rename(columns={'date': 'ds', 'daily_sales': 'y'})
    
    model = Prophet(daily_seasonality=True)
    
    # Adding regressors
    for col in ['avg_rolling', 'day_of_week', 'is_weekend']:
        model.add_regressor(col)
        
    model.fit(df_train)
    
    # Predict on test set
    future = df_test[['ds', 'avg_rolling', 'day_of_week', 'is_weekend']]
    forecast = model.predict(future)
    
    predictions = forecast['yhat'].values
    return evaluate_model(df_test['y'], predictions, "Prophet")

def train_rf(X_train, y_train, X_test, y_test):
    """Trains a Random Forest Regressor."""
    logger.info("Training Random Forest...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    results = evaluate_model(y_test, predictions, "Random Forest")
    return model, results

def train_xgb(X_train, y_train, X_test, y_test):
    """Trains an XGBoost Regressor."""
    logger.info("Training XGBoost...")
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    return evaluate_model(y_test, predictions, "XGBoost")

def generate_forecast(model, last_date, last_data, days=30):
    """Generates a 30-day forecast using the trained Random Forest."""
    logger.info(f"Generating {days}-day forecast using Random Forest...")
    
    future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
    
    # Mock future features (in reality, we'd extrapolate or use known future values)
    future_records = []
    
    current_rolling = last_data['avg_rolling']
    
    for d in future_dates:
        record = {
            'date': d,
            'avg_rolling': current_rolling, # Holding rolling steady for baseline
            'day_of_week': d.weekday(),
            'is_weekend': 1 if d.weekday() >= 5 else 0
        }
        future_records.append(record)
        
    future_df = pd.DataFrame(future_records)
    future_X = future_df[['avg_rolling', 'day_of_week', 'is_weekend']]
    
    # Predict
    forecast_y = model.predict(future_X)
    future_df['predicted_sales'] = np.maximum(0, np.round(forecast_y, 0)) # Max 0 to prevent negative sales
    
    # Drop modeling cols for clean output
    out_df = future_df[['date', 'predicted_sales']]
    
    # Save
    os.makedirs(os.path.dirname(FORECAST_PATH), exist_ok=True)
    out_df.to_csv(FORECAST_PATH, index=False)
    logger.info(f"Forecast saved to {FORECAST_PATH}")

def main():
    logger.info("Starting Forecasting Training Script...")
    
    # 1. Load Data
    df = load_and_prep_data()
    
    if len(df) < 14:
        logger.error("Not enough data to train. Need at least 14 days.")
        return
        
    # 2. Train-Test Split (80/20 chronological)
    train_size = int(len(df) * 0.8)
    train, test = df.iloc[:train_size], df.iloc[train_size:]
    
    logger.info(f"Train size: {len(train)} days | Test size: {len(test)} days")
    
    # Features & Target for Tree Models
    features = ['avg_rolling', 'day_of_week', 'is_weekend']
    target = 'daily_sales'
    
    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]
    
    # 3. Train & Evaluate Models
    results = []
    
    # ARIMA
    try:
        results.append(train_arima(train, test))
    except Exception as e:
         logger.warning(f"ARIMA failed: {e}")
         
    # Prophet
    try:
        results.append(train_prophet(train, test))
    except Exception as e:
         logger.warning(f"Prophet failed: {e}")
         
    # Random Forest
    rf_model, rf_res = train_rf(X_train, y_train, X_test, y_test)
    results.append(rf_res)
    
    # XGBoost
    results.append(train_xgb(X_train, y_train, X_test, y_test))
    
    # 4. Print Comparison Table
    results_df = pd.DataFrame(results)
    
    print("\n" + "="*50)
    print("      MODEL PERFORMANCE COMPARISON (TEST SET)")
    print("="*50)
    print(results_df.to_string(index=False))
    print("="*50 + "\n")
    
    # 5. Save the best model (Requested: Random Forest)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(rf_model, MODEL_PATH)
    logger.info(f"Saved Random Forest model to {MODEL_PATH}")
    
    # 6. Generate 30-Day Forecast
    last_date = df.index[-1]
    last_data = df.iloc[-1]
    
    generate_forecast(rf_model, last_date, last_data, days=30)
    
    logger.info("Script execution complete.")

if __name__ == "__main__":
    main()
