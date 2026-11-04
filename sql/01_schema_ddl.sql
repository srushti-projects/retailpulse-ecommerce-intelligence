-- ====================================================================
-- RetailPulse Data Warehouse Schema (Star Schema DDL)
-- Target: PostgreSQL / Enterprise Data Warehouse
-- Architecture: Kimball Dimensional Model (Fact-Grain Standard)
-- ====================================================================

-- 1. Dimension: Customers (Who)
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_customers_unique ON dim_customers(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_customers_city ON dim_customers(customer_city);

-- 2. Dimension: Products (What)
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g NUMERIC(10, 2),
    product_length_cm NUMERIC(10, 2),
    product_height_cm NUMERIC(10, 2),
    product_width_cm NUMERIC(10, 2)
);

CREATE INDEX IF NOT EXISTS idx_products_category ON dim_products(product_category_name);

-- 3. Dimension: Date (When)
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- 4. Fact: Orders (Grain: 1 row per order)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    order_status VARCHAR(30) NOT NULL,
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    currency VARCHAR(10) DEFAULT 'BRL',
    fx_rate_to_usd NUMERIC(10, 4) DEFAULT 1.0,
    total_order_value_usd NUMERIC(12, 2)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON fact_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON fact_orders(order_purchase_timestamp);

-- 5. Fact: Order Items (Grain: 1 row per item in an order)
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) REFERENCES dim_products(product_id),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(10, 2) NOT NULL,
    freight_value NUMERIC(10, 2) NOT NULL,
    price_usd NUMERIC(10, 2),
    freight_usd NUMERIC(10, 2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE INDEX IF NOT EXISTS idx_order_items_product ON fact_order_items(product_id);

-- 6. Fact: Order Payments
CREATE TABLE IF NOT EXISTS fact_order_payments (
    order_id VARCHAR(50) REFERENCES fact_orders(order_id),
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE INDEX IF NOT EXISTS idx_payments_type ON fact_order_payments(payment_type);

