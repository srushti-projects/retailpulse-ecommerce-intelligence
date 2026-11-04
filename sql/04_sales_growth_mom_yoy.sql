-- ====================================================================
-- RetailPulse Analytics Engine: Sales Momentum, MoM Growth & Running Total
-- File: sql/04_sales_growth_mom_yoy.sql
-- Concepts: Date Aggregations, Window Functions (LAG, SUM OVER)
-- ====================================================================

WITH monthly_sales_summary AS (
    -- Step 1: Aggregate revenue, orders, and AOV by calendar month
    SELECT 
        strftime('%Y-%m', order_purchase_timestamp) AS sales_month,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_buyers,
        ROUND(SUM(total_order_value_usd), 2) AS monthly_gmv_usd,
        ROUND(AVG(total_order_value_usd), 2) AS avg_order_value_usd
    FROM fact_orders
    WHERE order_status NOT IN ('cancelled')
    GROUP BY strftime('%Y-%m', order_purchase_timestamp)
),

monthly_momentum AS (
    -- Step 2: Use LAG() to fetch previous month's GMV and calculate MoM % change
    SELECT 
        sales_month,
        total_orders,
        active_buyers,
        monthly_gmv_usd,
        avg_order_value_usd,
        -- Window function: Look back 1 month
        LAG(monthly_gmv_usd, 1) OVER (ORDER BY sales_month ASC) AS prev_month_gmv_usd,
        -- Window function: Cumulative Running Total GMV from day 1
        ROUND(SUM(monthly_gmv_usd) OVER (ORDER BY sales_month ASC), 2) AS cumulative_running_gmv_usd
    FROM monthly_sales_summary
)

-- Step 3: Executive Sales Momentum Report
SELECT 
    sales_month,
    total_orders,
    monthly_gmv_usd,
    avg_order_value_usd,
    prev_month_gmv_usd,
    -- MoM Growth % calculation with NULL handling for month 1
    CASE 
        WHEN prev_month_gmv_usd IS NULL THEN 0.0
        ELSE ROUND(((monthly_gmv_usd - prev_month_gmv_usd) * 100.0 / prev_month_gmv_usd), 2)
    END AS "mom_growth_%",
    cumulative_running_gmv_usd
FROM monthly_momentum
ORDER BY sales_month ASC;

