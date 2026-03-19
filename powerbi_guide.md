# 📊 Power BI Dashboard Implementation Guide

This guide contains the exact steps and DAX formulas you need to perfectly replicate the "Differentiation Pyramid" dashboard exclusively inside Power BI.

## Step 1: Import the Data
1. Run `python notebooks/09_powerbi_export.py` to generate the master dataset.
2. Open Power BI Desktop.
3. Click **Get Data** > **Text/CSV**.
4. Select `outputs/powerbi_master_dataset.csv`.
5. Click **Load**. (No complex schema joining needed!)

---

## Step 2: Create the "What-If" Churn Simulator (Top 30% Factor)
This transforms your dashboard from a reporting tool to an interactive revenue simulator.

1. Go to **Modeling** > **New Parameter** > **Numeric Range**.
   * **Name**: Churn Reduction %
   * **Data Type**: Decimal Number
   * **Minimum**: 0.00 | **Maximum**: 0.30 | **Increment**: 0.01
   * **Default**: 0.05 (5%)
2. This will auto-generate a slicer (slider) on your canvas.

Now, right-click your dataset and click **New Measure** to create the interconnected logic:

```dax
Total Revenue = SUM([payment_value])
```

```dax
Total At-Risk Customers = 
CALCULATE(
    DISTINCTCOUNT([customer_unique_id]),
    [at_risk] = 1
)
```

```dax
Total At-Risk Revenue = 
CALCULATE(
    SUM([CLV]),
    [at_risk] = 1
)
```

And finally, the simulator logic:
```dax
Expected Recovered Revenue = 
[Total At-Risk Revenue] * 'Churn Reduction %'[Churn Reduction % Value]
```

---

## Step 3: Build the Dashboard Pages

### Page 1: Executive Overview
* **Cards (KPIs):** Drop in the exact Measures defined above (Total Revenue, At-Risk Revenue, Expected Recovered Revenue).
* **Line Chart:** `X-Axis` = `order_purchase_timestamp` | `Y-Axis` = `Total Revenue`
* **Donut Chart:** `Legend` = `segment` (from RFM) | `Values` = `Total Revenue`

### Page 2: Advanced Customer Intelligence
* **Scatter Plot:** 
   * `X-Axis` = `Recency`
   * `Y-Axis` = `health_score`
   * `Size` = `CLV`
   * `Color` = `segment`
* **Table (Customer Lookup):** Drop in `customer_unique_id`, `health_score`, `churn_prob`, `CLV`, and `segment`. 

### The Ultimate Interviewer Hook
Place the "Churn Reduction %" slider prominently on the Executive Overview. Tell the recruiter: 
> *"This isn't just a static report. I computed the predictive Churn Probability and Customer Lifetime Value (CLV) in Python, merged it into a single data model, and built this What-If slider so the VP of Marketing can drag it and dynamically see exactly how many Reais (R$) they will recover if their next retention campaign is 5%, 10%, or 15% effective."*
