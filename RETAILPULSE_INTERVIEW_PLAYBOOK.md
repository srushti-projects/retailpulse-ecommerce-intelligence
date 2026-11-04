# RetailPulse — Real-Time E-Commerce Intelligence Platform
## Complete Master Case Study & Interview Playbook

> **Candidate Project Reference**: *RetailPulse*  
> **Role Targeted**: Business / Data Analyst (E-Commerce, Quick-Commerce, FinTech)  
> **Core Tech Stack**: PostgreSQL / SQLite, Python (FastAPI / ETL), Power BI (DAX), Pandas, Real-Time APIs  

---

## 1. Executive Summary & Business Objective

### The Business Problem
At major e-commerce platforms (Amazon, Flipkart, Walmart), executives and category managers need continuous visibility into operational performance, revenue health, and customer retention. Traditional static weekly/monthly reporting is too slow to catch issues like sudden drop-offs in category demand, payment gateway failures, or regional margin erosions.

### The Solution: RetailPulse
A hybrid e-commerce intelligence system combining:
1. **Historical Enterprise Foundation**: A multi-table relational database of 25,000+ real retail orders, 37,000+ order items, 5,000 customers, and 248 products across 7 categories.
2. **Real-Time Streaming Engine**: A Python event generator simulating live incoming checkouts and cart status updates into the database.
3. **Live Macro Context Ingestion**: Real-time Foreign Exchange (FX) rates (via Frankfurter API) to normalize multi-currency transactions (USD, INR, EUR, BRL) into a single global reporting currency.
4. **Interactive BI & Analytics Layer**: Power BI dashboard equipped with advanced DAX KPIs (AOV, MoM/YoY growth, RFM customer segmentation, delivery SLA adherence).

---

## 2. Architecture & Data Flow

