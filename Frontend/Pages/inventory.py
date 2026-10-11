
import streamlit as st
from pathlib import Path
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Inventory | CommerceAI",
    page_icon="📦",
    layout="wide",
)


# ============================================================
# LOAD CSS
# ============================================================

def load_css():
    css_path = (
        Path(__file__).parent.parent
        / "assets"
        / "style.css"
    )

    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )


load_css()


# ============================================================
# SAMPLE INVENTORY DATA
# Replace with database/API data when connected.
# ============================================================

inventory_df = pd.DataFrame(
    [
        {"Product": "Smart Watch", "SKU": "ELEC-001", "Category": "Wearables", "Stock": 42, "Reorder Level": 20, "Unit Price": 4500},
        {"Product": "USB-C Cable", "SKU": "ACC-002", "Category": "Accessories", "Stock": 68, "Reorder Level": 25, "Unit Price": 350},
        {"Product": "Smartphone", "SKU": "ELEC-003", "Category": "Mobiles", "Stock": 31, "Reorder Level": 15, "Unit Price": 24999},
        {"Product": "Laptop Stand", "SKU": "ACC-004", "Category": "Accessories", "Stock": 55, "Reorder Level": 20, "Unit Price": 1200},
        {"Product": "HDMI Cable", "SKU": "ACC-005", "Category": "Accessories", "Stock": 19, "Reorder Level": 20, "Unit Price": 500},
        {"Product": "Webcam", "SKU": "ELEC-006", "Category": "Electronics", "Stock": 14, "Reorder Level": 18, "Unit Price": 2200},
    ]
)


def get_stock_status(row):
    if row["Stock"] <= 0:
        return "Out of stock"
    if row["Stock"] <= row["Reorder Level"]:
        return "Reorder"
    if row["Stock"] <= row["Reorder Level"] * 1.5:
        return "Monitor"
    return "Healthy"


inventory_df["Status"] = inventory_df.apply(
    get_stock_status,
    axis=1,
)

inventory_df["Stock Value"] = (
    inventory_df["Stock"] * inventory_df["Unit Price"]
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="inventory-page-header">
        <div>
            <div class="inventory-eyebrow">
                INVENTORY INTELLIGENCE
            </div>
            <h1>Inventory Overview</h1>
            <p>
                Monitor stock levels, identify supply risks,
                and make smarter replenishment decisions.
            </p>
        </div>
        <div class="inventory-header-icon">📦</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI METRICS
# ============================================================

total_products = len(inventory_df)
low_stock = int(
    inventory_df["Status"].isin(["Reorder", "Out of stock"]).sum()
)
monitor_stock = int(
    (inventory_df["Status"] == "Monitor").sum()
)
inventory_value = inventory_df["Stock Value"].sum()


def format_inr(value):
    if value >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    if value >= 1000:
        return f"₹{value / 1000:.1f}K"
    return f"₹{value:,.0f}"


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpis = [
    (
        kpi1,
        "TOTAL PRODUCTS",
        f"{total_products}",
        "Products in this sample",
        "neutral",
        "▦",
    ),
    (
        kpi2,
        "REORDER REQUIRED",
        f"{low_stock}",
        "At or below reorder level",
        "danger" if low_stock else "good",
        "!",
    ),
    (
        kpi3,
        "STOCK TO MONITOR",
        f"{monitor_stock}",
        "Approaching reorder level",
        "warning" if monitor_stock else "good",
        "◷",
    ),
    (
        kpi4,
        "INVENTORY VALUE",
        format_inr(inventory_value),
        "Value of listed stock",
        "neutral",
        "₹",
    ),
]

for col, label, value, note, tone, icon in kpis:
    with col:
        st.markdown(
            f"""
            <div class="inventory-kpi-card">
                <div class="inventory-kpi-top">
                    <span class="inventory-kpi-label">{label}</span>
                    <span class="inventory-kpi-icon {tone}">{icon}</span>
                </div>
                <div class="inventory-kpi-value">{value}</div>
                <div class="inventory-kpi-note">
                    <span class="kpi-status-dot {tone}"></span>
                    {note}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# INVENTORY TABLE
# ============================================================

st.markdown(
    """
    <div class="inventory-section-heading">
        <div>
            <div class="inventory-eyebrow">STOCK MONITORING</div>
            <h2>Product inventory</h2>
            <p>
                Search products and inspect current stock,
                reorder thresholds, and stock value.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


filter1, filter2, filter3 = st.columns([2, 1.2, 1.2])

with filter1:
    search_term = st.text_input(
        "Search inventory",
        placeholder="Search product name or SKU...",
        key="inventory_search",
    )

with filter2:
    categories = ["All categories"] + sorted(
        inventory_df["Category"].unique().tolist()
    )
    selected_category = st.selectbox(
        "Category",
        categories,
        key="inventory_category",
    )

with filter3:
    statuses = ["All statuses"] + [
        "Healthy",
        "Monitor",
        "Reorder",
        "Out of stock",
    ]
    selected_status = st.selectbox(
        "Stock status",
        statuses,
        key="inventory_status",
    )


filtered_df = inventory_df.copy()

if search_term.strip():
    term = search_term.strip()
    mask = (
        filtered_df["Product"].str.contains(
            term, case=False, na=False
        )
        | filtered_df["SKU"].str.contains(
            term, case=False, na=False
        )
    )
    filtered_df = filtered_df[mask]

if selected_category != "All categories":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]

if selected_status != "All statuses":
    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]


