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

        with open(css_path, "r", encoding="utf-8") as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="page-header">

        <div>

            <div class="page-kicker">
                INVENTORY INTELLIGENCE
            </div>

            <h1 class="page-title">
                Inventory Overview
            </h1>

            <p class="page-description">
                Monitor stock levels, identify inventory risks
                and understand reorder opportunities.
            </p>

        </div>

        <div class="page-header-icon">
            📦
        </div>

    </div>
    """
)


# ============================================================
# INVENTORY METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                TOTAL PRODUCTS
            </div>

            <div class="metric-value">
                20
            </div>

            <div class="metric-note">
                Active products
            </div>

        </div>
        """
    )


with col2:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                LOW STOCK
            </div>

            <div class="metric-value">
                0
            </div>

            <div class="metric-note positive">
                Healthy stock level
            </div>

        </div>
        """
    )


with col3:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                INVENTORY RISK
            </div>

            <div class="metric-value">
                2
            </div>

            <div class="metric-note warning">
                Products require attention
            </div>

        </div>
        """
    )


with col4:

    st.html(
        """
        <div class="metric-card">

            <div class="metric-label">
                INVENTORY VALUE
            </div>

            <div class="metric-value">
                ₹8.42M
            </div>

            <div class="metric-note">
                Current inventory value
            </div>

        </div>
        """
    )


st.divider()


# ============================================================
# INVENTORY STATUS
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>

            <div class="section-kicker">
                STOCK MONITORING
            </div>

            <div class="section-title">
                Inventory status
            </div>

        </div>

        <div class="section-description">
            Current stock position across products.
        </div>

    </div>
    """
)


inventory_df = pd.DataFrame(
    {
        "Product": [
            "Smart Watch",
            "USB-C Cable",
            "Smartphone",
            "Laptop Stand",
            "HDMI Cable",
            "Webcam",
        ],
        "Stock": [
            42,
            68,
            31,
            55,
            19,
            14,
        ],
        "Status": [
            "Healthy",
            "Healthy",
            "Healthy",
            "Healthy",
            "Monitor",
            "Monitor",
        ],
    }
)


st.dataframe(
    inventory_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# RISK SECTION
# ============================================================

risk_col1, risk_col2 = st.columns(2)


with risk_col1:

    st.html(
        """
        <div class="risk-card warning-card">

            <div class="risk-icon">
                ⚠
            </div>

            <div>

                <div class="risk-title">
                    Inventory attention required
                </div>

                <div class="risk-description">
                    2 products are approaching their
                    inventory risk threshold.
                </div>

            </div>

        </div>
        """
    )


with risk_col2:

    st.html(
        """
        <div class="risk-card success-card">

            <div class="risk-icon">
                ✓
            </div>

            <div>

                <div class="risk-title">
                    Overall inventory is healthy
                </div>

                <div class="risk-description">
                    No products are currently classified
                    as critically low stock.
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# REORDER RECOMMENDATIONS
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>

            <div class="section-kicker">
                AI RECOMMENDATIONS
            </div>

            <div class="section-title">
                Reorder opportunities
            </div>

        </div>

    </div>
    """
)


recommendations = [
    (
        "Webcam",
        "Stock is approaching the risk threshold."
    ),
    (
        "HDMI Cable",
        "Monitor demand and consider replenishment."
    ),
]


for product, recommendation in recommendations:

    st.html(
        f"""
        <div class="recommendation-card">

            <div class="recommendation-icon">
                ↻
            </div>

            <div class="recommendation-content">

                <div class="recommendation-title">
                    {product}
                </div>

                <div class="recommendation-text">
                    {recommendation}
                </div>

            </div>

            <div class="recommendation-arrow">
                →
            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="main-footer">

        CommerceAI
        <span>•</span>
        Inventory Intelligence

    </div>
    """
)