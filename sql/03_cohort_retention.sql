-- ====================================================================
-- RetailPulse Analytics Engine: Customer Cohort Retention Analysis
-- File: sql/03_cohort_retention.sql
-- Concepts: Multi-table CTEs, Date Truncation, Month-Offset Math, Aggregations
-- ====================================================================

WITH customer_first_purchase AS (
    -- Step 1: Identify each customer's first purchase date (Cohort Birth Month)
    SELECT 
        customer_id,
        MIN(order_purchase_timestamp) AS first_order_timestamp,
        strftime('%Y-%m', MIN(order_purchase_timestamp)) AS cohort_month,
        CAST(strftime('%Y', MIN(order_purchase_timestamp)) AS INT) AS cohort_year,
        CAST(strftime('%m', MIN(order_purchase_timestamp)) AS INT) AS cohort_month_num
    FROM fact_orders
    WHERE order_status NOT IN ('cancelled')
    GROUP BY customer_id
),

customer_activities AS (
    -- Step 2: Map every subsequent order to its Cohort Index (Month 0, 1, 2, ...)
    SELECT 
        o.customer_id,
        fp.cohort_month,
        strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
        -- Calculate month difference
        (
            (CAST(strftime('%Y', o.order_purchase_timestamp) AS INT) - fp.cohort_year) * 12 +
            (CAST(strftime('%m', o.order_purchase_timestamp) AS INT) - fp.cohort_month_num)
        ) AS cohort_index
    FROM fact_orders o
    INNER JOIN customer_first_purchase fp ON o.customer_id = fp.customer_id
    WHERE o.order_status NOT IN ('cancelled')
),

cohort_sizes AS (
    -- Step 3: Count total unique customers who joined in each Cohort Month (Month 0 base)
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM customer_first_purchase
    GROUP BY cohort_month
),

cohort_activity_counts AS (
    -- Step 4: Count distinct active customers for each (cohort_month, cohort_index)
    SELECT 
        ca.cohort_month,
        ca.cohort_index,
        COUNT(DISTINCT ca.customer_id) AS active_customers
    FROM customer_activities ca
    GROUP BY ca.cohort_month, ca.cohort_index
)

-- Step 5: Pivot into the Executive Cohort Retention Matrix (Months 0 through 6)
SELECT 
    cac.cohort_month,
    cs.total_cohort_customers AS cohort_size,
    -- Retention percentages for Month 0 through Month 6
    ROUND(SUM(CASE WHEN cac.cohort_index = 0 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M0_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 1 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M1_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 2 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M2_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 3 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M3_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 4 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M4_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 5 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M5_%",
    ROUND(SUM(CASE WHEN cac.cohort_index = 6 THEN cac.active_customers ELSE 0 END) * 100.0 / cs.total_cohort_customers, 1) AS "M6_%"
FROM cohort_activity_counts cac
INNER JOIN cohort_sizes cs ON cac.cohort_month = cs.cohort_month
GROUP BY cac.cohort_month, cs.total_cohort_customers
ORDER BY cac.cohort_month ASC
LIMIT 12;

