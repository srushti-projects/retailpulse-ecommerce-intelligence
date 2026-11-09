# ⚡ RETAILPULSE — 1-PAGE DOUBLE-SIDED INTERVIEW CHEAT SHEET
> **Print Guide:** Print double-sided (Page 1 = Front, Page 2 = Back). Keep this in your folder or pocket before every interview.

---

# 📄 [FRONT SIDE] The Elevator Pitch & Trap Questions

---

### 🎙️ 1. The 60-Second Interview Elevator Pitch (Word-for-Word)
> *"I built **RetailPulse**, a real-time e-commerce intelligence and revenue diagnostics platform analyzing 25,000+ orders across \$18.4M in GMV.*
> 
> *I designed the data warehouse using a **Kimball Star Schema** with B-Tree indexing, enforcing grain separation across order headers, item line items, and payment splits to eliminate fan-out errors. On top of this, I authored a modular SQL analytics engine using multi-stage CTEs and window functions—specifically building an **RFM segmentation model via `NTILE(4)` quartiles**, and a calendar-offset **Cohort Retention Matrix**.*
> 
> *The most critical business discovery I made was an **operational payment rail anomaly**: while Credit Cards and UPI maintained a healthy 3.8% cancellation baseline, Debit Cards exhibited a **20.41% failure rate**, leaking **\$411,280 in lost GMV**. Using a 5 Whys Root Cause Analysis, I traced this to 3DS authentication timeouts caused by bank SMS OTP delivery latency exceeding the 60-second gateway window.*
> 
> *I modeled an engineering remediation—extending the timeout to 120s with dynamic UPI rerouting—projected to recover **\$316,000 in lost GMV** with zero marketing spend, and surfaced everything in an executive 3-page Power BI suite powered by custom DAX time intelligence and live currency normalization."*

---

### 🧠 2. The 3 Killer "Trap Questions" & Bulletproof Answers

#### ❓ Trap Q1: *"Why build a Star Schema? Why not just load a single flat 40-column table into Power BI?"*
* **Your Answer:**  
  *"Two reasons: **Grain Fan-Out** and **Engine Performance**. In a flat table where each row is an order item, orders with multiple items duplicate order headers and payment values. If you do a simple `SUM(total_order_value)`, you inflate GMV by 30% to 50% due to fan-out. Furthermore, VertiPaq memory compresses star schemas exponentially better than flat wide tables with high column cardinality, ensuring sub-second visual refresh speeds."*

#### ❓ Trap Q2: *"In your RFM query, why did you sort recency DESC in `NTILE(4)`?"*
* **Your Answer:**  
  *"`NTILE` assigns Bucket 1 to the first group and Bucket 4 to the last. In RFM, **4 is the best score**. For frequency and monetary spend, higher is better, so sorting `ASC` places top spenders in Bucket 4. But for **recency, lower days is better** (a purchase 2 days ago is better than 200 days ago). If you sort `ASC`, the active customer gets Bucket 1! Sorting `recency_days DESC` places 300-day inactive users in Bucket 1 and 2-day recent buyers in Bucket 4."*

#### ❓ Trap Q3: *"How do you prove the 3DS timeout caused the $411K debit card loss, rather than users lacking funds?"*
* **Your Answer:**  
  *"Through **error code telemetry and baseline comparison**. In our gateway logs, insufficient funds (`ERR_INSUFFICIENT_FUNDS`) accounted for only ~4% across all payment methods. However, **78% of debit card drops** were explicitly tagged `AUTH_TIMEOUT_EXPIRED` (user never submitted OTP). Because credit cards on the exact same platform had only a 3.87% cancellation rate, the 16.5% excess cancellation rate is an operational infrastructure failure, not buyer insolvency."*

---

### 🔢 3. The 5 Golden Numbers to Memorize
* **\$18.42M GMV** across **25,003 Orders** and **5,000 Customers** (Average Order Value: **\$736.80**).
* **20.41% Debit Card Failure Rate** vs. **3.87% Baseline** on Credit Card / UPI (5.3x higher).
* **\$411,280.01 Lost GMV** across **516 Cancelled Debit Card Orders**.
* **\$316,288 Recoverable GMV** by fixing the 3DS timeout and auto-rerouting to UPI.
* **31.9% Champions (1,435 users)** generate **71.9% (\$13.31M) of total platform GMV** (Pareto rule).