```
┌────────────────────────────────┐       ┌────────────────────────────────┐
│   Historical Base Data         │       │  Live Macro API (FX)           │
│   (25k Orders - Star Schema)   │       │  - Frankfurter API (Live rates)│
└───────────────┬────────────────┘       └───────────────┬────────────────┘
                │                                        │
                ▼                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Python Ingestion & Stream Engine                     │
│  - Event Generator emits simulated live checkouts every N seconds     │
│  - Fetches latest currency rates & calculates normalized GMV in USD    │
│  - Validates and buffers payloads before database load                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        SQL Data Warehouse                              │
│  - Star Schema (Fact_Orders, Fact_Order_Items, Dim_Customers, etc.)    │
│  - Advanced SQL Views: RFM Segmentation, Cohort Retention, MoM Trends  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Power BI Executive Suite                        │
│  - Executive Overview: GMV, Net Revenue, Orders, AOV, Return Rate      │
│  - Category & Product Deep Dive: Pareto 80/20, Price Elasticity        │
│  - Customer Intelligence: RFM Segmentation Grid, Churn Risk Matrix     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sprint Logs: The Complete Analytical Q&A Bank

### Sprint 1: Executive Sales Intelligence & Metric Design

#### Q1: Why is "Total Revenue" (Gross Sales) alone insufficient on an executive card?
* **Candidate's Insight**: Revenue can look high while orders are dropping (e.g., fewer buyers buying higher-priced items), or massive cancellations and returns might wipe out profits.
* **Industry Standard Metric Suite**:
  1. **GMV (Gross Merchandise Value)**: Total dollar value of customer orders placed before deductions.
  2. **Net Revenue**: $\text{GMV} - (\text{Cancellations} + \text{Returns})$. What the business actually banks.
  3. **Order & Customer Count**: Volume indicators to detect market share and customer base growth.
  4. **AOV (Average Order Value)**: $\frac{\text{Total Revenue}}{\text{Total Orders}}$. Measures basket size and purchasing power.
  5. **Return / Cancellation Rate (%)**: $\frac{\text{Cancelled or Returned Orders}}{\text{Total Orders}} \times 100$.

#### Q2: What benchmarks should revenue be compared against to make it actionable?
* **Candidate's Insight**: Compare against **Target / Budget** (Actual vs. Planned).
* **Industry Standard Benchmarks**:
  * **Target Variance (%)**: $\frac{\text{Actual} - \text{Target}}{\text{Target}} \times 100$.
  * **Month-over-Month (MoM)**: Compares current month vs. immediately preceding month to track momentum.
  * **Year-over-Year (YoY)**: Compares current month vs. the exact same month last year. Essential in retail due to major seasonality (e.g., Diwali, Prime Day, Cyber Monday).

#### Q3: How do you visualize trend performance and diagnose sudden dips?
* **Candidate's Insight**: Use a **Line Chart** (time on X, revenue on Y) because it displays continuous time series clearly. On a sudden dip, drill down into **Product Category** first.
* **Why Not a Pie Chart?**: Human perception struggles to evaluate angles and areas accurately when there are more than 2–3 categories. Bar and line charts allow exact comparative alignment.

---

### Sprint 2: Data Warehousing & Dimensional Modeling (Star Schema)

#### Q1: What is the difference between a Fact Table and a Dimension Table?
* **Fact Table (The Verbs/Measurements)**: Contains numeric measures, counts, timestamps, and foreign keys.
  * *Examples*: `Order_ID`, `Unit_Price`, `Quantity`, `Discount_Amount`, `Shipping_Fee`.
* **Dimension Table (The Nouns/Context)**: Contains descriptive textual attributes used to slice, dice, and filter facts.
  * *Examples*: `Customer_Name`, `City`, `Product_Category`, `Payment_Method`.

#### Q2: Why avoid storing everything in one flat 40-column table (Denormalized)?
* **Candidate's Insight**: Excessive storage redundancy, difficulty in updating repeated records, and sluggish filtering.
* **Technical Terms**:
  * **Update Anomaly**: If a customer changes their delivery address, updating 50 past order rows creates a high risk of inconsistent data. In a Star Schema, the address is updated once in `Dim_Customers`.
  * **Storage & Index Optimization**: Fact tables store clean, lightweight integer IDs linking to dimensions, minimizing table bloat.

#### Q3: What dimensions belong in an E-Commerce Star Schema?
* `Dim_Customers`: Who purchased (Customer ID, Name, Segment, City, State).
* `Dim_Products`: What was bought (Product ID, Title, Category, Dimensions, Base Price).
* `Dim_Date`: When it occurred (Date Key, Day, Month, Quarter, Year, Day of Week, Holiday Flag).
* `Dim_Geography`: Where it was shipped (Zip Code, City, State, Country, Region).

---

### Sprint 3: The "Fact Table Grain" & Real-Time Architecture

#### Q1: If an order has multiple items, where does the Order-Level Shipping Fee go?
* **Candidate's Insight**: If placed on every item row, running `SUM(shipping_fee)` duplicates the fee for every item in the cart.
* **The Solution — Two-Fact Architecture**:
  * `Fact_Orders` (Grain: 1 row per order): Stores `order_id`, `customer_id`, `order_date`, `shipping_fee`, `order_status`, `payment_method`.
  * `Fact_Order_Items` (Grain: 1 row per order item): Stores `order_id`, `item_id`, `product_id`, `unit_price`, `quantity`, `freight_value`.
  * *Why this matters*: Keeps aggregations mathematically pure without needing complex subqueries or grouping hacks in SQL/DAX.

#### Q2: What is a Live Event Payload in E-Commerce?
When a customer clicks checkout, the application pushes a lightweight JSON object to the message bus/API:
```json
{
  "order_id": "ORD-025001",
  "customer_id": "CUST-03124",
  "timestamp": "2026-11-04T11:59:34Z",
  "currency": "USD",
  "items": [
    {"product_id": "PROD-0042", "qty": 1, "price_usd": 1200.00},
    {"product_id": "PROD-0118", "qty": 1, "price_usd": 1389.60}
  ],
  "shipping_fee_usd": 12.50,
  "payment_method": "credit_card"
}
```

#### Q3: Why prioritize Live Currency Exchange (FX) over Weather for global e-commerce?
* **Candidate's Insight**: FX applies year-round to all cross-border transactions, whereas weather is localized and seasonal.
* **Business Value**: Allows normalization of international sales into a single reporting currency (e.g., USD or INR) using real-time conversion rates.

---

### Sprint 4: Advanced Customer Analytics (RFM & Cohorts)

#### 1. RFM Segmentation (Recency, Frequency, Monetary)
* **Definition**: A behavioral customer segmentation technique that quantifies when a customer last bought, how often they buy, and how much they spend.
* **The Metrics**:
  * **Recency (R)**: Days elapsed since the customer's last completed purchase. *Lower days = Higher score.*
  * **Frequency (F)**: Total number of orders placed in a given evaluation window (e.g., 365 days). *Higher orders = Higher score.*
  * **Monetary (M)**: Total currency value spent by the customer. *Higher spend = Higher score.*
* **Customer Personas & Business Actions**:
  * **Champions (High R, High F, High M)**: Top 30% of customer base driving 70%+ of revenue ($13.3M GMV in our dataset).  
    *Action*: Loyalty rewards, early access to new launches, VIP support.
  * **Can't Lose Them / At Risk (Low R, High F, High M)**: Historically heavy spenders who haven't shopped in 200+ days (e.g., Vikram, holding $1.95M past value).  
    *Action*: Win-back SMS/Email campaigns with personalized high-value vouchers.
  * **New / Promising (High R, Low F, Medium M)**: Recently acquired customers who placed 1–2 orders.  
    *Action*: Onboarding email series, cross-sell related categories.
  * **Lost / Churned (Low R, Low F, Low M)**: One-time low-value buyers from over a year ago.  
    *Action*: Exclude from expensive paid ad retargeting to preserve ad spend.

#### 2. Cohort Analysis & Retention (The "Leaky Bucket")
* **The Business Problem**: Looking solely at Monthly Active Users (MAU) hides customer churn. If marketing spends heavily to acquire new users while older users churn immediately, the business is bleeding cash.
* **Cohort Definition**: A group of customers grouped by their first purchase month (e.g., "Jan 2023 Cohort").
* **Retention Calculation**:
  $$\text{Retention Rate (Month } N\text{)} = \frac{\text{Active Customers from Cohort in Month } N}{\text{Total Customers in Cohort at Month 0}} \times 100$$
* **Reading the Matrix**: Comparing retention decay curves across cohorts reveals whether product improvements or marketing campaigns improve long-term loyalty.

---

### Sprint 5: The E-Commerce Conversion Funnel & Cart Abandonment

#### 1. The Funnel Stages
$$\text{Product Views (PDP)} \longrightarrow \text{Add to Cart (ATC)} \longrightarrow \text{Checkout Initiated} \longrightarrow \text{Purchase Completed}$$

* **Overall Conversion Rate (CR)**: $\frac{\text{Completed Orders}}{\text{Total Product Views}} \times 100$ (Benchmark: 1.5% - 3.5%).
* **Cart Abandonment Rate (CAR)**: $\frac{\text{Carts Created} - \text{Orders Placed}}{\text{Carts Created}} \times 100$ (Global Benchmark: ~70%).

#### 2. Diagnostic Root Causes
* **High Views, Low Add-to-Cart**: "Window shopping" / Aspirational browsing (luxury items), high price vs competitors, or lack of reviews.
* **High Add-to-Cart, High Checkout Drop-off**: "Price Shock" (unexpected platform fees, shipping costs added at checkout), forced registration.
* **High Checkout, Low Purchase**: Technical friction (payment gateway down, OTP latency, lack of preferred local payment rails like UPI/EMI).

#### 3. Automated Business Recovery
* **Cart Abandonment Recovery Workflow**: Automated triggered messages at +1h (scarcity/urgency push notification) and +12h (personalized time-bound discount voucher) recovering 15–20% of abandoned GMV.

---

### Sprint 6: Product & Category Intelligence (Pareto 80/20 & Inventory Health)

#### 1. The 80/20 Pareto Principle in Retail
* **Core Rule**: In e-commerce catalogs, roughly **20% of top-selling products generate 80% of total revenue**.
* **ABC Classification**:
  * **Class A**: Top 20% products driving 80% GMV (Blockbuster SKUs, high velocity).
  * **Class B**: Next 30% products driving 15% GMV.
  * **Class C**: Remaining 50% products driving 5% GMV (Long-tail / slow movers).
* **Visualization**: A **Pareto Chart** (Combo chart: Clustered Columns for individual product revenue + Line on secondary axis for cumulative % of total revenue).

#### 2. Inventory Health & Days of Inventory on Hand (DOH)
$$\text{DOH} = \frac{\text{Current Inventory Units}}{\text{Average Daily Units Sold}}$$
* **Stockout Disasters**: Direct loss of GMV, search algorithm penalty (platforms derank out-of-stock listings), customer churn to competitors.
* **Overstocking / Dead Stock Solutions**: Bundling with Class A items, targeted flash outlet promotions to free up warehouse space.

---

### Sprint 7: Advanced SQL Analytics & Window Functions

#### 1. Window Function: `NTILE(n)` for Quartile Scoring
* **Definition**: Divides an ordered partition of rows into `n` approximately equal buckets (e.g., 4 quartiles).
* **Recency Rule**: In NTILE, bucket 1 is assigned to the first rows.
  * `ORDER BY recency_days DESC`: Inactive customers (high days) get Bucket 1; recent buyers (low days) get Bucket 4.
  * `ORDER BY spend ASC`: Low spenders get Bucket 1; top spenders get Bucket 4.

#### 2. Window Function: `LAG()` and `LEAD()`
* **`LAG(column, offset)`**: Looks backward by `offset` rows in the ordered window. Essential for MoM comparisons:
  ```sql
  LAG(monthly_gmv, 1) OVER (ORDER BY sales_month ASC) AS prev_month_gmv
  ```
* **MoM Growth % Formula**:
  $$\text{MoM Growth \%} = \frac{\text{Current Month GMV} - \text{Previous Month GMV}}{\mathbf{Previous\ Month\ GMV}} \times 100$$
  *(Always divide by the Previous baseline, not Current!)*

#### 3. Window Function: Running Total / Cumulative GMV
* **Cumulative Aggregation**:
  ```sql
  SUM(monthly_gmv) OVER (ORDER BY sales_month ASC) AS cumulative_running_gmv
  ```
* **How It Works**: With `ORDER BY`, SQL defaults the window frame to `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, adding up all historical rows up to the current row.

