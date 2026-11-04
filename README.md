# RetailPulse — Real-Time E-Commerce Intelligence Platform
> An enterprise-grade e-commerce analytics and live streaming intelligence system modeled after data platforms at Amazon, Flipkart, and Walmart.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-green.svg)](https://www.postgresql.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-DAX_Intelligence-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📌 Project Overview
**RetailPulse** is an end-to-end e-commerce intelligence platform that monitors and analyzes commercial performance, customer behavioral segmentation, product velocity, and payment risk.

Unlike standard static sales dashboards, **RetailPulse integrates a hybrid event-driven architecture**:
1. **Historical Foundation:** A 25,000-order Kimball Star Schema database modeling real retail customer purchasing patterns.
2. **Real-Time Order Streaming Engine:** A Python producer simulating live customer checkouts with on-the-fly currency conversion using the public Frankfurter Foreign Exchange (FX) API.
3. **Advanced SQL Diagnostic Engine:** Production SQL queries utilizing Window Functions (`NTILE`, `LAG`, `SUM OVER`) and multi-level CTEs for RFM segmentation, cohort retention heatmaps, and payment gateway risk analysis.
4. **Interactive Power BI Executive Suite:** A 3-page interactive dashboard with custom DAX measures for executive sales, customer retention, and operations.

---

## 🏗️ Architecture & Data Pipeline

```
┌────────────────────────────────┐       ┌────────────────────────────────┐
│   Historical Base Data         │       │  Live Macro API (FX)           │
│   (25k Orders - Star Schema)   │       │  - Frankfurter API (Live rates)│
└───────────────┬────────────────┘       └───────────────┬────────────────┘
                │                                        │
                ▼                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Python Ingestion & Stream Engine                     │
│  - Event Generator emits simulated live checkouts every N seconds     │
│  - Fetches latest currency rates & calculates normalized GMV in USD    │
│  - Validates and buffers payloads before database load                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        SQL Data Warehouse                              │
│  - Star Schema (Fact_Orders, Fact_Order_Items, Dim_Customers, etc.)    │
│  - Advanced SQL Views: RFM Segmentation, Cohort Retention, MoM Trends  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Power BI Executive Suite                        │
│  - Page 1: Executive Overview (GMV, Net Revenue, Orders, AOV, MoM %)   │
│  - Page 2: Customer & RFM Intelligence (Champions, At-Risk VIPs)       │
│  - Page 3: Product & Payment Operations (Pareto 80/20, Gateway Risk)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
├── data/
│   ├── retailpulse.db              # High-performance SQL database (25k+ orders)
│   ├── dim_customers.csv           # Customer dimension (5,000 customers)
│   ├── dim_products.csv            # Product dimension (248 products, 7 categories)
│   ├── dim_date.csv                # Date calendar dimension (2023 - 2024)
│   ├── fact_orders.csv             # Order-level transactional facts
│   ├── fact_order_items.csv        # Item-level line item facts
│   └── fact_order_payments.csv     # Payment method & installments facts
├── pipeline/
│   ├── live_fx_service.py          # Real-time Frankfurter FX API integration
│   ├── load_base_data.py           # Enterprise Star Schema loader & generator
│   └── stream_producer.py          # Real-time live order streaming engine
├── sql/
│   ├── 01_schema_ddl.sql           # Kimball Star Schema DDL with B-Tree indexes
│   ├── 02_rfm_analysis.sql         # RFM Customer Segmentation via NTILE(4)
│   ├── 03_cohort_retention.sql     # Customer Cohort Retention Matrix (Months 0-6)
│   ├── 04_sales_growth_mom_yoy.sql # Sales momentum, MoM Growth % & Running Total
│   └── 05_payment_risk_analysis.sql# Payment Gateway failure diagnostics
├── powerbi/
│   ├── DAX_MEASURES.md             # 15+ Production DAX Measures cheat-sheet
│   └── DASHBOARD_DESIGN_GUIDE.md   # Step-by-step 3-page Power BI layout guide
└── RETAILPULSE_INTERVIEW_PLAYBOOK.md # Comprehensive study guide & interview Q&A bank
```

---

## ⚡ Quickstart & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/RetailPulse.git
cd RetailPulse
```

### 2. Install dependencies
```bash
pip install pandas numpy requests
```

### 3. Initialize the database
```bash
python pipeline/load_base_data.py
```

### 4. Run the Real-Time Order Streamer
```bash
# Stream 10 live orders into the database
python pipeline/stream_producer.py 10
```

---

## 📊 Analytical Highlights & Key Findings

### 1. RFM Customer Segmentation
Using `NTILE(4)` window functions across Recency, Frequency, and Monetary spend:
* **Champions (31.9% of base):** 1,435 customers driving **$13.31M in GMV** (avg spend: $9,273, avg orders: 11.6).
* **Can't Lose Them / At Risk (9.8% of base):** 442 high-value customers holding **$1.95M in past spend** who have been inactive for over 230 days (prime targets for win-back campaigns).
* **Lost / Churned (13.4% of base):** 602 one-time buyers inactive for >480 days (excluded from paid ad retargeting).

### 2. Payment Gateway Risk Diagnostics
* **Baseline Payment Cancellation:** Credit Card (**3.87%**) and UPI (**3.89%**).
* **The Anomaly:** Debit Card orders suffered from a **20.41% cancellation rate**, leaking over **$411,280 USD in lost GMV** due to 3DS authentication timeouts.

### 3. Customer Cohort Retention (The Leaky Bucket)
Tracking retention decay across 2023 cohorts revealed that 30-day retention slipped from **30.0% in January** down to **11.3% by June**, prompting category management to overhaul post-purchase onboarding sequences.

---

## 🎯 Resume Impact Bullets
* **RetailPulse — Real-Time E-Commerce Intelligence Platform** *(Python, SQL, PostgreSQL, Power BI, DAX)*
  * Architected a hybrid e-commerce data warehouse across 25,000+ orders using Kimball Star Schema design in SQL.
  * Built a Python streaming pipeline integrating Frankfurter FX API to simulate live checkout events and multi-currency GMV normalization.
  * Developed advanced SQL analytical scripts (`NTILE`, `LAG`, CTEs) to implement RFM segmentation, cohort retention heatmaps, and payment gateway anomaly detection.
  * Designed an interactive 3-page Power BI executive suite with 15+ DAX measures (AOV, MoM Growth %, Running Total YTD, Cancellation Rate).

---

## 📄 License
This project is open-source under the MIT License.