---
\pagebreak
---

# 📄 [BACK SIDE] Quick Technical & Architectural Reference

---

### 🛠️ 1. SQL Quick Pointers & Patterns
* **Star Schema Grain Hierarchy:**
  * `dim_customers` (Who) | `dim_products` (What) | `dim_date` (When).
  * `fact_orders` (Grain: 1 row per order transaction).
  * `fact_order_items` (Grain: 1 row per item within an order $\rightarrow$ Composite PK: `(order_id, order_item_id)`).
  * `fact_order_payments` (Grain: 1 row per payment split $\rightarrow$ Composite PK: `(order_id, payment_sequential)`).
* **B-Tree Indexing Rule:** Index all Foreign Keys (`customer_id`, `product_id`) and frequent filter columns (`order_status`, `order_purchase_timestamp`) to avoid $O(N)$ full-table scans.
* **Month-Offset Integer Math (Cohort Retention):**
  $$\text{Cohort Index} = (\text{Year} - \text{BirthYear}) \times 12 + (\text{Month} - \text{BirthMonth})$$
* **Single-Pass Conditional Aggregation (Script 05):**
  * `COUNT(DISTINCT CASE WHEN order_status = 'cancelled' THEN order_id END)`: Evaluates multiple metric branches in 1 table scan because SQL ignores `NULL`s.
* **MoM Growth % Safeguard:** `(Current - Prev) / Prev * 100` with `CASE WHEN prev IS NULL THEN 0.0`.

---

### 📐 2. DAX Core Rules & Mechanics
* **Row Context:** Knowing which single row is being evaluated (Calculated Columns, `SUMX`). Does *not* filter other tables.
* **Filter Context:** Active filters from slicers, visuals, page filters, and `CALCULATE`.
* **Context Transition:** `CALCULATE` converts a Row Context into an equivalent Filter Context.
* **Safe Division Rule:** Always use `DIVIDE([Numerator], [Denominator], 0)`—never the slash `/` operator—to prevent `#DIV/0!` errors.
* **Time Intelligence Golden Rule:** `DATEADD` and `TOTALYTD` require a contiguous date dimension table (`dim_date`) marked as a Date Table.
* **Measure Branching:** `[Total GMV] ➔ [GMV Prev Month] ➔ [MoM Growth %]`. Change once, updates everywhere.

---

### 🎨 3. Visual Design Rationales ("Why This Chart?")
* **Combo Chart (Page 1):** Dual-axis correlates absolute volume (GMV bars) with relative velocity (MoM growth line) without fragmenting context into 2 charts.
* **Horizontal Bar Chart (Page 1):** Essential for category names (`computers_accessories`) so labels read horizontally without tilt or truncation.
* **Treemap (Page 2):** Nested areas make the 72% GMV dominance of Champions visually unmistakable in 1 second.
* **Matrix Heatmap (Page 2):** Avoids the unreadable "spaghetti chart" of 12 overlapping line series; 2D color gradient exposes Month 1 drop-off immediately.
* **Alert Table (Page 3):** Enables multi-metric diagnosis (Attempts, Cancels, Rate %, Lost $) with conditional alert red (`#FEE2E2`) drawing eyes directly to the anomaly.
* **Bubble Map (Page 3):** Scales by revenue rather than land mass, preventing huge empty states from visually overpowering dense urban economic hubs (São Paulo).

---

### 🔍 4. The 5 Whys Root Cause Analysis (RCA) Chain
$$\text{Symptom: 5.6\% Platform Cancellation} \longrightarrow \text{Slice: Debit Card at 20.41\%}$$
$$\longrightarrow \text{Error: 78\% AUTH\_TIMEOUT\_EXPIRED} \longrightarrow \text{Latency: Bank SMS takes 72s}$$
$$\longrightarrow \text{Root Cause: Gateway iframe hard-timed-out at 60s without fallback rail}$$
$$\longrightarrow \text{Remediation: 120s timeout window + WhatsApp/App Push + 1-click UPI reroute}$$
