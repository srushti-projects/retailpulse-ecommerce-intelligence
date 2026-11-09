import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "retailpulse.db")
DATA_DIR = os.path.join(BASE_DIR, "data")

conn = sqlite3.connect(DB_PATH)

# 1. Export Payment Risk Analysis CSV
with open(os.path.join(BASE_DIR, "sql", "05_payment_risk_analysis.sql"), "r") as f:
    df_payment = pd.read_sql_query(f.read(), conn)
df_payment.to_csv(os.path.join(DATA_DIR, "payment_risk_analysis.csv"), index=False)
print("Exported data/payment_risk_analysis.csv:")
print(df_payment.to_string(index=False))

# 2. Export Pareto 80/20 Table
pareto_sql = """
WITH prod_sales AS (
    SELECT 
        p.product_id,
        p.product_category_name,
        ROUND(SUM(i.price_usd + i.freight_usd), 2) AS total_product_revenue_usd,
        COUNT(i.order_item_id) AS units_sold
    FROM fact_order_items i
    INNER JOIN dim_products p ON i.product_id = p.product_id
    GROUP BY p.product_id, p.product_category_name
),
ranked AS (
    SELECT 
        product_id,
        product_category_name,
        total_product_revenue_usd,
        units_sold,
        SUM(total_product_revenue_usd) OVER (ORDER BY total_product_revenue_usd DESC) AS cumulative_revenue_usd,
        (SELECT SUM(total_product_revenue_usd) FROM prod_sales) AS grand_total_usd
    FROM prod_sales
)
SELECT 
    product_id,
    product_category_name,
    total_product_revenue_usd,
    units_sold,
    cumulative_revenue_usd,
    ROUND((cumulative_revenue_usd * 100.0 / grand_total_usd), 1) AS cumulative_revenue_pct
FROM ranked
ORDER BY total_product_revenue_usd DESC;
"""
df_pareto = pd.read_sql_query(pareto_sql, conn)
df_pareto.to_csv(os.path.join(DATA_DIR, "product_pareto_analysis.csv"), index=False)
print(f"\nExported data/product_pareto_analysis.csv with {len(df_pareto)} products.")

conn.close()

