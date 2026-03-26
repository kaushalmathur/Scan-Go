import pandas as pd
import numpy as np
import logging
import os
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# 1. Configuration & Logging Setup
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="../backend/.env") # Path relative to working dir typical for scripts
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/scango")

OUTPUT_PATH = "data/features.csv"

def extract_data(engine):
    """Pulls data from transactions, scans, and products tables to form a base dataframe."""
    logger.info("Extracting data from PostgreSQL...")
    
    # Simple join to get relevant transaction, scan, and product details.
    # In a real scenario, this query would be carefully tailored to the specific ML objective.
    query = """
    SELECT 
        s.id as scan_id,
        s.user_id,
        s.timestamp as scan_time,
        p.id as product_id,
        p.category as product_category,
        p.price,
        t.status as transaction_status,
        t.created_at as transaction_time
    FROM scans s
    LEFT JOIN products p ON s.product_id = p.id
    LEFT JOIN cart_items ci ON ci.product_id = p.id
    LEFT JOIN transactions t ON ci.transaction_id = t.id AND t.user_id = s.user_id
    """
    
    df = pd.read_sql(query, engine)
    logger.info(f"Extracted {len(df)} records from database.")
    return df

def clean_data(df):
    """Removes nulls, parses timestamps, deduplicates."""
    logger.info("Cleaning data...")
    
    # 1. Deduplicate
    initial_len = len(df)
    df = df.drop_duplicates(subset=['scan_id', 'transaction_time'])
    logger.info(f"Removed {initial_len - len(df)} duplicate rows.")
    
    # 2. Parse Timestamps
    df['scan_time'] = pd.to_datetime(df['scan_time'])
    df['transaction_time'] = pd.to_datetime(df['transaction_time'])
    
    # 3. Handle Nulls
    # Drop rows where critical info like product or category is missing
    df = df.dropna(subset=['product_id', 'product_category'])
    
    # For transaction_time, if it's null, it implies the item was scanned but not bought (abandoned logic)
    # We will keep them but mark a binary 'purchased' flag later
    
    logger.info(f"Data cleaning complete. {len(df)} records remaining.")
    return df

def engineer_features(df):
    """Engineers time and category-based features."""
    logger.info("Engineering features...")
    
    # Target variable proxy: did they actually buy it?
    df['purchased'] = df['transaction_status'].apply(lambda x: 1 if x == 'completed' else 0)
    
    # 1. Time-based features
    df['hour_of_day'] = df['scan_time'].dt.hour
    df['day_of_week'] = df['scan_time'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # 2. Categorical Encoding (product_category)
    logger.info("Encoding categorical features...")
    le = LabelEncoder()
    df['product_category_encoded'] = le.fit_transform(df['product_category'].astype(str))
    
    # 3. Rolling 7-day sales (mock up logic based on daily aggregations)
    logger.info("Calculating rolling 7-day sales per product...")
    
    # Create a daily sales dataframe for products
    # We only count completed transactions for sales
    sales_df = df[df['purchased'] == 1].copy()
    sales_df['date'] = sales_df['scan_time'].dt.date
    daily_sales = sales_df.groupby(['product_id', 'date']).size().reset_index(name='daily_count')
    
    # Sort and calculate rolling sum
    daily_sales['date'] = pd.to_datetime(daily_sales['date'])
    daily_sales = daily_sales.sort_values(by=['product_id', 'date'])
    
    # Set index to date for rolling operation
    daily_sales = daily_sales.set_index('date')
    rolling_sales = daily_sales.groupby('product_id')['daily_count'].rolling(window='7D').sum().reset_index()
    rolling_sales = rolling_sales.rename(columns={'daily_count': 'rolling_7d_sales'})
    
    # Merge the rolling features back to the main dataframe
    df['date'] = df['scan_time'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    
    df = pd.merge(df, rolling_sales, on=['product_id', 'date'], how='left')
    
    # Fill NaN rolling sales with 0 (e.g., first day or items with no previous sales)
    df['rolling_7d_sales'] = df['rolling_7d_sales'].fillna(0)
    
    # Drop intermediate column
    df = df.drop(columns=['date'])
    
    logger.info("Feature engineering complete.")
    return df

def save_features(df, output_path):
    """Saves the final dataframe to a CSV."""
    logger.info(f"Saving feature matrix to {output_path}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} records to {output_path}.")

def main():
    logger.info("Starting ML Data Pipeline...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # 1. Extract
        raw_df = extract_data(engine)
        
        if raw_df.empty:
            logger.warning("No data extracted. Pipeline terminating.")
            return

        # 2. Clean
        clean_df = clean_data(raw_df)
        
        if clean_df.empty:
            logger.warning("Dataframe empty after cleaning. Pipeline terminating.")
            return
            
        # 3. Engineer
        feature_df = engineer_features(clean_df)
        
        # 4. Load/Save
        save_features(feature_df, OUTPUT_PATH)
        
        logger.info("ML Data Pipeline completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
