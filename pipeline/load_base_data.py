"""
RetailPulse - Enterprise Base Data Generator & Loader
Populates the Star Schema database with realistic, high-fidelity historical e-commerce data (2023 - 2024).
Embeds real-world retail distributions:
- Pareto 80/20 product revenue rule
- Realistic RFM customer cohorts (Champions, At-Risk, Churned)
- Seasonality spikes (Q4 Holiday / Festive surges)
- Payment method distribution and realistic failure/cancellation anomalies
"""

import os
import random
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from live_fx_service import LiveFXService

# Set reproducible random seed
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "retailpulse.db")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_customers(n=5000):
    """Generates customer dimension with realistic demographic spread."""
    cities = [
        ("Mumbai", "MH"), ("Bengaluru", "KA"), ("Delhi", "DL"), ("Hyderabad", "TS"),
        ("Pune", "MH"), ("Chennai", "TN"), ("Kolkata", "WB"), ("Ahmedabad", "GJ"),
        ("New York", "NY"), ("London", "UK"), ("Sao Paulo", "SP")
    ]
    city_weights = [0.22, 0.18, 0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02]
    
    customers = []
    for i in range(1, n + 1):
        cust_id = f"CUST-{i:05d}"
        unique_id = f"UID-{random.randint(1000, 9999)}-{i:04d}"
        chosen_city, chosen_state = random.choices(cities, weights=city_weights)[0]
        zip_code = f"{random.randint(100000, 999999)}"
        
        customers.append({
            "customer_id": cust_id,
            "customer_unique_id": unique_id,
            "customer_zip_code_prefix": zip_code,
            "customer_city": chosen_city,
            "customer_state": chosen_state
        })
    return pd.DataFrame(customers)

def generate_products(n=250):
    """Generates product dimension with category tiers and pricing distributions."""
    categories = [
        ("Electronics", 250.0, 1200.0, 0.25),
        ("Computers & Laptops", 400.0, 2000.0, 0.15),
        ("Fashion & Apparel", 20.0, 150.0, 0.20),
        ("Home & Kitchen", 30.0, 300.0, 0.15),
        ("Beauty & Personal Care", 15.0, 90.0, 0.10),
        ("Sports & Fitness", 25.0, 250.0, 0.08),
        ("Books & Stationery", 10.0, 50.0, 0.07)
    ]
    
    products = []
    prod_id = 1
    for cat_name, min_p, max_p, cat_weight in categories:
        cat_count = int(n * cat_weight)
        for _ in range(cat_count):
            price = round(random.uniform(min_p, max_p), 2)
            # Pareto weight: some products are runaway bestsellers (Pareto 80/20 rule)
            sales_velocity_weight = round(random.paretovariate(1.2), 2)
            
            products.append({
                "product_id": f"PROD-{prod_id:04d}",
                "product_category_name": cat_name,
                "base_price_usd": price,
                "product_weight_g": random.randint(200, 8000),
                "product_length_cm": random.randint(10, 80),
                "product_height_cm": random.randint(5, 50),
                "product_width_cm": random.randint(10, 60),
                "sales_velocity_weight": sales_velocity_weight
            })
            prod_id += 1
            
    return pd.DataFrame(products)

def generate_date_dimension(start_date="2023-01-01", end_date="2024-12-31"):
    """Generates comprehensive date dimension table."""
    dates = pd.date_range(start=start_date, end=end_date)
    date_records = []
    
    for d in dates:
        date_records.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "full_date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": (d.month - 1) // 3 + 1,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "day_of_month": d.day,
            "day_of_week": d.weekday() + 1,
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.weekday() >= 5 else 0
        })
    return pd.DataFrame(date_records)

