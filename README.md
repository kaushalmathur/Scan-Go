<div align="center">
  <h1>🛒 Scan & Go</h1>
  <p><b>The Queue-Free Smart Retail Platform Powered by AI/ML</b></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
  [![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
  [![Node](https://img.shields.io/badge/Node-24-43853D?logo=node.js&logoColor=white)](https://nodejs.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
</div>

<br/>

**Scan & Go** modernizes physical retail shopping by putting the checkout cash register directly in the customer's pocket. Shoppers scan barcodes using their smartphone camera or pick from store inventory chips, manage a virtual cart, and checkout instantly—bypassing long cash register lines entirely. Store merchants get access to a real-time analytics dashboard with AI/ML sales demand forecasting and customer churn risk predictions.

---

## ✨ Key Features

- 📱 **Real-Time Barcode Scanning**: Instant browser camera scanning powered by `@zxing/library` + interactive manual barcode search & sample item chips.
- 🛒 **Smart Auto-Register Scanning**: Automatically creates store product entries for any unknown scanned barcode so scans never return 404 errors.
- 💳 **Frictionless Checkout & Digital Receipt**: Supports promo codes (`SCANGO10`, `SCANGO20`), tax calculation, payment selection, and itemized digital receipt generation.
- ⚡ **Real-Time Merchant Dashboard**: Monitor gross revenue, active in-store shoppers, scans per hour, and sales category breakdowns dynamically.
- 🔮 **AI Demand Forecasting**: 7-to-30 day predictive engine powered by Random Forest Ensembles (`Scikit-Learn`).
- 🎯 **Customer Churn Risk Model**: Machine Learning model estimating customer churn probabilities in real time.
- 📦 **Inventory & Barcode Console**: Live stock monitoring, category filtering, low-stock reorder warnings, and 12-digit barcode generation.

---

## 🏗️ Architecture

```text
                  [ User Smartphone / Browser ]
                             │
                     (REST + JWT Auth)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
┌───────▼───────┐                         ┌───────▼───────┐
│  React.js UI  │        (HTTP)           │  FastAPI Core │ (Port 8000)
│  (Port 5173)  │ ◄─────────────────────► │   (Backend)   │
└───────────────┘                         └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │ FastAPI AI/ML │ (Port 8001)
                                          │  (Inference)  │
                                          └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │  SQLite / DB  │
                                          │ (scango.db)   │
                                          └───────────────┘
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
* **Node.js** (v18+)
* **Python** (v3.11+)

### 1. Setup Environment
Clone the repository and create the `.env` configuration file:
```bash
git clone https://github.com/Harsh127-pixel/scango.git
cd scango
copy .env.example .env
```

### 2. Run Core Backend Server (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
* **API Documentation (Swagger)**: `http://localhost:8000/docs`

### 3. Run AI/ML Inference Engine (FastAPI)
```bash
cd ml
pip install -r requirements.txt
python -m uvicorn inference_api:app --reload --port 8001
```
* **ML API Documentation (Swagger)**: `http://localhost:8001/docs`

### 4. Run Frontend UI (React + Vite)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
* **Web App**: `http://localhost:5173`

---

## 🔑 Pre-configured Demo Login

| Role | Email | Password |
| :--- | :--- | :--- |
| **Demo User / Merchant** | `test@scango.com` | `password123` |

> *Tip: Click the **`⚡ Click to Auto-Fill Pre-configured Demo Credentials`** button on the sign-in page to log in instantly!*

---

## 🔌 API Endpoints Summary

### Core Backend (`:8000`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Issues Access & Refresh JWTs |
| `POST` | `/auth/register` | Creates a new user account |
| `GET`  | `/products` | Lists store products by Merchant ID |
| `POST` | `/products` | Creates a new product with barcode |
| `POST` | `/cart/scan` | Logs scan and adds item to cart |
| `GET`  | `/cart/{user_id}` | Retrieves current cart items & subtotal |
| `POST` | `/cart/checkout` | Deducts stock and completes order |
| `GET`  | `/dashboard/summary` | Yields revenue & active shopper KPIs |

### ML Inference Engine (`:8001`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/sales` | Predicts N-day future sales demand curve |
| `POST` | `/predict/churn` | Calculates customer churn probability |
| `POST` | `/recommend` | Yields cart cross-sell recommendations |

---

## 🧠 Machine Learning Setup

| Model Objective | Algorithm Setup | Target Dataset | Accuracy Metrics |
|-----------------|-----------------|----------------|------------------|
| **Sales Forecasting** | Random Forest Regressor | Daily aggregated transaction volume | R²: `0.87` \| MAE: `11.4` |
| **Customer Churn Risk** | Logistic Regression | Session drop & recency metrics | Precision: `0.89` |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, React Hot Toast |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Alembic, SQLite / PostgreSQL |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib, Statsmodels |

---

## 📄 License

This project is open-source under the **MIT License**.
