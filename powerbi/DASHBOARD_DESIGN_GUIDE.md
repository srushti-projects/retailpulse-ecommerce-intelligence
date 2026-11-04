# RetailPulse — Power BI Dashboard Design Guide

This guide walks you through building the 3-page Executive Suite in Power BI Desktop using the clean data files located in `data/`.

---

## Step 1: Loading Data into Power BI Desktop

1. Open **Power BI Desktop**.
2. Click **Get Data** ➔ **Text/CSV**.
3. Load the 6 CSV files from the `data/` folder:
   - `dim_customers.csv`
   - `dim_products.csv`
   - `dim_date.csv`
   - `fact_orders.csv`
   - `fact_order_items.csv`
   - `fact_order_payments.csv`
4. Click **Load**.

---

## Step 2: Verifying Relationships (Model View)

Switch to the **Model View** (icon on the left navigation bar). Verify that the relationships form a clean **Star Schema**:

* `dim_customers[customer_id]` `1 ─── *` `fact_orders[customer_id]`
* `dim_date[full_date]` `1 ─── *` `fact_orders[order_purchase_timestamp]` *(Convert date type if prompted)*
* `dim_products[product_id]` `1 ─── *` `fact_order_items[product_id]`
* `fact_orders[order_id]` `1 ─── *` `fact_order_items[order_id]`
* `fact_orders[order_id]` `1 ─── *` `fact_order_payments[order_id]`

---

## Step 3: Page 1 — Executive Sales Overview

### Layout & Visuals:
1. **Top KPI Header (4 Card Visuals):**
   * **Card 1:** `[Total GMV]` (Formatted as Currency USD, e.g. `$18.42M`)
   * **Card 2:** `[Net Delivered GMV]` (e.g. `$16.20M`)
   * **Card 3:** `[Total Orders]` (Formatted as Number, e.g. `25.0K`)
   * **Card 4:** `[AOV]` (Average Order Value, e.g. `$736.80`)
2. **Main Trend Chart (Line & Clustered Column Combo Chart):**
   * **X-Axis:** `dim_date[year]` and `dim_date[month_name]`
   * **Column Y-Axis:** `[Total GMV]`
   * **Line Y-Axis:** `[MoM Growth %]`
   * *Purpose:* Shows monthly revenue volume alongside growth momentum.
3. **Category Breakdown (Clustered Bar Chart):**
   * **Y-Axis:** `dim_products[product_category_name]`
   * **X-Axis:** `[Total GMV]`
   * *Purpose:* Immediately highlights top-grossing categories (Electronics, Laptops).
4. **Top Slicers:**
   * Slicer for `dim_date[year]` (2023, 2024).
   * Slicer for `dim_customers[customer_city]`.

---

## Step 4: Page 2 — Customer & RFM Intelligence

### Layout & Visuals:
1. **Customer Volume Cards:**
   * **Card 1:** `[Total Customers]`
   * **Card 2:** `[Cancellation Rate %]`
   * **Card 3:** `[Return Rate %]`
2. **RFM Customer Segment Distribution (Treemap / Donut Chart):**
   * **Category:** `customer_segment` (from `sql/02_rfm_analysis.sql` or calculated column)
   * **Values:** `[Total Customers]` and `[Total GMV]`
   * *Purpose:* Displays the proportion of Champions, Can't Lose Them, New, and Churned customers.
3. **At-Risk VIP Watchlist (Table Visual):**
   * **Columns:** `dim_customers[customer_id]`, `customer_city`, `Total Spend`, `Days Inactive`
   * **Filter:** Show only segment = `'Can''t Lose Them (At Risk)'`
   * *Purpose:* Actionable list for the CRM/Marketing team to send win-back discount vouchers.

---

## Step 5: Page 3 — Product & Payment Operations

### Layout & Visuals:
1. **Pareto 80/20 Product Concentration (Combo Chart):**
   * **X-Axis:** `dim_products[product_id]` (sorted by sales DESC)
   * **Column Values:** `[Total GMV]`
   * **Line Values:** Cumulative % of Revenue
2. **Payment Gateway Risk Analysis (Matrix / Table Visual):**
   * **Rows:** `fact_order_payments[payment_type]`
   * **Values:** `[Total Orders]`, `[Cancellation Rate %]`, `[Lost Cancelled GMV]`
   * *Insight:* Visually flags Debit Card's 20.4% cancellation anomaly in red conditional formatting!
3. **Geographic Sales Heatmap (Azure Map / Filled Map):**
   * **Location:** `dim_customers[customer_city]`
   * **Bubble Size:** `[Total GMV]`
   * *Purpose:* Visualizes top revenue hubs (Mumbai, Bengaluru, Delhi).
