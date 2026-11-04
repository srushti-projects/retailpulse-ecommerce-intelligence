-- ====================================================================
-- RetailPulse Analytics Engine: Customer RFM Segmentation
-- File: sql/02_rfm_analysis.sql
-- Concepts: CTEs (WITH clause), Aggregations, Window Functions (NTILE), CASE
-- ====================================================================

WITH raw_customer_rfm AS (
    -- Step 1: Calculate raw Recency, Frequency, and Monetary metrics per customer
    SELECT 
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        -- Reference baseline date: latest date in dataset (2024-10-31)
        CAST(
            JULIANDAY('2024-10-31 23:59:59') - JULIANDAY(MAX(o.order_purchase_timestamp)) 
            AS INT
        ) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(o.total_order_value_usd), 2) AS monetary_spend_usd
    FROM dim_customers c
    INNER JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status NOT IN ('cancelled')
    GROUP BY c.customer_id, c.customer_unique_id, c.customer_city, c.customer_state
),

rfm_quartiles AS (
    -- Step 2: Assign scores 1 to 4 using NTILE(4)
    -- Crucial Rule: NTILE assigns bucket 1 to the first group in sort order.
    -- For Recency: DESC puts largest days (inactive) in bucket 1, and smallest days (recent) in bucket 4.
    -- For Frequency & Monetary: ASC puts lowest orders/spend in bucket 1, highest in bucket 4.
    SELECT 
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state,
        recency_days,
        frequency,
        monetary_spend_usd,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_spend_usd ASC) AS m_score
    FROM raw_customer_rfm
),

rfm_segmented AS (
    -- Step 3: Assign business personas based on RFM score combinations
    SELECT 
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state,
        recency_days,
        frequency,
        monetary_spend_usd,
        r_score,
        f_score,
        m_score,
        (CAST(r_score AS TEXT) || CAST(f_score AS TEXT) || CAST(m_score AS TEXT)) AS rfm_combined_code,
        CASE 
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'Can''t Lose Them (At Risk)'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'New / Promising'
            WHEN r_score = 1 AND f_score = 1 THEN 'Lost / Churned'
            ELSE 'Potential Loyalists'
        END AS customer_segment
    FROM rfm_quartiles
)

-- Step 4: Executive Segment Summary Report
SELECT 
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rfm_segmented), 1) AS pct_of_customer_base,
    ROUND(AVG(recency_days), 0) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_orders,
    ROUND(AVG(monetary_spend_usd), 2) AS avg_spend_usd,
    ROUND(SUM(monetary_spend_usd), 2) AS total_segment_revenue_usd
FROM rfm_segmented
GROUP BY customer_segment
ORDER BY total_segment_revenue_usd DESC;