#### 4. Diagnostic SQL: Payment Gateway Failure Detection
* **Real Project Finding in RetailPulse**:
  * Credit Card Failure Rate: **3.87%**
  * UPI Failure Rate: **3.89%**
  * Voucher Failure Rate: **4.26%**
  * **Debit Card Failure Rate: 20.41% (Over $411,000 in lost GMV!)**
* **Root Cause**: Pinpointed bank OTP / 3DS redirect timeout on Debit Card payment rails.

---

### Sprint 8: Power BI & DAX Architecture

#### 1. Safe Division with `DIVIDE()`
* Syntax: `DIVIDE(Numerator, Denominator, AlternateValue)`
* Example: `AOV = DIVIDE([Total GMV], [Total Orders], 0)`
* Avoids `#ERROR` on division by zero when filter context has 0 orders.

#### 2. The Filter Context Modifier: `CALCULATE()`
* Syntax: `CALCULATE(<Expression>, <FilterCondition>)`
* Example:
  ```dax
  Net Delivered GMV = CALCULATE([Total GMV], fact_orders[order_status] = "delivered")
  ```
* Rewrites the filter context on the fly (equivalent to a dynamic SQL `WHERE` clause).

#### 3. Time Intelligence in DAX
* **Previous Month Comparison**:
  ```dax
  GMV Previous Month = CALCULATE([Total GMV], DATEADD(dim_date[full_date], -1, MONTH))
  ```
