# RetailPulse — Executive Power BI Design & UI/UX Master Guide
> **LinkedIn & Portfolio Edition**: How to design an executive-level, visually stunning e-commerce dashboard that catches the eyes of recruiters, VPs, and hiring managers.

---

## 🎨 1. Executive Color Palette & Theme (The "FinTech Modern" Theme)

Never use Power BI's default neon rainbow palette. Top corporate dashboards at companies like Stripe, Amazon, and Revolut use a **muted, high-contrast palette** with strict color psychology:

| Element | Color Name | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | Ultra-Light Gray | `#F4F5F7` | Soft on the eyes, makes white cards pop |
| **Card / Visual Container** | Pure White | `#FFFFFF` | Background for individual visual cards |
| **Primary Brand / Headers** | Deep Navy Slate | `#0F172A` | KPI values, main titles, table headers |
| **Secondary Neutral** | Muted Slate Gray | `#64748B` | Subtitles, axis labels, inactive states |
| **Primary Chart Accent** | Cobalt Royal Blue | `#2563EB` | Revenue bars, volume series |
| **Growth / Positive** | Emerald Mint | `#10B981` | Positive MoM growth, delivered orders |
| **Alert / Risk** | Coral Crimson | `#EF4444` | High cancellations, debit card anomaly |

---

## 📐 2. The 5 Golden Rules of Executive UI/UX Design

### Rule 1: The "Card Container" Architecture
* **Canvas Settings:** Set Page Background to `#F4F5F7` (100% transparency OFF / transparency = 0%).
* **Every Visual is a Card:** Turn ON **Background** for every visual ➔ set color to `#FFFFFF`.
* **Rounded Corners:** Format ➔ Visual ➔ Border ➔ Color: `#E2E8F0` | Radius: **10 px** to **12 px**.
* **Drop Shadow:** Turn ON **Shadow** ➔ Preset: *Bottom Right* | Transparency: **85%** | Blur: **6 px**. This gives the modern "floating card" effect seen on top web apps.

### Rule 2: Top KPI Card Hierarchy
Do not use the standard bulky Card visual. Use the **New KPI Card (or Card New)** visual:
* **Metric Value:** Font size **26 pt to 28 pt**, Bold, `#0F172A`.
* **Metric Title:** Font size **10 pt**, All Caps, Semi-bold, `#64748B` (e.g. `TOTAL GMV`).
* **Growth Indicator:** Small pill below or next to the value (e.g., `▲ +156.5% MoM` in green or `▼ -4.8%` in red).

### Rule 3: Left Navigation Bar (Sidebar)
Add a sleek dark vertical sidebar on the left side (width: 180px–200px):
* Background: `#0F172A` (Deep Navy).
* At top: Platform logo or text: `⚡ RetailPulse`.
* 3 Clean Navigation Buttons (using Page Navigator or Blank Buttons):
  1. `📊 Executive Overview`
  2. `👥 Customer & RFM`
  3. `⚙️ Operations & Risk`
* At bottom: Live status indicator: `🟢 System Live | Frankfurter FX`.

### Rule 4: Slicers that Look Like Modern Buttons
* Never use the default dropdown slicer if you only have 2–4 options.
* Convert the Year and Region slicers to **Tile / Button** style:
  * Format ➔ Slicer Settings ➔ Style: **Tile**.
  * Gives clean clickable pills: `[ All ]` `[ 2023 ]` `[ 2024 ]`.

### Rule 5: The "Executive Insight Callout Box" (Secret Sauce)
Recruiters love dashboards that explain the *business takeaway*, not just the chart.
* On each page, add a small white container card with a light blue or yellow left border and an icon:
  > **💡 Executive Takeaway:**  
  > *Black Friday surge in Nov 2023 drove +156.5% MoM GMV ($1.38M). However, Debit Card cancellations hit an abnormal 20.4%, leaking $411k in GMV.*

---

