import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

st.set_page_config(layout="wide")

st.title("☕ Coffee Sales Dashboard")

st.markdown("""
### Sales Trend and Time-Based Performance Analysis  

This dashboard analyzes coffee sales data to understand customer purchasing patterns across time.  
It helps identify peak hours, busiest days, and high-performing store locations.

The goal is to support better decision-making in staffing, operations, and sales strategy using data-driven insights.
""")

# ================= LOAD DATA =================
df = pd.read_csv("coffee_sales.csv")

# ================= DATA PREPARATION =================
df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
# Create proper day of week
df["day_of_week"] = pd.to_datetime(df["transaction_time"]).dt.day_name()

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=day_order, ordered=True)
# Create revenue if not present
if "revenue" not in df.columns:
    df["revenue"] = df["transaction_qty"] * df["unit_price"]

# Extract hour
df["hour"] = df["transaction_time"].dt.hour

# Time bucket
df["time_bucket"] = pd.cut(
    df["hour"],
    bins=[0,6,12,18,24],
    labels=["Night","Morning","Afternoon","Evening"],
    right=False
)

# Day of week
df["day_of_week"] = df["transaction_time"].dt.day_name()

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=day_order, ordered=True)

# ================= SIDEBAR FILTERS =================
st.sidebar.header("Filters")

store = st.sidebar.selectbox(
    "Select Store Location",
    ["All"] + sorted(df["store_location"].dropna().unique())
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["revenue", "transaction_qty"]
)

hour_range = st.sidebar.slider(
    "Select Hour Range",
    0, 23, (6, 20)
)

# ================= FILTER DATA =================
filtered_df = df.copy()

if store != "All":
    filtered_df = filtered_df[filtered_df["store_location"] == store]

filtered_df = filtered_df[
    (filtered_df["hour"] >= hour_range[0]) &
    (filtered_df["hour"] <= hour_range[1])
]

# ================= KPI CARDS =================
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["revenue"].sum()
total_transactions = filtered_df["transaction_id"].nunique()
total_qty = filtered_df["transaction_qty"].sum()
avg_order_value = total_revenue / total_transactions if total_transactions else 0

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Transactions", total_transactions)
col3.metric("Total Quantity Sold", total_qty)
col4.metric("Avg Order Value", f"₹{avg_order_value:,.2f}")

# ================= CHART ROW 1 =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Store Location")
    store_sales = filtered_df.groupby("store_location")["revenue"].sum()
    st.bar_chart(store_sales)

with col2:
    st.subheader("Revenue by Day of Week")
    day_sales = filtered_df.groupby("day_of_week")["revenue"].sum()
    st.bar_chart(day_sales)

# ================= CHART ROW 2 =================
col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by Hour")
    hour_sales = filtered_df.groupby("hour")["revenue"].sum()
    st.line_chart(hour_sales)

with col4:
    st.subheader("Revenue by Time of Day")
    time_sales = filtered_df.groupby("time_bucket")["revenue"].sum()
    st.bar_chart(time_sales)

# ================= TOP PRODUCTS =================
st.subheader("Top 10 Products by Revenue")

top_products = (
    filtered_df.groupby("product_type")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_products)

# ================= METRIC COMPARISON =================
st.subheader("Metric Comparison by Store")

metric_sales = filtered_df.groupby("store_location")[metric].sum()
st.bar_chart(metric_sales)

# ================= HEATMAP =================
st.subheader("Hourly Sales Heatmap (Day vs Hour)")

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

heatmap_data = filtered_df.pivot_table(
    values="revenue",
    index="day_of_week",
    columns="hour",
    aggfunc="sum"
)

# Force all days to show
heatmap_data = heatmap_data.reindex(day_order)

fig, ax = plt.subplots(figsize=(12,6))
sns.heatmap(
    heatmap_data,
    cmap="YlOrRd",
    ax=ax,
    linewidths=0.5,
    linecolor="white"
)

ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")

st.pyplot(fig)
