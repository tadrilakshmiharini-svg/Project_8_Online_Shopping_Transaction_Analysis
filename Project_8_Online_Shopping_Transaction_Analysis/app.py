
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============== PAGE SETTINGS ==============
st.set_page_config(
    page_title="ShopAnalytics",
    page_icon="🛒",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# ============== LIGHT THEME DESIGN ==============
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f3f7ff, #ffffff, #eef4ff);
    color: #172554;
}

[data-testid="stHeader"] {
    background: rgba(255,255,255,0.92);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff, #f2edff);
    border-right: 1px solid #e0e7ff;
}

h1, h2, h3 {
    color: #172554 !important;
}

p, label, [data-testid="stMarkdownContainer"] {
    color: #334155;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #eaf2ff);
    border: 1px solid #d6e4ff;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 5px 18px #64748b18;
}

div[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

div[data-testid="stMetricValue"] {
    color: #1d4ed8 !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #dbe4f0;
    border-radius: 12px;
}

div[data-testid="stDownloadButton"] button {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
}

hr {
    border-color: #dbe4f0;
}
</style>
""", unsafe_allow_html=True)

# ============== LOAD REPORTS ==============
@st.cache_data
def load_csv(filename):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()

orders = load_csv("transaction_summary.csv")
status_report = load_csv("order_status_report.csv")
payments_report = load_csv("payment_method_report.csv")
products = load_csv("product_quantity_report.csv")
monthly = load_csv("monthly_order_volume.csv")

# ============== SIDEBAR ==============
st.sidebar.markdown("# 🛒 ShopAnalytics")
st.sidebar.caption("✨ Online Shopping Analysis")
st.sidebar.divider()

page = st.sidebar.radio(
    "📍 NAVIGATION",
    [
        "🏠 Dashboard",
        "🧾 Orders",
        "🏆 Products",
        "📁 Reports"
    ]
)



# ============== HEADER ==============
st.title("🛍️ Online Shopping Transaction Analysis")
st.subheader("✨ Monitor orders, revenue, payments and product performance")

if orders.empty:
    st.error("⚠️ No transaction data found. Please run python main.py first.")
    st.stop()

orders = orders.copy()

# Prepare date and amount columns
if "order_date" in orders.columns:
    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

amount_col = next(
    (
        col for col in ["order_value", "total_amount", "amount"]
        if col in orders.columns
    ),
    None
)

if amount_col:
    orders[amount_col] = pd.to_numeric(
        orders[amount_col], errors="coerce"
    ).fillna(0)

# Exclude cancelled and refunded transactions from realized revenue
if "order_status" in orders.columns:
    eligible = ~orders["order_status"].astype(str).str.lower().isin(
        ["cancelled", "refunded"]
    )
else:
    eligible = pd.Series(True, index=orders.index)

total_orders = len(orders)
eligible_orders = int(eligible.sum())

revenue = (
    orders.loc[eligible, amount_col].sum()
    if amount_col else 0
)

average_order_value = (
    revenue / eligible_orders if eligible_orders else 0
)

product_count = (
    products["product_name"].nunique()
    if "product_name" in products.columns else 0
)

# Colour palette
COLORS = [
    "#3987FF",
    "#19CFA5",
    "#FFB938",
    "#FF5C93",
    "#A56BFF",
    "#FF8057"
]

# ============== DASHBOARD ==============
if page == "🏠 Dashboard":

    st.markdown("## 📊 Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🧾 Total Orders", f"{total_orders:,}")
    col2.metric("💰 Realized Revenue", f"₹{revenue:,.2f}")
    col3.metric("📦 Eligible Orders", f"{eligible_orders:,}")
    col4.metric("🏷️ Products Analyzed", f"{product_count:,}")

    st.caption(
        f"Average order value: ₹{average_order_value:,.2f} | "
        "Cancelled and refunded orders are excluded from realized revenue."
    )

    st.divider()

    # Three colourful charts
    chart1, chart2, chart3 = st.columns(3)

    with chart1:
        st.markdown("### 📦 Orders by Status")

        if "order_status" in orders.columns:
            status_data = (
                orders["order_status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Orders")
                .sort_values("Orders")
            )

            fig = px.bar(
                status_data,
                x="Orders",
                y="Status",
                orientation="h",
                color="Status",
                text="Orders",
                color_discrete_sequence=COLORS,
                template="plotly_white"
            )

            fig.update_layout(
                showlegend=False,
                height=370,
                margin=dict(l=5, r=15, t=15, b=10),
                xaxis_title="Number of Orders",
                yaxis_title="",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, width="stretch")

    with chart2:
        st.markdown("### 💳 Payment Methods")

        if "payment_method" in orders.columns:
            payment_data = (
                orders["payment_method"]
                .value_counts()
                .rename_axis("Payment Method")
                .reset_index(name="Orders")
            )

            fig = px.pie(
                payment_data,
                names="Payment Method",
                values="Orders",
                hole=0.58,
                color_discrete_sequence=COLORS,
                template="plotly_white"
            )

            fig.update_traces(
                textinfo="percent",
                textposition="inside"
            )

            fig.update_layout(
                height=370,
                margin=dict(l=5, r=5, t=15, b=10),
                paper_bgcolor="rgba(255,255,255,0)",
                legend=dict(orientation="h", y=-0.18)
            )
            st.plotly_chart(fig, width="stretch")

    with chart3:
        st.markdown("### 🏆 Best-Selling Products")

        if not products.empty and {
            "product_name", "units_sold"
        }.issubset(products.columns):

            product_data = products.copy()
            product_data["units_sold"] = pd.to_numeric(
                product_data["units_sold"], errors="coerce"
            ).fillna(0)

            product_data = product_data.sort_values("units_sold")

            fig = px.bar(
                product_data,
                x="units_sold",
                y="product_name",
                orientation="h",
                text="units_sold",
                color="product_name",
                color_discrete_sequence=COLORS,
                template="plotly_white"
            )

            fig.update_layout(
                showlegend=False,
                height=370,
                margin=dict(l=5, r=15, t=15, b=10),
                xaxis_title="Units Sold",
                yaxis_title="",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)"
            )

            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    # Monthly chart and quick insights
    monthly_col, insights_col = st.columns([2, 1])

    with monthly_col:
        st.markdown("### 📅 Monthly Order Volume")

        if not monthly.empty and {
            "month", "order_count"
        }.issubset(monthly.columns):

            monthly_data = monthly.copy()
            monthly_data["order_count"] = pd.to_numeric(
                monthly_data["order_count"], errors="coerce"
            ).fillna(0)

            fig = px.bar(
                monthly_data,
                x="month",
                y="order_count",
                text="order_count",
                color="order_count",
                color_continuous_scale=["#A9D8FF", "#3987FF"],
                template="plotly_white"
            )

            fig.update_layout(
                height=320,
                coloraxis_showscale=False,
                xaxis_title="Month",
                yaxis_title="Number of Orders",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)"
            )

            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Monthly order report is not available.")

    with insights_col:
        st.markdown("### 💡 Quick Insights")

        if "order_status" in orders.columns:
            status_counts = orders["order_status"].value_counts()
            if not status_counts.empty:
                st.success(
                    f"📦 Most common status: **{status_counts.index[0]}** "
                    f"({status_counts.iloc[0]} orders)"
                )

        if "payment_method" in orders.columns:
            payment_counts = orders["payment_method"].value_counts()
            if not payment_counts.empty:
                st.info(
                    f"💳 Most used payment method: **{payment_counts.index[0]}**"
                )

        if not products.empty and "units_sold" in products.columns:
            product_data = products.copy()
            product_data["units_sold"] = pd.to_numeric(
                product_data["units_sold"], errors="coerce"
            ).fillna(0)

            if not product_data.empty:
                best = product_data.loc[
                    product_data["units_sold"].idxmax()
                ]
                st.warning(
                    f"🏆 Top product: **{best['product_name']}** "
                    f"({int(best['units_sold'])} units)"
                )

        st.markdown(
            "✨ Explore the other sections to filter transactions "
            "and download reports."
        )

# ============== ORDERS PAGE ==============
elif page == "🧾 Orders":

    st.markdown("## 🧾 Transaction Explorer")

    filtered = orders.copy()

    if "order_status" in filtered.columns:
        statuses = sorted(filtered["order_status"].dropna().unique())

        chosen_statuses = st.multiselect(
            "📦 Filter by order status",
            statuses,
            default=statuses
        )

        filtered = filtered[
            filtered["order_status"].isin(chosen_statuses)
        ]

    if "payment_method" in filtered.columns:
        methods = sorted(filtered["payment_method"].dropna().unique())

        chosen_methods = st.multiselect(
            "💳 Filter by payment method",
            methods,
            default=methods
        )

        filtered = filtered[
            filtered["payment_method"].isin(chosen_methods)
        ]

    search = st.text_input("🔎 Search orders")

    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(
                search, case=False, na=False
            )
        ).any(axis=1)

        filtered = filtered[mask]

    st.metric("🧾 Matching Orders", len(filtered))

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Filtered Orders",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_orders.csv",
        mime="text/csv"
    )

# ============== PRODUCTS PAGE ==============
elif page == "🏆 Products":

    st.markdown("## 🏆 Product Performance")

    if products.empty:
        st.warning("Product report not found.")
    else:
        data = products.copy()

        if "category" in data.columns:
            categories = sorted(data["category"].dropna().unique())

            chosen_categories = st.multiselect(
                "🗂️ Select product categories",
                categories,
                default=categories
            )

            data = data[data["category"].isin(chosen_categories)]

        if "units_sold" in data.columns:
            data["units_sold"] = pd.to_numeric(
                data["units_sold"], errors="coerce"
            ).fillna(0)

            fig = px.bar(
                data.sort_values("units_sold"),
                x="units_sold",
                y="product_name",
                orientation="h",
                text="units_sold",
                color="product_name",
                color_discrete_sequence=COLORS,
                template="plotly_white"
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Units Sold",
                yaxis_title="",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)"
            )

            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, width="stretch")

        if "item_revenue" in data.columns:
            data["item_revenue"] = pd.to_numeric(
                data["item_revenue"], errors="coerce"
            ).fillna(0)

            st.markdown("### 💰 Revenue by Product")

            fig = px.bar(
                data.sort_values("item_revenue"),
                x="item_revenue",
                y="product_name",
                orientation="h",
                text="item_revenue",
                color="product_name",
                color_discrete_sequence=COLORS,
                template="plotly_white"
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Item Revenue (₹)",
                yaxis_title="",
                paper_bgcolor="rgba(255,255,255,0)",
                plot_bgcolor="rgba(255,255,255,0)"
            )

            st.plotly_chart(fig, width="stretch")

        st.dataframe(
            data,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Product Report",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name="product_report.csv",
            mime="text/csv"
        )

# ============== REPORTS PAGE ==============
elif page == "📁 Reports":

    st.markdown("## 📁 Reports Centre")
    st.write("Preview and download the generated CSV reports below.")

    reports = {
        "🧾 Transaction Summary": "transaction_summary.csv",
        "📦 Order Status": "order_status_report.csv",
        "💳 Payment Methods": "payment_method_report.csv",
        "🏆 Product Quantities": "product_quantity_report.csv",
        "📅 Monthly Order Volume": "monthly_order_volume.csv"
    }

    for title, filename in reports.items():
        data = load_csv(filename)

        with st.expander(title):
            if data.empty:
                st.warning("Report file not found.")
            else:
                st.dataframe(
                    data,
                    width="stretch",
                    hide_index=True
                )

                st.download_button(
                    f"⬇️ Download {title}",
                    data=data.to_csv(index=False).encode("utf-8"),
                    file_name=filename,
                    mime="text/csv",
                    key=filename
                )

# ============== FOOTER ==============
st.divider()
st.caption(
    "🛒 ShopAnalytics | Made with Python, Pandas, Plotly and Streamlit"
)