## 🖼️ 3. Page-by-Page Layout Blueprint

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Sidebar] │  PAGE 1: EXECUTIVE SALES OVERVIEW                                          │
│           ├────────────────────────────────────────────────────────────────────────────┤
│ ⚡RetailPulse│ [ Card 1 ]        [ Card 2 ]        [ Card 3 ]        [ Card 4 ]          │
│           │  TOTAL GMV        NET REVENUE       TOTAL ORDERS      AVERAGE BASKET (AOV) │
│ • Overview│  $18.42M          $16.20M           25,003            $736.80              │
│ • Customers│  ▲ +12.4% MoM     87.9% Delivered   ▲ +8.2% MoM       $75.40 Freight Incl  │
│ • Operations├─────────────────────────────────────────┬────────────────────────────────┤
│           │ [ Visual 1: Combo Line & Bar Chart ]      │ [ Visual 2: Category Rank ]    │
│           │ Monthly GMV ($) vs MoM Growth %           │ Horizontal Clustered Bar       │
│           │ (Bars: Total GMV | Line: MoM Growth %)    │ Electronics, Laptops, Fashion  │
│           ├─────────────────────────────────────────┴────────────────────────────────┤
│           │ [ Visual 3: Insight Callout Box ]                                          │
│ 🟢 Live FX│ 💡 Key Insight: Q4 festive spike generated 42% of annual volume...        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Page 1: Executive Sales Overview (The High-Impact Landing Page)
1. **Top Bar:** 
   * Page Title: `Executive Sales Performance & Revenue Health`
   * Slicers: Year `[2023 | 2024]` and Currency `[USD | INR | EUR]`.
2. **KPI Header Row (4 Cards):**
   * Card 1: `[Total GMV]` ($18.42M) with MoM % indicator.
   * Card 2: `[Net Delivered GMV]` ($16.20M) with Delivery SLA rate.
   * Card 3: `[Total Orders]` (25.0K orders).
   * Card 4: `[AOV]` ($736.80).
3. **Primary Center Visual (Combo Chart):**
   * **Visual Type:** Line and Clustered Column Chart.
   * **Shared X-Axis:** `dim_date[sales_month]`.
   * **Column Y-Axis:** `[Total GMV]` (Formatted in Millions `$0.00M`, Color: `#2563EB`).
   * **Line Y-Axis:** `[MoM Growth %]` (Color: `#10B981` Emerald, with data markers turned ON).
4. **Right Visual (Category Revenue Share):**
   * **Visual Type:** Clustered Bar Chart (Horizontal).
   * **Y-Axis:** `dim_products[product_category_name]`.
   * **X-Axis:** `[Total GMV]`.
   * **Data Labels:** Turned ON (values inside/outside bars).

---

### Page 2: Customer & RFM Intelligence (The "Data Science" Page)
1. **KPI Header Row:**
   * `[Total Customers]` (5,000)
   * `[Active Champions]` (1,435)
   * `[At-Risk VIP Spend]` ($1.95M)
   * `[Customer Churn Rate %]` (13.4%)
