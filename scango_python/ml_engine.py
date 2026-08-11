import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class RetailMLEngine:
    """
    Industry-Standard Machine Learning Pipeline using Pandas, NumPy & Scikit-Learn.
    Handles Sales Demand Forecasting, Churn Risk Prediction, and Customer Segmentation.
    """

    def __init__(self):
        self.rf_forecaster = None
        self.churn_classifier = None
        self.kmeans_clusterer = None
        self.scaler = StandardScaler()
        self._train_models()

    def _train_models(self):
        """Train Random Forest Regressor & Logistic Regression on historical synthetic sales data."""
        # 1. Feature Engineering with Pandas & NumPy
        np.random.seed(42)
        n_days = 180
        dates = [datetime.now() - timedelta(days=i) for i in range(n_days)][::-1]

        # Features: DayOfWeek, IsWeekend, RollingAvgSales, PriceIndex
        day_of_week = np.array([d.weekday() for d in dates])
        is_weekend = np.array([1 if d >= 5 else 0 for d in day_of_week])
        
        # Synthetic sales pattern with weekly seasonality & trend
        base_sales = 120 + 40 * np.sin(np.linspace(0, 10, n_days)) + 30 * is_weekend
        noise = np.random.normal(0, 10, n_days)
        total_sales = np.maximum(50, base_sales + noise)

        df = pd.DataFrame({
            'date': dates,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'sales': total_sales
        })

        # Calculate 7-day rolling average using Pandas
        df['rolling_7d_avg'] = df['sales'].rolling(window=7, min_periods=1).mean()

        X = df[['day_of_week', 'is_weekend', 'rolling_7d_avg']].values
        y = df['sales'].values

        # Fit Random Forest Regressor
        self.rf_forecaster = RandomForestRegressor(n_estimators=100, random_state=42)
        self.rf_forecaster.fit(X, y)

        # 2. Churn Risk Logistic Regression (Customer Recency vs Churn Probability)
        # Synthetic Customer Features: [DaysSinceLastScan, TotalScans, TotalSpend]
        np_customers = np.array([
            [2, 15, 120.0],
            [45, 2, 12.5],
            [1, 22, 210.0],
            [30, 4, 35.0],
            [5, 18, 145.0],
            [60, 1, 8.0],
            [3, 30, 310.0],
            [25, 5, 42.0]
        ])
        y_churn = np.array([0, 1, 0, 1, 0, 1, 0, 1]) # 0 = Active, 1 = Churned

        self.churn_classifier = LogisticRegression()
        self.churn_classifier.fit(np_customers, y_churn)

        # 3. K-Means Customer Clustering (k=3)
        self.kmeans_clusterer = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.kmeans_clusterer.fit(np_customers)

    def forecast_next_ndays(self, n_days: int = 7) -> pd.DataFrame:
        """
        Generates N-day future sales demand predictions using Random Forest Regressor.
        Returns a Pandas DataFrame formatted for Plotly visualization.
        """
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, n_days + 1)]
        
        # Prepare future feature matrix using NumPy & Pandas
        future_day_of_week = np.array([d.weekday() for d in future_dates])
        future_is_weekend = np.array([1 if d >= 5 else 0 for d in future_day_of_week])
        rolling_avg = np.full(n_days, 165.0) # Estimated recent average

        X_future = np.column_stack([future_day_of_week, future_is_weekend, rolling_avg])
        predictions = self.rf_forecaster.predict(X_future)

        # Add stochastic noise using NumPy for realistic daily variance
        noise = np.random.normal(0, 5, n_days)
        final_forecast = np.round(np.maximum(100, predictions + noise), 2)

        return pd.DataFrame({
            'Date': [d.strftime('%b %d') for d in future_dates],
            'Predicted Sales ($)': final_forecast,
            'Lower Bound ($)': np.round(final_forecast * 0.9, 2),
            'Upper Bound ($)': np.round(final_forecast * 1.1, 2)
        })

    def predict_user_churn(self, days_since_last_scan: int, total_scans: int, total_spend: float) -> dict:
        """
        Calculates customer churn risk percentage using Logistic Regression.
        """
        features = np.array([[days_since_last_scan, total_scans, total_spend]])
        prob = float(self.churn_classifier.predict_proba(features)[0][1])
        
        return {
            "churn_probability": round(prob * 100, 1),
            "is_at_risk": prob > 0.5,
            "risk_level": "High Risk" if prob > 0.6 else ("Moderate Risk" if prob > 0.3 else "Low Risk")
        }

    def compute_category_statistics(self, transaction_items: list) -> pd.DataFrame:
        """
        Processes transaction logs using Pandas to yield category-wise revenue & item counts.
        """
        if not transaction_items:
            # Default dataset for demonstration
            data = {
                'Category': ['Beverages', 'Dairy & Milk', 'Snacks & Crisps', 'Confectionery', 'Pantry & Coffee'],
                'Revenue ($)': [4850.50, 3420.00, 2980.75, 1950.25, 2640.00],
                'Items Sold': [1200, 850, 1400, 600, 450]
            }
            return pd.DataFrame(data)

        df = pd.DataFrame(transaction_items)
        grouped = df.groupby('Category').agg({
            'Revenue ($)': 'sum',
            'Items Sold': 'sum'
        }).reset_index()
        return grouped

# Global Singleton Instance for fast reuse in Streamlit
ml_pipeline = RetailMLEngine()
