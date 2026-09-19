import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Geetanagar Dark Store Hub Analytics",
    page_icon="📦",
    layout="wide"
)

# Load CSV Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("bb.csv")
    # Clean column names
    df.columns = [c.replace('Ã¯Â»Â¿', '').strip() for c in df.columns]
    return df

try:
    df = load_data()

    # Header Section
    st.title("📦 Quick-Commerce Dark Store Operations & Analytics")
    st.caption("Live Operational Intelligence Engine | Hub: Guw_121_Geetanagar (Flipkart Minutes)")

    # Sidebar Filters
    st.sidebar.header("🎯 Dashboard Filters")
    
    # Filter by Vehicle Type
    vehicles = ["All"] + list(df["Vehicle Category"].dropna().unique())
    selected_vehicle = st.sidebar.selectbox("Filter by Vehicle Type", vehicles)
    
    # Filter by Order Status
    statuses = ["All"] + list(df["Order Status"].dropna().unique())
    selected_status = st.sidebar.selectbox("Filter by Order Status", statuses)

    # Filter Dataframe
    filtered_df = df.copy()
    if selected_vehicle != "All":
        filtered_df = filtered_df[filtered_df["Vehicle Category"] == selected_vehicle]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["Order Status"] == selected_status]

    # Executive KPI Summary Cards
    st.markdown("### 📈 Key Operational Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_orders = len(filtered_df)
    delivered = len(filtered_df[filtered_df["Order Status"] == "delivered"])
    fulfillment_rate = (delivered / total_orders * 100) if total_orders > 0 else 0
    total_cash = filtered_df["Cash Collected"].sum()
    total_dist = filtered_df["Delivery Distance Travelled (km)"].sum()
    active_riders = filtered_df["(Rider Name)"].nunique()

    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Fulfillment Rate", f"{fulfillment_rate:.1f}%")
    col3.metric("Total COD Cash", f"₹{total_cash:,.2f}")
    col4.metric("Total Distance", f"{total_dist:,.1f} km")
    col5.metric("Active Riders", f"{active_riders}")

    st.divider()

    # Analytics Charts Row 1
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("🛵 Delivery Fleet Distribution")
        vehicle_counts = filtered_df["Vehicle Category"].value_counts().reset_index()
        vehicle_counts.columns = ["Vehicle Type", "Orders Handled"]
        fig_vehicle = px.pie(
            vehicle_counts, 
            values="Orders Handled", 
            names="Vehicle Type", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_vehicle, use_container_width=True)

    with col_chart2:
        st.subheader("💳 Payment Mode Split (UPI vs Cash)")
        pay_counts = filtered_df["Payment Mode"].value_counts(dropna=False).reset_index()
        pay_counts.columns = ["Payment Mode", "Count"]
        pay_counts["Payment Mode"] = pay_counts["Payment Mode"].fillna("Prepaid / Online")
        fig_pay = px.bar(
            pay_counts, 
            x="Payment Mode", 
            y="Count", 
            color="Payment Mode",
            text="Count"
        )
        st.plotly_chart(fig_pay, use_container_width=True)

    st.divider()

    # Analytics Charts Row 2
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.subheader("🏆 Top 10 Delivery Riders (Wishmasters)")
        rider_performance = filtered_df[filtered_df["Order Status"] == "delivered"]["(Rider Name)"].value_counts().head(10).reset_index()
        rider_performance.columns = ["Rider Name", "Successful Deliveries"]
        fig_rider = px.bar(
            rider_performance, 
            x="Successful Deliveries", 
            y="Rider Name", 
            orientation="h",
            color="Successful Deliveries",
            color_continuous_scale="Viridis"
        )
        fig_rider.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_rider, use_container_width=True)

    with col_chart4:
        st.subheader("🚨 Non-Delivery Reasons (NDR Root Cause)")
        ndr_df = filtered_df["(NDR Reason)"].dropna().value_counts().reset_index()
        ndr_df.columns = ["Reason", "Count"]
        if not ndr_df.empty:
            fig_ndr = px.bar(
                ndr_df, 
                x="Reason", 
                y="Count", 
                color="Count", 
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_ndr, use_container_width=True)
        else:
            st.info("No Non-Delivery Reason exceptions in selected filter.")

    st.divider()

    # Cash Reconciliation & Raw Data Table
    st.subheader("💰 Rider Cash Reconciliation Log")
    rider_cash = filtered_df.groupby("(Rider Name)")["Cash Collected"].sum().reset_index()
    rider_cash.columns = ["Rider Name", "Total COD Cash Collected (₹)"]
    rider_cash = rider_cash[rider_cash["Total COD Cash Collected (₹)"] > 0].sort_values(by="Total COD Cash Collected (₹)", ascending=False)
    
    st.dataframe(rider_cash, use_container_width=True)

except Exception as e:
    st.error(f"Error loading dataset: {e}")
