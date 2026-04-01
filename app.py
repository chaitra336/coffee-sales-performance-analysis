import streamlit as st
import pandas as pd
import plotly.express as px

# --------- PAGE CONFIG ----------
st.set_page_config(layout="wide", page_title="☕ Afficionado Coffee Roasters - Sales Analysis 2025")

# --------- CUSTOM CSS FOR THEME & KPI CARDS ----------
st.markdown("""
<style>
body {
    background-color: AliceBlue;
.block-container {
    padding: 1.5rem 2rem;
}
h1 {
    color: #1b4332;  /* dark green title */
    margin-bottom: 0.3rem;
}
h3 {
    color: #1b4332;
    margin-top: 1.5rem;
}
.kpi-row {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
}
.kpi-card {
    flex: 1;
    padding: 14px 22px;
    border-radius: 30px;
    background: linear-gradient(145deg, #d8f3dc, #b7e4c7);
    box-shadow: 3px 3px 10px rgba(0,0,0,0.07);
    text-align: center;
    min-width: 140px;
}
.kpi-title {
    font-size: 15px;
    color: #1b4332;
    font-weight: 600;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 22px;
    color: #081c15;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# --------- TITLE & SUBTITLE ----------
# --------- CENTERED DASHBOARD TITLE (WIDER) ----------
st.markdown(f"""
<div style="display: flex; justify-content: center; margin: 30px 0;">
    <div style="
        padding: 25px 40px;
        border-radius: 30px;
        background: linear-gradient(145deg, #d8f3dc, #b7e4c7);
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        width: 100%;  /* <-- make cylinder longer, adjust percentage as needed */
        max-width: 1000px; /* optional, prevents it from being too wide on large screens */
    ">
        <div style="font-size: 40px; color: #1b4332; font-weight: 700; margin-bottom: 5px;">
            ☕ Afficionado Coffee Roasters – Sales and Time-Based Performance Analysis
        </div>
        <div style="font-size: 16px; color: #1b4332; font-weight: 500;">
            Time-based sales insights across stores, days, and hours
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------- LOAD DATA ----------
df = pd.read_csv("transaction.csv")

# --------- DATA PREPARATION ----------
df['transaction_time'] = pd.to_datetime(df['transaction_time'])
df['hour'] = df['transaction_time'].dt.hour
df['day'] = df['transaction_time'].dt.day_name()
df['revenue'] = df['transaction_qty'] * df['unit_price']

# Time bucket helper function
def get_time_bucket(hour):
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 16:
        return "Afternoon"
    elif 17 <= hour <= 21:
        return "Evening"
    else:
        return "Late Night"
df['time_bucket'] = df['hour'].apply(get_time_bucket)

# --------- FILTERS ----------
st.markdown("### Filters")
col1, col2, col3 = st.columns(3)

with col1:
    store = st.selectbox("Store Location", sorted(df['store_location'].unique()))

with col2:
    day = st.selectbox("Day of Week", ['All'] + df['day'].unique().tolist())

with col3:
    hour_range = st.slider("Hour Range", 0, 23, (6, 21))

# Filter data based on selections
filtered_df = df[df['store_location'] == store]
if day != 'All':
    filtered_df = filtered_df[filtered_df['day'] == day]
filtered_df = filtered_df[filtered_df['hour'].between(hour_range[0], hour_range[1])]

# --------- KPI CARDS (small cylinders) ----------
total_revenue = filtered_df['revenue'].sum()
total_orders = len(filtered_df)
avg_order_value = filtered_df['revenue'].mean() if total_orders > 0 else 0

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-title">Total Revenue</div>
        <div class="kpi-value">${total_revenue:,.0f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Total Orders</div>
        <div class="kpi-value">{total_orders}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Order Value</div>
        <div class="kpi-value">${avg_order_value:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------- CHARTS (compact layout) ----------

# Row 1: Sales Trend & Day of Week Performance
col1, col2 = st.columns(2)

# Daily sales trend (line chart)
# Aggregate daily revenue
daily = df.groupby('day')['revenue'].sum().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
).reset_index()

# Clean daily data - remove NaNs and clip size for scatter
daily = daily.dropna(subset=['revenue'])
daily['size'] = daily['revenue'].clip(lower=1)

# Create scatter plot
fig1 = px.scatter(
    daily,
    x='day',
    y='revenue',
    size='size',
    title="Daily Sales Scatter",
    color='revenue',
    color_continuous_scale="Greens"
)
fig1.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col1.plotly_chart(fig1, use_container_width=True)  # assuming col1 is defined

# Sales by day of week (bar chart)
fig2 = px.bar(
    daily, x='day', y='revenue',
    title="Sales by Day of Week",
    color_discrete_sequence=["#40916c"]
)
fig2.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col2.plotly_chart(fig2, use_container_width=True)

# Row 2: Hourly Demand & Heatmap
col3, col4 = st.columns(2)

# Hourly demand (line)
hourly = df.groupby('hour')['revenue'].sum().reset_index()
fig3 = px.line(
    hourly, x='hour', y='revenue',
    title="Hourly Demand Pattern",
    color_discrete_sequence=["#2d6a4f"]
)
fig3.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col3.plotly_chart(fig3, use_container_width=True)

# Heatmap (day vs hour)
heatmap = df.pivot_table(values='revenue', index='day', columns='hour', aggfunc='sum').reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)
fig4 = px.imshow(
    heatmap,
    color_continuous_scale="Greens",
    title="Sales Heatmap (Day vs Hour)"
)
fig4.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col4.plotly_chart(fig4, use_container_width=True)

# Row 3: Store Comparison & Product Category Distribution
col5, col6 = st.columns(2)

# Store-wise hourly revenue comparison (multi-line)
store_comp = df.groupby(['store_location', 'hour'])['revenue'].sum().reset_index()
fig5 = px.line(
    store_comp,
    x='hour', y='revenue',
    color='store_location',
    title="Store-wise Hourly Revenue Comparison"
)
fig5.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col5.plotly_chart(fig5, use_container_width=True)

# Revenue distribution by product category (donut pie chart)
category = df.groupby('product_category')['revenue'].sum().reset_index()
fig6 = px.pie(
    category,
    values='revenue',
    names='product_category',
    hole=0.5,
    title="Revenue by Product Category",
    color_discrete_sequence=px.colors.sequential.Greens
)
fig6.update_layout(margin=dict(l=20,r=20,t=40,b=20), height=320)
col6.plotly_chart(fig6, use_container_width=True)

# --------- FOOTER ----------
st.markdown("---")
st.caption("Dashboard created for Afficionado Coffee Roasters | Internship Project")