def generate_orders_and_items(df_customers, df_products, n_orders=25000):
    """Generates transactional facts with realistic seasonal trends and basket sizes."""
    print(f"Generating {n_orders} transactional orders and items...")
    fx = LiveFXService()
    
    # Pareto sampling weights for products
    prod_weights = df_products["sales_velocity_weight"].values
    prod_weights = prod_weights / prod_weights.sum()
    
    # Realistic customer order frequency (heavy repeat vs one-timers)
    customer_pool = df_customers["customer_id"].tolist()
    # 20% of customers will be repeat champions placing 4-10 orders
    champions = customer_pool[:int(len(customer_pool) * 0.2)]
    casuals = customer_pool[int(len(customer_pool) * 0.2):]
    
    orders = []
    order_items = []
    order_payments = []
    
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2024, 10, 31)
    total_seconds = int((end_time - start_time).total_seconds())
    
    payment_types = ["credit_card", "upi", "debit_card", "voucher"]
    payment_weights = [0.55, 0.30, 0.10, 0.05]
    
    for i in range(1, n_orders + 1):
        order_id = f"ORD-{i:06d}"
        
        # Select customer (champions sampled 4x more frequently)
        if random.random() < 0.65:
            cust_id = random.choice(champions)
        else:
            cust_id = random.choice(casuals)
            
        # Timestamp with Q4 holiday season boost
        random_sec = random.randint(0, total_seconds)
        order_time = start_time + timedelta(seconds=random_sec)
        # Seasonal boost: multiply chances in Oct, Nov, Dec
        if order_time.month in [10, 11, 12] and random.random() < 0.35:
            # Shift towards festive season safely
            order_time = order_time.replace(month=11, day=min(order_time.day, 30))
            
        # Realistic order status: mostly delivered, some cancelled / returned
        status_roll = random.random()
        chosen_payment = random.choices(payment_types, weights=payment_weights)[0]
        
        # Payment anomaly simulation: Net banking / Debit card has higher cancellation
        if chosen_payment == "debit_card" and random.random() < 0.18:
            status = "cancelled"
        elif status_roll < 0.04:
            status = "cancelled"
        elif status_roll < 0.08:
            status = "returned"
        elif status_roll < 0.12:
            status = "shipped"
        else:
            status = "delivered"
            
        currency = random.choices(["USD", "INR", "EUR", "BRL"], weights=[0.60, 0.25, 0.10, 0.05])[0]
        fx_rate = fx.get_rate(currency)
        
        # Basket size: 1 to 4 items
        num_items = random.choices([1, 2, 3, 4], weights=[0.65, 0.22, 0.09, 0.04])[0]
        chosen_indices = np.random.choice(len(df_products), size=num_items, p=prod_weights)
        
        order_total_usd = 0.0
        
        for item_seq, prod_idx in enumerate(chosen_indices, 1):
            prod = df_products.iloc[prod_idx]
            price_usd = float(prod["base_price_usd"])
            freight_usd = round(random.uniform(3.0, 15.0), 2)
            
            # Local currency pricing
            price_local = round(price_usd * fx_rate, 2)
            freight_local = round(freight_usd * fx_rate, 2)
            
            order_total_usd += (price_usd + freight_usd)
            
            order_items.append({
                "order_id": order_id,
                "order_item_id": item_seq,
                "product_id": prod["product_id"],
                "seller_id": f"SELL-{random.randint(100, 400)}",
                "shipping_limit_date": (order_time + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
                "price": price_local,
                "freight_value": freight_local,
                "price_usd": price_usd,
                "freight_usd": freight_usd
            })
            
        # Delivery dates
        delivery_days = random.randint(2, 9)
        delivered_date = (order_time + timedelta(days=delivery_days)).strftime("%Y-%m-%d %H:%M:%S") if status == "delivered" else None
        estimated_date = (order_time + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "order_status": status,
            "order_purchase_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_approved_at": (order_time + timedelta(minutes=random.randint(5, 60))).strftime("%Y-%m-%d %H:%M:%S"),
            "order_delivered_carrier_date": (order_time + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") if status in ["delivered", "shipped"] else None,
            "order_delivered_customer_date": delivered_date,
            "order_estimated_delivery_date": estimated_date,
            "currency": currency,
            "fx_rate_to_usd": fx_rate,
            "total_order_value_usd": round(order_total_usd, 2)
        })
        
        order_payments.append({
            "order_id": order_id,
            "payment_sequential": 1,
            "payment_type": chosen_payment,
            "payment_installments": random.choice([1, 1, 1, 3, 6, 12]),
            "payment_value": round(order_total_usd * fx_rate, 2)
        })
        
    return pd.DataFrame(orders), pd.DataFrame(order_items), pd.DataFrame(order_payments)

def main():
    print("=" * 60)
    print("RetailPulse - Enterprise Database Initialization")
    print("=" * 60)
    
    # 1. Generate Dimensions
    print("Generating Customer Dimension...")
    df_customers = generate_customers(5000)
    
    print("Generating Product Dimension...")
    df_products = generate_products(250)
    
    print("Generating Date Dimension...")
    df_date = generate_date_dimension()
    
    # 2. Generate Fact Transactions
    df_orders, df_order_items, df_payments = generate_orders_and_items(df_customers, df_products, n_orders=25000)
    
    # Clean up product helper column before saving
    df_products_clean = df_products.drop(columns=["sales_velocity_weight"])
    
    # 3. Save to SQLite Database
    print(f"\nWriting Star Schema to SQLite: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    df_customers.to_sql("dim_customers", conn, if_exists="replace", index=False)
    df_products_clean.to_sql("dim_products", conn, if_exists="replace", index=False)
    df_date.to_sql("dim_date", conn, if_exists="replace", index=False)
    df_orders.to_sql("fact_orders", conn, if_exists="replace", index=False)
    df_order_items.to_sql("fact_order_items", conn, if_exists="replace", index=False)
    df_payments.to_sql("fact_order_payments", conn, if_exists="replace", index=False)
    
    # Create indexes for high-speed SQL analytics
    print("Creating performance indexes...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ord_cust ON fact_orders(customer_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ord_ts ON fact_orders(order_purchase_timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ord_status ON fact_orders(order_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_prod ON fact_order_items(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_ord ON fact_order_items(order_id);")
    conn.commit()
    conn.close()
    
    # 4. Save CSV exports for Power BI direct import
    print("Exporting Clean CSVs for Power BI in /data/ ...")
    df_customers.to_csv(os.path.join(DATA_DIR, "dim_customers.csv"), index=False)
    df_products_clean.to_csv(os.path.join(DATA_DIR, "dim_products.csv"), index=False)
    df_date.to_csv(os.path.join(DATA_DIR, "dim_date.csv"), index=False)
    df_orders.to_csv(os.path.join(DATA_DIR, "fact_orders.csv"), index=False)
    df_order_items.to_csv(os.path.join(DATA_DIR, "fact_order_items.csv"), index=False)
    df_payments.to_csv(os.path.join(DATA_DIR, "fact_order_payments.csv"), index=False)
    
    print("\nSUCCESS! Enterprise RetailPulse Database initialized successfully:")
    print(f"- Total Customers: {len(df_customers):,}")
    print(f"- Total Products:  {len(df_products):,}")
    print(f"- Total Orders:    {len(df_orders):,}")
    print(f"- Total Items:     {len(df_order_items):,}")
    print(f"- Total Payments:  {len(df_payments):,}")
    print("=" * 60)

if __name__ == "__main__":
    main()
