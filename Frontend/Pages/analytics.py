import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Analytics | CommerceAI",
    page_icon="📊",
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

        with open(css_path, "r", encoding="utf-8") as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div class="page-header">

        <div>

            <div class="page-kicker">
                BUSINESS INTELLIGENCE
            </div>

            <h1 class="page-title">
                Analytics Overview
            </h1>

            <p class="page-description">
                Understand revenue, orders, products
                and profitability through a unified business view.
            </p>

        </div>

        <div class="page-header-icon">
            📊
        </div>

    </div>
    """
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                TOTAL REVENUE
            </div>

            <div class="metric-value">
                ₹12.35M
            </div>

            <div class="metric-note positive">
                ↑ Strong revenue performance
            </div>

        </div>
        """
    )


with col2:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                TOTAL ORDERS
            </div>

            <div class="metric-value">
                50
            </div>

            <div class="metric-note positive">
                ↑ Healthy order volume
            </div>

        </div>
        """
    )


with col3:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                AVERAGE ORDER VALUE
            </div>

            <div class="metric-value">
                ₹246.9K
            </div>

            <div class="metric-note">
                Per completed order
            </div>

        </div>
        """
    )


with col4:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                TOTAL PROFIT
            </div>

            <div class="metric-value">
                ₹1.84M
            </div>

            <div class="metric-note positive">
                ↑ Positive profitability
            </div>

        </div>
        """
    )


st.divider()


# ============================================================
# CHART DATA
# ============================================================

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
]

revenue = [
    1.42,
    1.65,
    1.82,
    1.95,
    2.31,
    2.67,
]

orders = [
    6,
    8,
    7,
    9,
    10,
    10,
]


# ============================================================
# CHARTS
# ============================================================

chart1, chart2 = st.columns([2, 1])


# ------------------------------------------------------------
# REVENUE
# ------------------------------------------------------------

with chart1:

    st.html(
        """
        <div class="chart-header">

            <div class="chart-title">
                Revenue performance
            </div>

            <div class="chart-description">
                Monthly revenue movement across the business.
            </div>

        </div>
        """
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=revenue,
            mode="lines+markers",
            line=dict(
                width=3,
                color="#7c6cff"
            ),
            marker=dict(
                size=7,
                color="#9a8cff"
            ),
            fill="tozeroy",
            fillcolor="rgba(124,108,255,0.08)",
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#aeb5c7"
        ),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            title="Revenue (₹M)",
            gridcolor="rgba(255,255,255,0.06)"
        ),
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# ORDERS
# ------------------------------------------------------------

with chart2:

    st.html(
        """
        <div class="chart-header">

            <div class="chart-title">
                Order activity
            </div>

            <div class="chart-description">
                Monthly order volume.
            </div>

        </div>
        """
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=months,
            y=orders,
            mode="lines+markers",
            line=dict(
                width=3,
                color="#9a6cff"
            ),
            marker=dict(
                size=7,
                color="#b39cff"
            ),
        )
    )

    fig2.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#aeb5c7"
        ),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            title="Orders",
            gridcolor="rgba(255,255,255,0.06)"
        ),
        showlegend=False,
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ============================================================
# TOP PRODUCTS
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>
            <div class="section-kicker">
                PRODUCT INTELLIGENCE
            </div>

            <div class="section-title">
                Top performing products
            </div>
        </div>

        <div class="section-description">
            Products generating the highest order volume.
        </div>

    </div>
    """
)


products = pd.DataFrame(
    {
        "Product": [
            "Smart Watch",
            "USB-C Cable",
            "Smartphone",
            "Laptop Stand",
            "HDMI Cable",
        ],
        "Units Sold": [
            28,
            27,
            26,
            23,
            23,
        ],
    }
)


st.dataframe(
    products,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CATEGORY SALES
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>
            <div class="section-kicker">
                SALES MIX
            </div>

            <div class="section-title">
                Category performance
            </div>
        </div>

    </div>
    """
)


category_df = pd.DataFrame(
    {
        "Category": [
            "Accessories",
            "Computers",
            "Electronics",
        ],
        "Revenue": [
            5187386,
            4271033,
            2887490,
        ],
    }
)


fig3 = go.Figure(
    go.Bar(
        x=category_df["Category"],
        y=category_df["Revenue"],
        marker_color="#7567f5",
    )
)


fig3.update_layout(
    height=350,
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=10
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#aeb5c7"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        title="Revenue",
    ),
    xaxis=dict(
        showgrid=False
    ),
    showlegend=False,
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="main-footer">

        CommerceAI
        <span>
            •
        </span>
        Business Analytics
    </div>
    """
)