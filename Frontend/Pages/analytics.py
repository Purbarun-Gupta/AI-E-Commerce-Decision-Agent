
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Analytics | CommerceAI",
    page_icon="📊",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "assets" / "style.css"
if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="page-header">
        <div>
            <div class="page-kicker">BUSINESS INTELLIGENCE</div>
            <h1 class="page-title">Analytics Overview</h1>
            <p class="page-description">
                Understand revenue, orders, and product performance.
            </p>
        </div>
        <div class="page-header-icon">📊</div>
    </div>
    """,
    unsafe_allow_html=True,
)

kpis = [
    ("TOTAL REVENUE", "₹12.35M", "Sample revenue"),
    ("TOTAL ORDERS", "50", "Sample order volume"),
    ("AVERAGE ORDER VALUE", "₹246.9K", "Revenue per order"),
    ("TOTAL PROFIT", "₹1.84M", "Sample profit"),
]

cols = st.columns(4)
for col, (label, value, note) in zip(cols, kpis):
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

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
revenue = [1.42, 1.65, 1.82, 1.95, 2.31, 2.67]
orders = [6, 8, 7, 9, 10, 10]

c1, c2 = st.columns([1.7, 1])

with c1:
    st.markdown("### Revenue performance")
    st.caption("Monthly revenue movement · sample data")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=revenue,
            mode="lines+markers",
            line=dict(width=3, color="#2563eb"),
            marker=dict(size=7, color="#2563eb"),
            fill="tozeroy",
            fillcolor="rgba(37,99,235,0.10)",
        )
    )
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#526078"),
        xaxis=dict(showgrid=False),
        yaxis=dict(title="Revenue (₹M)", gridcolor="#e5eaf1"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### Order activity")
    st.caption("Monthly order volume · sample data")
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=months,
            y=orders,
            marker_color="#3b82f6",
        )
    )
    fig2.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#526078"),
        xaxis=dict(showgrid=False),
        yaxis=dict(title="Orders", gridcolor="#e5eaf1"),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("## Top performing products")
products = pd.DataFrame({
    "Product": [
        "Smart Watch", "USB-C Cable", "Smartphone",
        "Laptop Stand", "HDMI Cable",
    ],
    "Units Sold": [28, 27, 26, 23, 23],
})
st.dataframe(products, use_container_width=True, hide_index=True)

st.markdown("## Category performance")
category_df = pd.DataFrame({
    "Category": ["Accessories", "Computers", "Electronics"],
    "Revenue": [5187386, 4271033, 2887490],
})
fig3 = go.Figure(
    go.Bar(
        x=category_df["Category"],
        y=category_df["Revenue"],
        marker_color="#2563eb",
    )
)
fig3.update_layout(
    height=330,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#526078"),
    yaxis=dict(title="Revenue (₹)", gridcolor="#e5eaf1"),
    xaxis=dict(showgrid=False),
    showlegend=False,
)
st.plotly_chart(fig3, use_container_width=True)
