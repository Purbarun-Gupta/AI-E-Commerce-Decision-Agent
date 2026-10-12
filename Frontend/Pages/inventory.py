
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Inventory | CommerceAI",
    page_icon="📦",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "assets" / "style.css"
if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

df = pd.DataFrame([
    {"Product": "Smart Watch", "SKU": "ELEC-001", "Category": "Wearables", "Stock": 42, "Reorder Level": 20, "Unit Price": 4500},
    {"Product": "USB-C Cable", "SKU": "ACC-002", "Category": "Accessories", "Stock": 68, "Reorder Level": 25, "Unit Price": 350},
    {"Product": "Smartphone", "SKU": "ELEC-003", "Category": "Mobiles", "Stock": 31, "Reorder Level": 15, "Unit Price": 24999},
    {"Product": "Laptop Stand", "SKU": "ACC-004", "Category": "Accessories", "Stock": 55, "Reorder Level": 20, "Unit Price": 1200},
    {"Product": "HDMI Cable", "SKU": "ACC-005", "Category": "Accessories", "Stock": 19, "Reorder Level": 20, "Unit Price": 500},
    {"Product": "Webcam", "SKU": "ELEC-006", "Category": "Electronics", "Stock": 14, "Reorder Level": 18, "Unit Price": 2200},
])


def stock_status(row):
    if row["Stock"] <= 0:
        return "Out of stock"
    if row["Stock"] <= row["Reorder Level"]:
        return "Reorder"
    if row["Stock"] <= row["Reorder Level"] * 1.5:
        return "Monitor"
    return "Healthy"


df["Status"] = df.apply(stock_status, axis=1)
df["Stock Value"] = df["Stock"] * df["Unit Price"]

st.markdown(
    """
    <div class="page-header">
        <div>
            <div class="page-kicker">INVENTORY INTELLIGENCE</div>
            <h1 class="page-title">Inventory Overview</h1>
            <p class="page-description">
                Monitor stock levels and identify replenishment risks.
            </p>
        </div>
        <div class="page-header-icon">📦</div>
    </div>
    """,
    unsafe_allow_html=True,
)

total_value = df["Stock Value"].sum()
reorder_count = int(df["Status"].isin(["Reorder", "Out of stock"]).sum())
monitor_count = int((df["Status"] == "Monitor").sum())

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "TOTAL PRODUCTS", f"{len(df)}", "Products listed"),
    (k2, "REORDER REQUIRED", str(reorder_count), "At/below reorder level"),
    (k3, "STOCK TO MONITOR", str(monitor_count), "Approaching threshold"),
    (k4, "INVENTORY VALUE", f"₹{total_value:,.0f}", "Listed stock value"),
]

for col, label, value, note in kpis:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("## Product inventory")

f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    search = st.text_input("Search product or SKU", key="inv_search")
with f2:
    category = st.selectbox(
        "Category",
        ["All categories"] + sorted(df["Category"].unique().tolist()),
    )
with f3:
    status = st.selectbox(
        "Status",
        ["All statuses", "Healthy", "Monitor", "Reorder", "Out of stock"],
    )

filtered = df.copy()

if search.strip():
    term = search.strip()
    filtered = filtered[
        filtered["Product"].str.contains(term, case=False, na=False)
        | filtered["SKU"].str.contains(term, case=False, na=False)
    ]

if category != "All categories":
    filtered = filtered[filtered["Category"] == category]

if status != "All statuses":
    filtered = filtered[filtered["Status"] == status]

st.caption(f"Showing {len(filtered)} of {len(df)} products")

display = filtered.copy()
display["Unit Price"] = display["Unit Price"].map(lambda x: f"₹{x:,.0f}")
display["Stock Value"] = display["Stock Value"].map(lambda x: f"₹{x:,.0f}")

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Stock": st.column_config.NumberColumn("Stock", format="%d units"),
        "Reorder Level": st.column_config.NumberColumn(
            "Reorder level", format="%d units"
        ),
    },
)

st.markdown("## Reorder recommendations")
reorder = df[df["Status"].isin(["Reorder", "Out of stock"])]

if reorder.empty:
    st.success("No products currently require replenishment.")
else:
    for _, row in reorder.iterrows():
        suggested = max(
            int(row["Reorder Level"]) * 2 - int(row["Stock"]),
            int(row["Reorder Level"]),
        )
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{row['Product']}**")
                st.caption(
                    f"{row['SKU']} · {row['Category']} · {row['Status']}"
                )
            with col2:
                st.metric("Current stock", f"{int(row['Stock'])} units")
            with col3:
                st.metric("Suggested top-up", f"{suggested} units")
