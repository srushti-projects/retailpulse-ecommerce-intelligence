-- ====================================================================
-- RetailPulse Analytics Engine: Payment Gateway Risk & Failure Diagnostics
-- File: sql/05_payment_risk_analysis.sql
-- Concepts: Multi-table JOINs, Conditional Aggregations (CASE WHEN), Risk Rate
-- ====================================================================

WITH payment_order_rollup AS (
    SELECT 
        p.payment_type,
        o.order_id,
        o.order_status,
        o.total_order_value_usd
    FROM fact_order_payments p
    INNER JOIN fact_orders o ON p.order_id = o.order_id
)

SELECT 
    payment_type,
    COUNT(DISTINCT order_id) AS total_orders_attempted,
    ROUND(SUM(total_order_value_usd), 2) AS total_attempted_gmv_usd,
    -- Completed Orders
    COUNT(DISTINCT CASE WHEN order_status = 'delivered' THEN order_id END) AS completed_orders,
    -- Cancelled / Failed Orders
    COUNT(DISTINCT CASE WHEN order_status = 'cancelled' THEN order_id END) AS cancelled_orders,
    -- Cancellation Failure Rate %
    ROUND(
        COUNT(DISTINCT CASE WHEN order_status = 'cancelled' THEN order_id END) * 100.0 / COUNT(DISTINCT order_id),
        2
    ) AS "cancellation_rate_%",
    -- Lost GMV due to cancellation
    ROUND(SUM(CASE WHEN order_status = 'cancelled' THEN total_order_value_usd ELSE 0 END), 2) AS lost_gmv_usd
FROM payment_order_rollup
GROUP BY payment_type
ORDER BY "cancellation_rate_%" DESC;

