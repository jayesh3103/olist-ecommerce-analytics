import sqlite3
import pandas as pd
import os

print("Connecting to Olist SQLite Database...")
conn = sqlite3.connect('data/olist.db')

# 1. Load Orders Data with Revenue and Timestamps
orders_query = """
SELECT 
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    c.customer_city,
    c.customer_state,
    p.payment_type,
    p.payment_value,
    p.payment_installments
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status IN ('delivered', 'shipped')
"""
print("Fetching Orders Data...")
df_orders = pd.read_sql_query(orders_query, conn)
df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])

# 2. Get unique customer mapping since our ML models use customer_unique_id
unique_cust_query = """
SELECT customer_id, customer_unique_id FROM customers
"""
df_cust_map = pd.read_sql_query(unique_cust_query, conn)

# Merge
df_main = df_orders.merge(df_cust_map, on='customer_id', how='left')

# 3. Load ML & Analytics Outputs
print("Loading ML and Analytics segments...")
rfm = pd.read_csv('outputs/rfm_segments.csv')
health = pd.read_csv('outputs/customer_health.csv')
churn = pd.read_csv('outputs/churn_predictions.csv')

# Rename and select columns to match Power BI DAX Guide
health = health.rename(columns={'clv_forecast': 'CLV'})
churn = churn.rename(columns={'predicted_churn': 'at_risk'})
rfm = rfm.rename(columns={'Segment': 'segment'})

# Use customer_id as the merge key
health = health[['customer_id', 'health_score', 'CLV', 'churn_risk_norm']]
churn = churn[['customer_id', 'churn_probability', 'at_risk']]

# Merge into main customer dataset
df_customers = pd.DataFrame({'customer_id': df_main['customer_id'].unique()})
df_customers = df_customers.merge(rfm[['customer_id', 'segment', 'RFM_score', 'Recency', 'Frequency', 'Monetary']], on='customer_id', how='left')
df_customers = df_customers.merge(health, on='customer_id', how='left')
df_customers = df_customers.merge(churn, on='customer_id', how='left')

# 4. Merge everything into the Final Power BI Flat Table
print("Flattening dataset for Power BI...")
df_powerbi = df_main.merge(df_customers, on='customer_id', how='left')

# Export
os.makedirs('outputs', exist_ok=True)
output_path = 'outputs/powerbi_master_dataset.csv'
df_powerbi.to_csv(output_path, index=False)
print(f"Success! Master Power BI Dataset exported to: {output_path} ({len(df_powerbi)} rows)")

conn.close()
