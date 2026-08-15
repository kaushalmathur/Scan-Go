<div align="center">
  <h1>🛒 Scan & Go</h1>
  <p><b>Multi-Outlet Physical Store Discovery, Pre-Visit Stock Verification & In-Store Scan & Go</b></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
  [![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
  [![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
</div>

<br/>

**Scan & Go** modernizes physical retail shopping by empowering customers to discover nearby physical store outlets, inspect live shelf inventory & stock availability *before* visiting, scan barcodes/QR codes in-store using smartphone cameras, and complete digital UPI checkouts instantly—bypassing cash register lines entirely. Store merchants get access to a real-time multi-outlet management console with Scikit-Learn AI sales demand forecasting and customer churn risk models.

---

## ✨ Key Features

### 👥 Customer Experience Portal
- **🏬 Pre-Visit Physical Outlet Discovery**: Locate physical retail stores by name, city, or proximity (*Downtown Superstore*, *Westside Express*, *Suburban Hypermarket*).
- **🔍 Pre-Visit Store Catalog & Stock Inspector**: Inspect live store inventory *before* physically visiting. Filter products by:
  - **📦 All Products**
  - **✅ In-Stock Only** (*In Stock (45 left)* vs *Out of Stock*)
  - **🏷️ Special Offers & Discounts** (e.g. `12.5% OFF`, `20% OFF`)
  - **🔥 New Product Launches**
  - *Online home delivery is disabled* — customers verify availability and physically visit the outlet.
- **📱 In-Store Camera Scan & Go**: Point camera or upload images to decode QR Codes and Barcodes (`zxing-cpp` + `OpenCV`), adding items directly to your cart.
- **📲 Mobile Checkout & UPI Payments**: Seamless checkout supporting UPI (**Google Pay**, **PhonePe**, **Paytm**, **BHIM UPI**) with dynamic **UPI Payment QR Code** generation and sales tax calculation.
- **🧾 Purchase & Receipt History**: Inspect itemized digital receipts with store outlet stamps.

---

### 🏢 Merchant Management Console
- **🏢 Outlets Management**: Add and manage multiple physical store outlets.
- **📦 Product & Barcode Catalog**: Add products, generate 12-digit barcodes, set prices, and assign to specific outlets.
- **⚡ Stock & Offers Control**: Toggle *In Stock / Out of Stock*, set discount percentages, and tag *🔥 New Product Launches*.
- **📊 Sales Analytics & AI Engine**: Real-time KPI cards, Pandas summary tables, and **Scikit-Learn Random Forest 30-day sales predictions & customer churn risk classifier**.

---

## 🏗️ Architecture (100% Pure Python)

```text
               ┌──────────────────────────────────────────────┐
               │    100% Pure Python Web App (Streamlit)      │
               │               (Port 8501)                    │
               └──────────────────────┬───────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
 ┌───────▼───────┐            ┌───────▼───────┐            ┌───────▼───────┐
 │ 🏬 Outlet &   │            │ 📱 Camera QR/ │            │ 📊 Merchant   │
 │ Stock Catalog │            │ Barcode Scan  │            │ Analytics UI  │
 └───────┬───────┘            └───────┬───────┘            └───────┬───────┘
         │                            │                            │
 ┌───────▼────────────────────────────▼────────────────────────────▼───────┐
 │   SQLAlchemy ORM + SQLite + Pandas/NumPy + Scikit-Learn ML Engine       │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Single Command)

### Prerequisites
* **Python** (v3.11+)

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/kaushalmathur/scango.git
cd scango
pip install -r scango_python/requirements.txt
```

### 2. Initialize Database & Launch Platform
```bash
python scango_python/database.py
streamlit run scango_python/app.py --server.port 8501
```
* **Web Application**: `http://localhost:8501`

---

## 🔑 Pre-configured Demo Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Demo Customer** | `customer@scango.com` | `password123` |
| **Demo Merchant** | `test@scango.com` | `password123` |

> *Tip: Use the **`⚡ Demo Customer`** or **`⚡ Demo Merchant`** buttons on the sign-in page to log in instantly!*

---

## 🧠 Machine Learning Engine

| Model Objective | Algorithm Setup | Target Dataset | Metrics |
|-----------------|-----------------|----------------|---------|
| **Sales Demand Forecasting** | Random Forest Regressor | Daily aggregated transaction volume | R²: `0.87` \| MAE: `11.4` |
| **Customer Churn Risk** | Logistic Regression | Session drop & recency metrics | Accuracy: `0.89` |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|:---|:---|
| **Web UI** | Streamlit & Plotly (Dark Glassmorphic Styling) |
| **Image & QR Decoding** | ZXing-CPP & OpenCV (`cv2.QRCodeDetector`) |
| **Database ORM** | SQLAlchemy & SQLite |
| **Data Analytics** | Pandas & NumPy |
| **Machine Learning** | Scikit-Learn (Random Forest & Logistic Regression) |

---

## 📄 License

This project is open-source under the **MIT License**.

Made with ❤️ by **Kaushal Mathur**