2. **Left Visual (RFM Customer Segments Treemap or Donut Chart):**
   * **Category:** `customer_segment` (Champions, Can't Lose Them, New, Lost).
   * **Values:** `[Total GMV]`.
   * **Colors:**
     * Champions: `#10B981` (Vibrant Green)
     * Can't Lose Them: `#F59E0B` (Amber Warning)
     * New / Promising: `#3B82F6` (Sky Blue)
     * Lost / Churned: `#94A3B8` (Muted Gray)
3. **Right Visual (At-Risk VIP Action Watchlist):**
   * **Visual Type:** Table Visual with conditional formatting.
   * **Columns:** `Customer ID`, `City`, `Total Spend ($)`, `Days Since Last Order`.
   * **Filter:** Filter visual to show only segment = `'Can''t Lose Them (At Risk)'`.
   * **Conditional Formatting:** Add a soft red/orange background bar on `Days Since Last Order` to highlight customers inactive for >200 days.
4. **Bottom Visual (Cohort Retention Heatmap):**
   * **Visual Type:** Matrix Visual.
   * **Rows:** `cohort_month` (Jan 2023, Feb 2023...).
   * **Columns:** Cohort Month Index (`M0`, `M1`, `M2`, `M3`, `M4`, `M5`, `M6`).
   * **Values:** `Retention %`.
   * **Conditional Formatting:** Background color gradient (Dark blue for 100% decaying to light pale blue for 10%).

---

### Page 3: Operations & Payment Risk (The "Root-Cause" Page)
1. **Top Visual (The Debit Card Anomaly Table):**
   * **Visual Type:** Table / Matrix Visual.
   * **Columns:** `Payment Method`, `Total Orders Attempted`, `Delivered Orders`, `Cancelled Orders`, `Cancellation Rate %`, `Lost GMV ($)`.
   * **Conditional Formatting:** Add an Alert Red background `#FEE2E2` with text `#DC2626` on **Cancellation Rate %** when `> 10%`. This immediately highlights the **20.4% Debit Card anomaly**!
2. **Bottom-Left Visual (Product Pareto 80/20 Curve):**
   * **Visual Type:** Line and Clustered Column Chart.
   * **X-Axis:** Top 30 Product IDs.
   * **Column Values:** Product GMV.
   * **Line Values:** Cumulative % (showing the 80% threshold line).
3. **Bottom-Right Visual (Geographic Sales Map):**
   * **Visual Type:** Filled Map or Bubble Map.
   * **Location:** `dim_customers[customer_city]`.
   * **Bubble Size:** `[Total GMV]`.

---

## 📱 4. The Viral LinkedIn Post Blueprint

When your dashboard is done, take **3 crisp, high-resolution screenshots** (Page 1, Page 2, and Page 3) or record a 30-second screen-recording clicking between the tabs.

Here is an optimized LinkedIn post template designed to attract Data Analytics recruiters:

```markdown
🚀 Excited to share my latest data analytics project: RetailPulse — A Real-Time E-Commerce Intelligence Platform!

Rather than building a standard static dashboard, I wanted to simulate how analytics teams at Amazon, Flipkart, and Walmart monitor commercial health, customer retention, and operational anomalies.

Key Architecture Highlights:
🔹 Data Modeling: Architected a Kimball Star Schema across 25,000+ orders, 37,000+ order items, and 5,000 customers in SQL.
🔹 Live Streaming & Ingestion: Built a Python event generator that streams live checkouts into the database with real-time currency conversion using the Frankfurter Foreign Exchange (FX) API.
🔹 Advanced SQL Engine: Leveraged Window Functions (NTILE, LAG, SUM OVER) and multi-level CTEs for RFM customer segmentation and month-over-month momentum tracking.

🔍 3 Major Business Findings from the Analysis:
1️⃣ The Payment Anomaly: Uncovered that Debit Card transactions suffered from an abnormal 20.4% cancellation rate (vs. 3.8% platform baseline), resulting in over $411,000 in lost GMV due to 3DS gateway timeouts.
2️⃣ RFM Customer Retention: Segmented the customer base into 5 behavioral tiers—finding that 31% of users are "Champions" driving $13.3M in revenue, while 442 "At-Risk VIPs" represent $1.95M in slipping spend requiring win-back campaigns.
3️⃣ The Cohort "Leaky Bucket": Monthly cohort analysis revealed customer retention decay from 30.0% in Month 1 down to 11.3% by mid-year, highlighting critical post-onboarding friction.

Tech Stack: SQL (PostgreSQL/SQLite) | Python (ETL & Live Streaming) | Power BI (Advanced DAX) | Dimensional Modeling

💻 GitHub Repo with complete SQL scripts, data pipeline, and DAX measures: [Link in comments]

Feedback and thoughts from senior analysts and data leaders are warmly welcomed!

#DataAnalytics #PowerBI #SQL #DataScience #BusinessIntelligence #Ecommerce #PortfolioProject #Analytics
```

---
*(Saved in your project folder: powerbi/DASHBOARD_DESIGN_GUIDE.md)*