st.markdown(
    f"""
    <div class="inventory-table-summary">
        <span>Showing <strong>{len(filtered_df)}</strong>
        of <strong>{len(inventory_df)}</strong> listed products</span>
        <span class="inventory-table-legend">
            <span class="legend-dot healthy-dot"></span> Healthy
            <span class="legend-dot monitor-dot"></span> Monitor
            <span class="legend-dot risk-dot"></span> Reorder
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


display_df = filtered_df[
    [
        "Product",
        "SKU",
        "Category",
        "Stock",
        "Reorder Level",
        "Status",
        "Stock Value",
    ]
].copy()

display_df["Stock Value"] = display_df["Stock Value"].map(
    lambda value: f"₹{value:,.0f}"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=300,
    column_config={
        "Product": st.column_config.TextColumn(
            "Product name",
            width="medium",
        ),
        "SKU": st.column_config.TextColumn(
            "SKU",
            width="small",
        ),
        "Category": st.column_config.TextColumn(
            "Category",
            width="medium",
        ),
        "Stock": st.column_config.NumberColumn(
            "Available stock",
            format="%d units",
        ),
        "Reorder Level": st.column_config.NumberColumn(
            "Reorder threshold",
            format="%d units",
        ),
        "Status": st.column_config.TextColumn(
            "Stock status",
            width="small",
        ),
        "Stock Value": st.column_config.TextColumn(
            "Stock value",
            width="small",
        ),
    },
)


# ============================================================
# STOCK HEALTH AND RISK
# ============================================================

st.markdown(
    """
    <div class="inventory-section-heading">
        <div>
            <div class="inventory-eyebrow">INVENTORY HEALTH</div>
            <h2>Stock health summary</h2>
            <p>A quick view of stock conditions in the listed products.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


healthy_count = int(
    (inventory_df["Status"] == "Healthy").sum()
)
monitor_count = int(
    (inventory_df["Status"] == "Monitor").sum()
)
risk_count = int(
    inventory_df["Status"].isin(["Reorder", "Out of stock"]).sum()
)

health_col, risk_col = st.columns(2)

with health_col:
    st.markdown(
        f"""
        <div class="inventory-insight-card health-insight">
            <div class="insight-icon">✓</div>
            <div class="insight-content">
                <div class="insight-kicker">STOCK HEALTH</div>
                <div class="insight-title">Inventory position</div>
                <div class="insight-description">
                    {healthy_count} products have stock comfortably
                    above their reorder threshold.
                </div>
                <div class="insight-bottom">
                    <span class="insight-number">{healthy_count}</span>
                    <span>healthy products</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with risk_col:
    st.markdown(
        f"""
        <div class="inventory-insight-card risk-insight">
            <div class="insight-icon">!</div>
            <div class="insight-content">
                <div class="insight-kicker">REPLENISHMENT RISK</div>
                <div class="insight-title">Products needing attention</div>
                <div class="insight-description">
                    {risk_count} products are at or below their
                    configured reorder threshold.
                </div>
                <div class="insight-bottom">
                    <span class="insight-number">{risk_count}</span>
                    <span>products to review</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# REORDER RECOMMENDATIONS
# ============================================================

st.markdown(
    """
    <div class="inventory-section-heading">
        <div>
            <div class="inventory-eyebrow">REPLENISHMENT PLANNING</div>
            <h2>Reorder recommendations</h2>
            <p>
                Products at or below their configured reorder threshold.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


reorder_df = inventory_df[
    inventory_df["Status"].isin(["Reorder", "Out of stock"])
].copy()

if reorder_df.empty:
    st.success(
        "No listed products currently require replenishment."
    )
else:
    for _, item in reorder_df.iterrows():
        stock = int(item["Stock"])
        reorder_level = int(item["Reorder Level"])
        suggested_qty = max(reorder_level * 2 - stock, reorder_level)

        st.markdown(
            f"""
            <div class="inventory-recommendation-card">
                <div class="recommendation-symbol">↻</div>
                <div class="recommendation-main">
                    <div class="recommendation-product">
                        {item["Product"]}
                    </div>
                    <div class="recommendation-meta">
                        SKU {item["SKU"]} · {item["Category"]}
                    </div>
                    <div class="recommendation-reason">
                        Current stock is {stock} units, at or below
                        the reorder threshold of {reorder_level} units.
                    </div>
                </div>
                <div class="recommendation-stock">
                    <span>STOCK</span>
                    <strong>{stock}</strong>
                    <small>units</small>
                </div>
                <div class="recommendation-quantity">
                    <span>SUGGESTED TOP-UP</span>
                    <strong>{suggested_qty}</strong>
                    <small>units · indicative</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="inventory-footer">
        <span class="inventory-footer-brand">CommerceAI</span>
        <span class="inventory-footer-dot">•</span>
        <span>Inventory Intelligence</span>
    </div>
    """,
    unsafe_allow_html=True,
)
