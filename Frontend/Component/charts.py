import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# COMMON CHART LAYOUT
# ============================================================

def chart_layout(title="", height=350):

    return {
        "height": height,
        "margin": dict(
            l=45,
            r=25,
            t=50,
            b=40
        ),

        "title": dict(
            text=title,
            font=dict(
                size=16
            ),
            x=0
        ),

        "paper_bgcolor": "rgba(0,0,0,0)",

        "plot_bgcolor": "rgba(0,0,0,0)",

        "font": dict(
            size=12
        ),

        "hovermode": "x unified",

        "xaxis": dict(
            showgrid=False,
            zeroline=False
        ),

        # IMPORTANT:
        # Do NOT put yaxis here.
        # Individual charts define their own y-axis.
    }


# ============================================================
# REVENUE CHART
# ============================================================

def revenue_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Month": [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun"
            ],

            "Revenue": [
                1.42,
                1.65,
                1.82,
                1.94,
                2.31,
                2.68
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Month"],
            y=data["Revenue"],

            mode="lines+markers",

            name="Revenue",

            line=dict(
                width=3
            ),

            marker=dict(
                size=7
            ),

            fill="tozeroy",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Revenue: ₹%{y:.2f}M"
                "<extra></extra>"
            )
        )
    )

    # Base layout
    fig.update_layout(
        **chart_layout(
            "Revenue performance",
            350
        )
    )

    # Y-axis defined ONLY here
    fig.update_yaxes(
        title_text="Revenue (₹M)",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zeroline=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# CATEGORY SALES CHART
# ============================================================

def category_sales_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Category": [
                "Accessories",
                "Computers",
                "Electronics"
            ],

            "Sales": [
                5.18,
                4.27,
                2.89
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["Category"],
            y=data["Sales"],

            name="Sales",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Sales: ₹%{y:.2f}M"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        **chart_layout(
            "Sales by category",
            350
        )
    )

    fig.update_yaxes(
        title_text="Sales (₹M)",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zeroline=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# TOP PRODUCTS CHART
# ============================================================

def top_products_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Product": [
                "Smart Watch",
                "USB-C Cable",
                "Smartphone",
                "Laptop Stand",
                "HDMI Cable"
            ],

            "Units": [
                28,
                27,
                26,
                23,
                23
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["Units"],
            y=data["Product"],

            orientation="h",

            name="Units Sold",

            hovertemplate=(
                "<b>%{y}</b><br>"
                "Units sold: %{x}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        **chart_layout(
            "Top products",
            350
        )
    )

    fig.update_xaxes(
        title_text="Units sold",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# SALES TREND CHART
# ============================================================

def sales_trend_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Month": [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun"
            ],

            "Orders": [
                6,
                8,
                7,
                9,
                10,
                10
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Month"],
            y=data["Orders"],

            mode="lines+markers",

            name="Orders",

            line=dict(
                width=3
            ),

            marker=dict(
                size=7
            ),

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Orders: %{y}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        **chart_layout(
            "Order trend",
            350
        )
    )

    fig.update_yaxes(
        title_text="Orders",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zeroline=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# PROFIT CHART
# ============================================================

def profit_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Product": [
                "Webcam",
                "HDMI Cable",
                "Smart Watch",
                "USB-C Cable",
                "Laptop Stand"
            ],

            "Profit": [
                1896,
                4477,
                5200,
                3900,
                4800
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["Product"],
            y=data["Profit"],

            name="Profit",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Profit: ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        **chart_layout(
            "Product profitability",
            350
        )
    )

    fig.update_yaxes(
        title_text="Profit (₹)",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zeroline=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# INVENTORY CHART
# ============================================================

def inventory_chart(data=None):

    if data is None:

        data = pd.DataFrame({
            "Status": [
                "Healthy",
                "At Risk",
                "Low Stock"
            ],

            "Products": [
                16,
                2,
                2
            ]
        })

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["Status"],
            y=data["Products"],

            name="Products",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Products: %{y}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        **chart_layout(
            "Inventory status",
            350
        )
    )

    fig.update_yaxes(
        title_text="Products",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zeroline=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )