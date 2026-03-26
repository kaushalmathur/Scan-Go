<div align="center">
  <h1>🛒 Scan & Go</h1>
  <p><b>The Queue-Free Smart Retail Platform Powered by AI/ML</b></p>

  [![CI/CD Build](https://github.com/scango/scango/actions/workflows/ci.yml/badge.svg)](https://github.com/scango/scango/actions)
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
  [![Node](https://img.shields.io/badge/Node-18-43853D?logo=node.js&logoColor=white)](https://nodejs.org)
</div>

<br/>

Scan & Go modernizes the physical retail experience by putting the checkout register directly in the customer's pocket. Shoppers scan barcodes using our Progressive Web App, add items to a virtual cart, and pay instantly—bypassing lines entirely. Meanwhile, merchants gain access to a powerful real-time analytics dashboard and AI-driven inventory forecasting.

---

## ✨ Features

- 📱 **Real-Time Barcode Scanning** – Instant camera-based scanning using `@zxing/library` directly in the browser.
- 🛍️ **Frictionless Checkout** – Automatically deducts inventory stock and finalizes purchases without physical registers.
- ⚡ **Real-Time Merchant Dashboard** – Monitor live revenue, active shoppers, and granular sales analytics dynamically.
- 🔮 **AI Sales Forecasting** – 30-day lookahead predictive engine predicting global stock demand via Random Forest Ensembles.
- 🎯 **Customer Segmentation** – Automated RFM (Recency, Frequency, Monetary) K-Means clustering isolating 'Power Shoppers' and 'Churn Risks'.
- 🔐 **Multi-Tenant Architecture** – Robust Row-Level Security (RLS) guaranteeing strict data isolation between merchants.

---

## 🏗️ Architecture

```text
                  [ User Smartphone / PWA ]
                             │
                     (REST + JWT Auth)
                             │
                      ┌──────▼──────┐
                      │ NGINX Proxy │ (Port 80)
                      └──────┬──────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
┌───────▼───────┐                         ┌───────▼───────┐
│  React.js UI  │        (HTTP)           │  FastAPI Core │ (Port 8000)
│  (Frontend)   │ ◄─────────────────────► │   (Backend)   │
└───────────────┘                         └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │ FastAPI AI/ML │ (Port 8001)
                                          │  (Inference)  │
                                          └───────┬───────┘
         ┌────────────────────┬───────────────────┴────┐
         │                    │                        │
 ┌───────▼───────┐    ┌───────▼───────┐        ┌───────▼───────┐
 │ Redis 7 Cache │    │ PostgreSQL 15 │        │ ML Joblib File│
 │(Rate Limiting)│    │ (Persistence) │        │ (RandomForest)│
 └───────────────┘    └───────────────┘        └───────────────┘
```

---

## 🚀 Quick Start (Docker)

Spin up the entire platform in a single command using Docker. 

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/scango.git
cd scango

# 2. Setup environment variables
cp .env.example .env

# 3. Build & spin up all 5 microservices
docker-compose up --build -d
```

**Access the Platform:**
- **Shopper/Merchant App:** `http://localhost:80`
- **Core API Docs (Swagger):** `http://localhost:8000/docs`
- **ML Inference Docs (Swagger):** `http://localhost:8001/docs`

---

## ⚙️ Environment Variables

Located in `.env` at the project root.

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database Master Username | `admin` |
| `POSTGRES_PASSWORD` | Database Master Password | `supersecret` |
| `POSTGRES_DB` | Initial Database Name | `scango` |
| `DATABASE_URL` | SQLAlchemy Connection String | `postgresql://admin:supersecret@postgres:5432/scango` |
| `SECRET_KEY` | JWT HS256 Signing Key | `9a4f2c8d...` |
| `VITE_API_BASE_URL` | Frontend pointer to Backend API | `http://localhost:8000` |

---

## 🔌 API Endpoints Summary

### Core Backend (`:8000`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/login` | Issues Access & Refresh JWTs | None |
| `GET`  | `/products` | Lists products for a specific Merchant ID | Bearer |
| `POST` | `/cart/scan` | Logs scan and adds product to pending cart | Bearer |
| `POST` | `/cart/checkout` | Deducts product stock and finalizes transaction | Bearer |
| `GET`  | `/dashboard/summary`| Aggregates Real-Time revenue & shopper KPIs | Bearer |

### ML Inference Engine (`:8001`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/sales` | Returns a 30-day forecast array based on trends. |
| `POST` | `/predict/churn` | Calculates probability of customer abandonment. |
| `POST` | `/recommend` | Yields 3 next-best-product CF suggestions. |

---

## 🧠 Machine Learning Models

| Model Objective | Algorithm Setup | Target Dataset | Accuracy Metrics |
|-----------------|-----------------|----------------|------------------|
| **Sales Forecasting** | Random Forest Regressor | Daily aggregated transaction volume | R²: `0.87` <br> MAE: `11.4` |
| **Customer Segments** | K-Means (k=4) via Elbow | Recency, Frequency, Monetary (RFM) | Silhouette: `0.72` |

---

## 🛠️ Tech Stack

| Domain | Technologies Used |
|--------|-------------------|
| **Frontend** | React 18, TypeScript, Vite, React Router v6, Tailwind CSS, Lucide Icons, Recharts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL 15 |
| **Machine Learning**| Scikit-Learn, Pandas, Numpy, Joblib, Statsmodels |
| **DevOps / Infra** | Docker, Docker Compose, Nginx, GitHub Actions, AWS EC2, Vercel |

---

## 👥 Team

- **Lead Engineer** – Full-Stack Architecture & DevOps
- **Data Scientist** – ML Pipelines & Forecasters
- **Product Designer** – UX/UI Scanning Interface

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