* **Cumulative Year-To-Date (YTD)**:
  ```dax
  Cumulative GMV YTD = TOTALYTD([Total GMV], dim_date[full_date])
  ```

---

## 4. How to Talk About This Project in Interviews

### The "Elevator Pitch" (30 Seconds):
> *"For my portfolio, I built **RetailPulse**, an end-to-end retail intelligence platform modeled after analytics systems at Amazon and Flipkart. Instead of a static dashboard, I architected a hybrid engine: a 25,000-order Star Schema in SQL, connected to a live Python event streamer that simulates real-time checkouts with on-the-fly currency conversion using a live Foreign Exchange API. On top of this, I built diagnostic SQL scripts for RFM customer segmentation, cohort retention heatmaps, and payment gateway risk analysis, and visualized the business insights across a 3-page Power BI executive suite."*

### Key Interview Talking Points (The "Stories"):
1. **The Debit Card Failure Story:**  
   *"While running payment gateway diagnostics, I noticed that Debit Card transactions had an abnormal 20.4% cancellation rate compared to our 3.8% platform baseline, costing \$411k in lost GMV. This demonstrated how diagnostic SQL directly saves revenue."*
2. **The Retention Cohort Story:**  
   *"Rather than looking at static monthly active users, I wrote a multi-step CTE query to track monthly cohort retention. I found that retention dropped from 30% in January down to 11% by June, signaling to marketing that post-onboarding engagement was leaking customers."*
3. **The RFM Champions Story:**  
   *"Using NTILE window functions, I classified 5,000 customers into 5 behavioral tiers. We found that 31% of customers were 'Champions' driving \$13.3M in GMV, while 442 VIP customers were 'At Risk' holding \$1.95M in past spend that required immediate win-back campaigns."*

---

## 5. End-to-End Project Roadmap & Milestones

| Milestone | Focus Area | Hands-on Deliverable | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1: Theory & Architecture** | Business Metrics, Star Schema, RFM, Cohorts, Funnels, Pareto | System Architecture & Analytical Blueprint | Completed ✅ |
| **Phase 2: Database & Data Pipeline** | SQLite / PostgreSQL & Python Streaming | Database schema setup, 25k records loaded, live FX API worker | Completed ✅ |
| **Phase 3: SQL Analytics Engine** | Advanced SQL & Window Functions | RFM segmentation, Cohort retention view, MoM GMV & Payment risk | Completed ✅ |
| **Phase 4: Power BI Executive Suite** | DAX & Visual Design | 3-Page dashboard guide & DAX measures library | Completed ✅ |
| **Phase 5: Portfolio & Interview Polish** | GitHub & Resume Narrative | Production README, architecture diagrams, interview script | Ready for Packaging 🚀 |

---
*(Saved in your project folder: RETAILPULSE_INTERVIEW_PLAYBOOK.md)*
