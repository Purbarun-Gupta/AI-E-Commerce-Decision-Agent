import streamlit as st


def display_metric(
    label,
    value,
    change=None,
    icon=None
):
    """
    Display a professional CommerceAI metric card.
    """

    icon_html = ""

    if icon:
        icon_html = f"""
        <span style="
            float:right;
            font-size:16px;
            opacity:0.85;
        ">
            {icon}
        </span>
        """


    change_html = ""

    if change:

        change_html = f"""
        <div class="metric-change">
            {change}
        </div>
        """


    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {label}
                {icon_html}
            </div>

            <div class="metric-value">
                {value}
            </div>

            {change_html}

        </div>
        """,
        unsafe_allow_html=True
    )



def display_business_metrics(
    revenue,
    orders,
    aov,
    profit
):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_metric("Total Revenue", revenue, icon="₹")

    with col2:
        display_metric("Total Orders", orders, icon="□")

    with col3:
        display_metric("Average Order", aov, icon="↗")

    with col4:
        display_metric("Total Profit", profit, icon="◆")


def display_inventory_metrics(
    products,
    low_stock,
    at_risk,
    inventory_value
):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_metric("Products", products, icon="▦")

    with col2:
        display_metric("Low Stock", low_stock, icon="!")

    with col3:
        display_metric("Inventory Risk", at_risk, icon="⚠")

    with col4:
        display_metric("Inventory Value", inventory_value, icon="₹")


def display_metric_row(metrics):

    """
    metrics format:

    [
        {
            "label": "Revenue",
            "value": "₹12.3M",
            "change": "↑ 12%"
        }
    ]
    """

    columns = st.columns(len(metrics))

    for column, metric in zip(columns, metrics):

        with column:

            display_metric(
                metric.get("label", ""),
                metric.get("value", ""),
                metric.get("change"),
                metric.get("icon")
            )