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
    revenue="₹12.35M",
    orders="50",
    aov="₹246.9K",
    profit="₹1.84M"
):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        display_metric(
            "Total Revenue",
            revenue,
            "↑ Strong revenue performance",
            "₹"
        )

    with col2:

        display_metric(
            "Total Orders",
            orders,
            "↑ Healthy order volume",
            "□"
        )

    with col3:

        display_metric(
            "Average Order",
            aov,
            "Per completed order",
            "↗"
        )

    with col4:

        display_metric(
            "Total Profit",
            profit,
            "↑ Positive profitability",
            "◆"
        )


def display_inventory_metrics(
    products="20",
    low_stock="0",
    at_risk="2",
    inventory_value="₹8.42M"
):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        display_metric(
            "Products",
            products,
            "Active inventory",
            "▦"
        )

    with col2:

        display_metric(
            "Low Stock",
            low_stock,
            "Needs monitoring",
            "!"
        )

    with col3:

        display_metric(
            "Inventory Risk",
            at_risk,
            "Products requiring attention",
            "⚠"
        )

    with col4:

        display_metric(
            "Inventory Value",
            inventory_value,
            "Estimated stock value",
            "₹"
        )


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