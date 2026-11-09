# RetailPulse — Power BI DAX Measures Library
This document provides production-ready DAX measures organized by business domain.

---

## 1. Core Sales & Volume Metrics

### Total GMV (Gross Merchandise Value)
```dax
Total GMV = SUM(fact_orders[total_order_value_usd])
```

### Total Orders
```dax
Total Orders = DISTINCTCOUNT(fact_orders[order_id])
```

### Total Customers
```dax
Total Customers = DISTINCTCOUNT(fact_orders[customer_id])
```

### Average Order Value (AOV)
```dax
AOV = DIVIDE([Total GMV], [Total Orders], 0)
```

---

## 2. Order Quality & Deductions

### Net Delivered GMV
```dax
Net Delivered GMV = 
CALCULATE(
    [Total GMV], 
    fact_orders[order_status] = "delivered"
)
```

### Cancelled Orders
```dax
Cancelled Orders = 
CALCULATE(
    [Total Orders], 
    fact_orders[order_status] = "cancelled"
)
```

### Cancellation Rate %
```dax
Cancellation Rate % = 
DIVIDE([Cancelled Orders], [Total Orders], 0)
```

### Returned Orders
```dax
Returned Orders = 
CALCULATE(
    [Total Orders], 
    fact_orders[order_status] = "returned"
)
```

### Return Rate %
```dax
Return Rate % = 
DIVIDE([Returned Orders], [Total Orders], 0)
```

---

## 3. Time Intelligence & Growth Momentum

### GMV Previous Month (MoM Baseline)
```dax
GMV Previous Month = 
CALCULATE(
    [Total GMV],
    DATEADD(dim_date[full_date], -1, MONTH)
)
```

### MoM Growth %
```dax
MoM Growth % = 
DIVIDE(
    [Total GMV] - [GMV Previous Month],
    [GMV Previous Month],
    0
)
```

### Cumulative Running GMV (YTD)
```dax
Cumulative GMV YTD = 
TOTALYTD([Total GMV], dim_date[full_date])
```

---

## 4. Product & Item Intelligence

### Total Units Sold
```dax
Total Units Sold = COUNTROWS(fact_order_items)
```

### Items Per Order (Basket Depth)
```dax
Avg Basket Depth = DIVIDE([Total Units Sold], [Total Orders], 0)
```

---

## 5. Best Practice: The `_Measures` Table
In Power BI Desktop:
1. Go to **Home** ➔ **Enter Data**.
2. Name the table `_Measures`.
3. Create all your new measures inside this table.
4. Delete the empty default `Column1`.
5. Power BI will automatically promote `_Measures` with a calculator icon to the top of your field list!

