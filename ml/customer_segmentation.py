import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# 1. Configuration & Logging Setup
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="../backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/scango")

OUTPUT_CSV = "output/segments.csv"

def extract_transaction_data(engine):
    """Pulls successful transactions per user from PostgreSQL."""
    logger.info("Extracting user transaction data...")
    
    query = """
    SELECT 
        user_id,
        created_at AS transaction_date,
        amount AS monetary_value
    FROM transactions
    WHERE status = 'completed' AND user_id IS NOT NULL
    """
    
    df = pd.read_sql(query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.tz_localize(None)
    
    logger.info(f"Loaded {len(df)} transactions.")
    return df

def build_rfm_table(df):
    """Constructs the Recency, Frequency, Monetary table."""
    logger.info("Building RFM table...")
    
    # Define a snapshot date normally 1 day after the max date in dataset
    snapshot_date = df['transaction_date'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('user_id').agg({
        'transaction_date': lambda x: (snapshot_date - x.max()).days, # Recency
        'user_id': 'count',                                          # Frequency
        'monetary_value': 'sum'                                      # Monetary
    }).rename(columns={
        'transaction_date': 'Recency',
        'user_id': 'Frequency',
        'monetary_value': 'Monetary'
    }).reset_index()
    
    logger.info(f"Built RFM profile for {len(rfm)} unique users.")
    return rfm

def test_elbow_method(X_scaled):
    """Tests k=2 to 8 to find the elbow point (WSS/Inertia)."""
    logger.info("Testing KMeans from k=2 to k=8 to validate the Elbow Method...")
    inertias = []
    
    for k in range(2, 9):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(X_scaled)
        inertias.append((k, kmeans.inertia_))
        
    for k, wss in inertias:
        logger.info(f"k={k}: Inertia = {wss:.2f}")

def apply_kmeans(rfm):
    """Scales data, applies KMeans with k=4, and assigns labels."""
    logger.info("Scaling features with StandardScaler...")
    scaler = StandardScaler()
    
    # We use log transform before scaling to handle right-skewed Monetary and Frequency data typical in retail
    # Adding a small constant to prevent log(0)
    rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].copy()
    for col in rfm_log.columns:
        rfm_log[col] = np.log1p(rfm_log[col])
        
    X_scaled = scaler.fit_transform(rfm_log)
    
    test_elbow_method(X_scaled)
    
    logger.info("Applying K-Means clustering with k=4...")
    # Based on the prompt requirement: k=4
    kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
    rfm['Cluster'] = kmeans.fit_predict(X_scaled)
    
    return rfm

def label_clusters(rfm):
    """Assigns business logic labels to the 4 clusters."""
    logger.info("Assigning descriptive labels to clusters...")
    
    # Calculate median RFM values for each cluster to understand them
    cluster_means = rfm.groupby('Cluster').agg({
        'Recency': 'median',
        'Frequency': 'median',
        'Monetary': 'median'
    }).reset_index()
    
    # Simple heuristic to identify segments based on relative values.
    # High Monetary & High Freq = Power Shoppers
    # Med Monetary & Med Freq = Regular Users
    # Low Freq & High Recency = Occasional Buyers
    # Low Recency (Recent) & Low Freq = New Joiners
    
    # We will score them based on R (inverted, low is better), F, M
    cluster_means['R_Score'] = cluster_means['Recency'].rank(ascending=False)
    cluster_means['F_Score'] = cluster_means['Frequency'].rank(ascending=True)
    cluster_means['M_Score'] = cluster_means['Monetary'].rank(ascending=True)
    cluster_means['Total_Score'] = cluster_means['R_Score'] + cluster_means['F_Score'] + cluster_means['M_Score']
    
    # Sort clusters by Total Score to map them dynamically
    cluster_means = cluster_means.sort_values('Total_Score', ascending=False)
    ordered_clusters = cluster_means['Cluster'].tolist()
    
    # Map the ordered clusters to the 4 labels (from best to worst assuming 4 distinct groups)
    label_map = {
        ordered_clusters[0]: 'Power Shoppers',
        ordered_clusters[1]: 'Regular Users',
        ordered_clusters[2]: 'New Joiners', # New joiners usually have good recency but low freq
        ordered_clusters[3]: 'Occasional Buyers' # Bad recency, bad freq
    }
    
    rfm['Segment'] = rfm['Cluster'].map(label_map)
    rfm.drop('Cluster', axis=1, inplace=True)
    
    return rfm

def save_to_database(rfm, engine):
    """Saves the user_segments back to PostgreSQL."""
    logger.info("Saving segment assignments to user_segments table in PostgreSQL...")
    
    output_df = rfm[['user_id', 'Segment', 'Recency', 'Frequency', 'Monetary']].copy()
    output_df['updated_at'] = datetime.now()
    
    output_df.to_sql(
        name='user_segments',
        con=engine,
        if_exists='replace', # Replace existing segments table if pipeline runs again
        index=False
    )
    logger.info("Successfully written to database.")

def output_summary(rfm):
    """Outputs a summary CSV with cluster stats."""
    logger.info(f"Generating summary statistics to {OUTPUT_CSV}...")
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    summary = rfm.groupby('Segment').agg({
        'user_id': 'count',
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': ['mean', 'sum']
    }).round(2)
    
    summary.columns = ['User_Count', 'Avg_Recency_Days', 'Avg_Frequency', 'Avg_Monetary', 'Total_Monetary']
    summary.reset_index(inplace=True)
    
    summary.to_csv(OUTPUT_CSV, index=False)
    logger.info("Summary saved successfully.")
    
    print("\n" + "="*70)
    print("CUSTOMER SEGMENTATION SUMMARY")
    print("="*70)
    print(summary.to_string(index=False))
    print("="*70 + "\n")

def main():
    logger.info("Starting Customer Segmentation Pipeline...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # 1. Extract
        try:
            df = extract_transaction_data(engine)
        except Exception as e:
            # For testing without a populated DB, create mock data
            logger.warning(f"Could not extract from DB: {e}. Generating mock data for demonstration.")
            df = pd.DataFrame({
                'user_id': np.random.randint(1, 100, size=500),
                'transaction_date': [datetime.now() - pd.Timedelta(days=np.random.randint(0, 100)) for _ in range(500)],
                'monetary_value': np.random.uniform(10, 500, size=500)
            })

        if df.empty:
            logger.warning("No completed transactions found.")
            return

        # 2. Build RFM
        rfm = build_rfm_table(df)
        
        if len(rfm) < 4:
            logger.error("Not enough unique users to perform k=4 clustering. Need at least 4.")
            return

        # 3. Scale, Test Elbow, and Apply K-Means
        rfm = apply_kmeans(rfm)
        
        # 4. Label Clusters
        rfm = label_clusters(rfm)
        
        # 5. Output Summary CSV
        output_summary(rfm)
        
        # 6. Save back to DB
        try:
            save_to_database(rfm, engine)
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")

        logger.info("Customer Segmentation completed.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
