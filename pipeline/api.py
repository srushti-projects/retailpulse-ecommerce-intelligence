"""
RetailPulse - Enterprise Analytics REST API (FastAPI)
Exposes real-time business KPIs, RFM segments, and diagnostic anomaly alerts.
Allows downstream frontend apps or data consumers to query live e-commerce intelligence.
"""

import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "retailpulse.db")

app = FastAPI(
    title="RetailPulse Intelligence API",
    description="Real-Time E-Commerce & Retail Intelligence Service",
    version="1.0.0"
)

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def root():
    return {
        "platform": "RetailPulse Real-Time Intelligence",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/v1/kpis")
def get_executive_kpis():
    """Returns top executive North Star metrics."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            ROUND(SUM(total_order_value_usd), 2) AS total_gmv_usd,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(AVG(total_order_value_usd), 2) AS aov_usd,
            ROUND(COUNT(DISTINCT CASE WHEN order_status = 'delivered' THEN order_id END) * 100.0 / COUNT(DISTINCT order_id), 1) AS delivery_sla_pct
        FROM fact_orders;
    """)
    row = dict(c.fetchone())
    conn.close()
    return row

@app.get("/api/v1/rfm-segments")
def get_rfm_segments():
    """Returns customer distribution across RFM behavioral tiers."""
    conn = get_db_connection()
    c = conn.cursor()
    rfm_query = """
    WITH raw AS (
        SELECT customer_id,
               CAST(JULIANDAY('2024-10-31 23:59:59') - JULIANDAY(MAX(order_purchase_timestamp)) AS INT) AS recency_days,
               COUNT(DISTINCT order_id) AS frequency,
               ROUND(SUM(total_order_value_usd), 2) AS monetary_spend_usd
        FROM fact_orders
        WHERE order_status NOT IN ('cancelled')
        GROUP BY customer_id
    ),
    scored AS (
        SELECT *,
               NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
               NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
               NTILE(4) OVER (ORDER BY monetary_spend_usd ASC) AS m_score
        FROM raw
    ),
    segmented AS (
        SELECT *,
            CASE 
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
                WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'Can''t Lose Them (At Risk)'
                WHEN r_score >= 3 AND f_score <= 2 THEN 'New / Promising'
                WHEN r_score = 1 AND f_score = 1 THEN 'Lost / Churned'
                ELSE 'Potential Loyalists'
            END AS customer_segment
        FROM scored
    )
    SELECT customer_segment, COUNT(*) AS customer_count, ROUND(SUM(monetary_spend_usd), 2) AS total_revenue_usd
    FROM segmented GROUP BY customer_segment ORDER BY total_revenue_usd DESC;
    """
    c.execute(rfm_query)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"segments": rows}

@app.get("/api/v1/anomalies/payment-risk")
def get_payment_anomalies():
    """Diagnostic audit endpoint that flags payment method failure anomalies."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT 
            p.payment_type,
            COUNT(DISTINCT p.order_id) AS total_orders,
            ROUND(COUNT(DISTINCT CASE WHEN o.order_status = 'cancelled' THEN o.order_id END) * 100.0 / COUNT(DISTINCT p.order_id), 2) AS cancellation_rate_pct,
            ROUND(SUM(CASE WHEN o.order_status = 'cancelled' THEN o.total_order_value_usd ELSE 0 END), 2) AS lost_gmv_usd
        FROM fact_order_payments p
        INNER JOIN fact_orders o ON p.order_id = o.order_id
        GROUP BY p.payment_type
        ORDER BY cancellation_rate_pct DESC;
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    
    # Flag critical risk
    alerts = []
    for r in rows:
        if r["cancellation_rate_pct"] > 10.0:
            alerts.append({
                "severity": "CRITICAL",
                "payment_type": r["payment_type"],
                "failure_rate": f"{r['cancellation_rate_pct']}%",
                "lost_revenue": f"${r['lost_gmv_usd']:,.2f}",
                "message": "Abnormal cancellation rate exceeding 10% platform threshold."
            })
            
    return {"payment_methods": rows, "active_alerts": alerts}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
