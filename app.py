import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("☕ Afficionado Coffee Roasters - Sales Dashboard")
# -------------------------
# LOAD + CLEAN DATA (FULL FIX)
# -------------------------
file_path = "coffee_sales_cleaned.csv"

df = pd.read_csv(
    file_path,
    sep=",",
    encoding="utf-8",
    engine="python",
    on_bad_lines="skip"
)

# clean column names
df.columns = df.columns.str.strip().str.lower()

# rename variants
df = df.rename(columns={
    "transaction time": "transaction_time",
    "transaction qty": "transaction_qty",
    "unit price": "unit_price",
    "store": "store_location",
    "product": "product_type"
})

# ensure columns exist
if "transaction_time" not in df.columns:
    df["transaction_time"] = pd.NaT

if "transaction_qty" not in df.columns:
    df["transaction_qty"] = 0

if "unit_price" not in df.columns:
    df["unit_price"] = 0

# convert types
df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
df["transaction_qty"] = pd.to_numeric(df["transaction_qty"], errors="coerce").fillna(0)
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)

# features
df["hour"] = df["transaction_time"].dt.hour.fillna(0)
df["day_of_week"] = df["transaction_time"].dt.day_name().fillna("Unknown")

# revenue
df["revenue"] = df["transaction_qty"] * df["unit_price"]

# time bucket
def time_bucket(hour):
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 16:
        return "Afternoon"
    elif 17 <= hour <= 21:
        return "Evening"
    else:
        return "Late Night"

df["time_bucket"] = df["hour"].apply(time_bucket)


# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filters")

store = st.sidebar.multiselect(
    "Select Store",
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

# -------------------------
# KPI SECTION
# -------------------------
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

# -------------------------
# REVENUE BY STORE
# -------------------------
st.subheader("Revenue by Store Location")
store_sales = filtered_df.groupby("store_location")[metric].sum()
st.bar_chart(store_sales)

# -------------------------
# REVENUE BY HOUR
# -------------------------
st.subheader("Revenue by Hour")
hour_sales = filtered_df.groupby("hour")[metric].sum()
st.line_chart(hour_sales)

# -------------------------
# TIME BUCKET
# -------------------------
st.subheader("Revenue by Time of Day")
time_sales = filtered_df.groupby("time_bucket")[metric].sum()
st.bar_chart(time_sales)

# -------------------------
# TOP PRODUCTS
# -------------------------
st.subheader("Top 10 Products by Revenue")
top_products = (
    filtered_df.groupby("product_type")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_products)

# -------------------------
# DAY OF WEEK
# -------------------------
st.subheader("Revenue by Day of Week")
day_sales = filtered_df.groupby("day_of_week")[metric].sum()
st.bar_chart(day_sales)

# -------------------------
# HEATMAP
# -------------------------
st.subheader("Hourly Sales Heatmap (Day vs Hour)")

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
