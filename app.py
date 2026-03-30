import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Coffee Sales Dashboard", layout="wide")

st.title("Afficionado Coffee Roasters - Sales Trend Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("coffee_sales_cleaned.csv")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert time column safely
    df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")

    # Feature engineering
    df["hour"] = df["transaction_time"].dt.hour
    df["day_of_week"] = df["transaction_time"].dt.day_name()

    df["revenue"] = df["transaction_qty"] * df["unit_price"]

    # Time bucket
    def bucket(x):
        if 6 <= x <= 11:
            return "Morning"
        elif 12 <= x <= 16:
            return "Afternoon"
        elif 17 <= x <= 21:
            return "Evening"
        else:
            return "Late Night"

    df["time_bucket"] = df["hour"].apply(bucket)

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

store = st.sidebar.multiselect(
    "Select Store Location",
    df["store_location"].unique(),
    default=df["store_location"].unique()
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["revenue", "transaction_qty"]
)

hour_range = st.sidebar.slider(
    "Select Hour Range",
    0, 23, (6, 20)
)

filtered_df = df[
    (df["store_location"].isin(store)) &
    (df["hour"] >= hour_range[0]) &
    (df["hour"] <= hour_range[1])
]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["revenue"].sum()
col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")

total_transactions = filtered_df["transaction_id"].nunique()
col2.metric("Total Transactions", total_transactions)

total_qty = filtered_df["transaction_qty"].sum()
col3.metric("Total Quantity Sold", total_qty)

avg_order_value = total_revenue / total_transactions
col4.metric("Avg Order Value", f"₹{avg_order_value:,.2f}")

# -----------------------------
# CHARTS
# -----------------------------
st.subheader("Revenue by Store Location")
store_sales = filtered_df.groupby("store_location")["revenue"].sum()
st.bar_chart(store_sales)

st.subheader("Revenue by Hour")
hour_sales = filtered_df.groupby("hour")["revenue"].sum()
st.line_chart(hour_sales)

st.subheader("Revenue by Time of Day")
time_sales = filtered_df.groupby("time_bucket")["revenue"].sum()
st.bar_chart(time_sales)

st.subheader("Top 10 Products by Revenue")
top_products = (
    filtered_df.groupby("product_type")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_products)

st.subheader("Revenue by Day of Week")
day_sales = filtered_df.groupby("day_of_week")["revenue"].sum()
st.bar_chart(day_sales)

st.subheader("Metric Comparison by Store")
metric_sales = filtered_df.groupby("store_location")[metric].sum()
st.bar_chart(metric_sales)

# -----------------------------
# HEATMAP
# -----------------------------
st.subheader("Hourly Sales Heatmap")

heatmap_data = filtered_df.pivot_table(
    values="revenue",
    index="day_of_week",
    columns="hour",
    aggfunc="sum"
)

fig, ax = plt.subplots()
ax.imshow(heatmap_data)

ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns)

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

st.pyplot(fig)
