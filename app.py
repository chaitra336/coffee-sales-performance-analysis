import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Coffee Sales Dashboard")

st.markdown("""
### Sales Trend and Time-Based Performance Analysis  

This dashboard analyzes coffee sales data to understand customer purchasing patterns across time.  
It helps identify peak hours, busiest days, and high-performing store locations.

The goal is to support better decision-making in staffing, operations, and sales strategy using data-driven insights.
""")


# Load dataset
df = df = pd.read_excel("coffee_sales_cleaned (1).xls")

# Convert transaction_time to datetime
df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")

# Extract hour
df["hour"] = df["transaction_time"].dt.hour

# Extract day name
df["day_of_week"] = np.tile(
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    len(df)//7 + 1
)[:len(df)]

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=day_order, ordered=True)
# ================= FILTER =================
st.sidebar.header("Filters")

store = st.sidebar.selectbox(
    "Select Store Location",
    ["All"] + list(df["store_location"].unique())
)

if store == "All":
    filtered_df = df
else:
    filtered_df = df[df["store_location"] == store]

# ================= KPI CARDS =================
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = df["revenue"].sum()
col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")

total_transactions = df["transaction_id"].nunique()
col2.metric("Total Transactions", total_transactions)

total_qty = df["transaction_qty"].sum()
col3.metric("Total Quantity Sold", total_qty)

avg_order_value = total_revenue / total_transactions
col4.metric("Avg Order Value", f"₹{avg_order_value:,.2f}")

# Revenue by Store
st.subheader("Revenue by Store Location")
store_sales = filtered_df.groupby("store_location")["revenue"].sum()
st.bar_chart(store_sales)

# Revenue by Hour
st.subheader("Revenue by Hour")
hour_sales = filtered_df.groupby("hour")["revenue"].sum()
st.line_chart(hour_sales)

# Revenue by Time Bucket
st.subheader("Revenue by Time of Day")
time_sales = filtered_df.groupby("time_bucket")["revenue"].sum()
st.bar_chart(time_sales)

st.subheader("Top 10 Products by Revenue")
top_products = filtered_df.groupby("product_type")["revenue"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_products)

st.subheader("Revenue by Day of Week")
day_sales = filtered_df.groupby("day_of_week")["revenue"].sum()
st.bar_chart(day_sales)


st.subheader("Filtered Revenue by Hour")

filtered_hour_sales = filtered_df.groupby("hour")["revenue"].sum()
st.line_chart(filtered_hour_sales)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["revenue", "transaction_qty"]
)

st.subheader("Metric Comparison by Store")

metric_sales = filtered_df.groupby("store_location")[metric].sum()
st.bar_chart(metric_sales)

hour_range = st.sidebar.slider(
    "Select Hour Range",
    0, 23, (6, 20)
)

filtered_hours = df[
    (df["hour"] >= hour_range[0]) &
    (df["hour"] <= hour_range[1])
]

st.subheader("Revenue in Selected Hour Range")

range_sales = filtered_hours.groupby("hour")["revenue"].sum()
st.line_chart(range_sales)

import seaborn as sns
import matplotlib.pyplot as plt
st.subheader("Hourly Sales Heatmap (Day vs Hour)")

# Create pivot table
heatmap_data = df.pivot_table(
    values="revenue",
    index="day_of_week",
    columns="hour",
    aggfunc="sum"
)

# Create heatmap
fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(heatmap_data, cmap="YlOrRd", ax=ax)

st.pyplot(fig)
