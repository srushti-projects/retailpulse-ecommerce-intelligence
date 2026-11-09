"""
RetailPulse - Real-Time Order Stream Producer
Simulates live customer checkouts streaming into the database every N seconds.
Integrates on-the-fly currency conversion using the LiveFXService.
Demonstrates enterprise streaming ingestion architecture.
"""

import os
import sys
import time
import random
import sqlite3
from datetime import datetime, timedelta
from live_fx_service import LiveFXService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "retailpulse.db")

class OrderStreamProducer:
    def __init__(self, interval_seconds=3):
        self.interval = interval_seconds
        self.fx = LiveFXService()
        self.fx.fetch_live_rates()
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        
        # Load active customer & product IDs from DB cache
        self.cursor.execute("SELECT customer_id, customer_city FROM dim_customers;")
        self.customers = self.cursor.fetchall()
        
        self.cursor.execute("SELECT product_id, product_category_name, base_price_usd FROM dim_products;")
        self.products = self.cursor.fetchall()
        
        # Get highest current order ID number
        self.cursor.execute("SELECT MAX(order_id) FROM fact_orders;")
        max_id = self.cursor.fetchone()[0]
        self.order_counter = int(max_id.split("-")[1]) if max_id and "-" in max_id else 30000
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Stream Producer initialized:")
        print(f" - Connected to database: {DB_PATH}")
        print(f" - Loaded {len(self.customers)} customers, {len(self.products)} products")
        print(f" - Starting order sequence from: ORD-{self.order_counter + 1:06d}")

    def generate_single_order(self):
        """Generates a realistic live order payload."""
        self.order_counter += 1
        order_id = f"ORD-{self.order_counter:06d}"
        
        cust_id, cust_city = random.choice(self.customers)
        currency = random.choices(["USD", "INR", "EUR", "BRL"], weights=[0.50, 0.35, 0.10, 0.05])[0]
        fx_rate = self.fx.get_rate(currency)
        
        # Random basket: 1 to 3 items
        num_items = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]
        items = random.sample(self.products, num_items)
        
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        total_usd = 0.0
        item_records = []
        
        for idx, (prod_id, cat_name, price_usd) in enumerate(items, 1):
            freight_usd = round(random.uniform(2.5, 8.0), 2)
            price_local = round(price_usd * fx_rate, 2)
            freight_local = round(freight_usd * fx_rate, 2)
            total_usd += (price_usd + freight_usd)
            
            item_records.append((
                order_id, idx, prod_id, f"SELL-{random.randint(100, 400)}",
                (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                price_local, freight_local, price_usd, freight_usd
            ))
            
        status = "processing"
        estimated_delivery = (now + timedelta(days=random.randint(3, 7))).strftime("%Y-%m-%d %H:%M:%S")
        
        order_record = (
            order_id, cust_id, status, timestamp_str, timestamp_str,
            None, None, estimated_delivery, currency, fx_rate, round(total_usd, 2)
        )
        
        # Insert into Database
        self.cursor.execute("""
            INSERT INTO fact_orders (
                order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at,
                order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date,
                currency, fx_rate_to_usd, total_order_value_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, order_record)
        
        self.cursor.executemany("""
            INSERT INTO fact_order_items (
                order_id, order_item_id, product_id, seller_id, shipping_limit_date,
                price, freight_value, price_usd, freight_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, item_records)
        
        self.conn.commit()

        # Also append to fact_orders.csv for instant Power BI 1-click Refresh!
        csv_path = os.path.join(DATA_DIR, "fact_orders.csv")
        try:
            with open(csv_path, "a", encoding="utf-8") as f:
                # Format: order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date,currency,fx_rate_to_usd,total_order_value_usd
                row_str = f"{order_id},{cust_id},{status},{timestamp_str},{timestamp_str},,,{estimated_delivery},{currency},{fx_rate},{round(total_usd, 2)}\n"
                f.write(row_str)
        except Exception as e:
            pass
        
        # Log event to terminal
        print(f"[{now.strftime('%H:%M:%S')}] [LIVE EVENT] {order_id} | Customer: {cust_id} ({cust_city}) | "
              f"Items: {num_items} | Currency: {currency} | "
              f"Total: ${total_usd:,.2f} USD ({currency} {round(total_usd * fx_rate, 2):,.2f})")

    def run_stream(self, max_events=None):
        """Streams live orders continuously or up to max_events."""
        print(f"\n>>> Starting Live Ingestion Stream (Interval: {self.interval}s) <<<")
        print("Press Ctrl+C to stop streaming.\n")
        events_emitted = 0
        try:
            while True:
                self.generate_single_order()
                events_emitted += 1
                if max_events and events_emitted >= max_events:
                    print(f"\n[STREAM COMPLETED] Successfully emitted {events_emitted} live orders.")
                    break
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[STREAM STOPPED] Worker safely shut down by user.")
        finally:
            self.conn.close()


if __name__ == "__main__":
    # If passed an integer argument, emit that many events then stop
    max_ev = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    producer = OrderStreamProducer(interval_seconds=1)
    producer.run_stream(max_events=max_ev)

