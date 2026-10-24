import streamlit as st
import pandas as pd

from api import api_get


def render_analytics():
    """Render the CommerceAI analytics dashboard."""

    st.markdown(
        """
        <div class="chat-page-header">
            <div>
                <div class="page-kicker">COMMERCEAI WORKSPACE</div>
                <h1>Business Analytics</h1>
                <p>
                    Monitor revenue, orders, profitability,
                    product performance, and inventory risk.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Refresh analytics", key="refresh_analytics"):
        st.rerun()

    # --------------------------------------------------
    # HARDCODED DEMO DATA — replace with API data later
    # --------------------------------------------------

    demo_overview = {
        "total_revenue": 12345909,
        "total_orders": 50,
        "average_order_value": 246918.18,
        "total_profit": 2845000,
    }

    demo_sales_trends = pd.DataFrame({
        "Month": [
            "May", "Jun", "Jul", "Aug", "Sep", "Oct",
            "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"
        ],
        "Revenue": [
            720000, 850000, 790000, 980000,
            1050000, 920000, 1180000, 1320000,
            1100000, 1250000, 1450000, 1685909
        ],
        "Orders": [
            32, 38, 35, 42, 47, 41,
            51, 58, 49, 55, 63, 72
        ],
    })

    demo_top_products = pd.DataFrame({
        "Product": [
            "Wireless Headphones",
            "Smart Watch",
            "Bluetooth Speaker",
            "Laptop Stand",
            "USB-C Hub",
        ],
        "Units Sold": [245, 198, 176, 154, 132],
        "Revenue": [735000, 594000, 440000, 308000, 264000],
        "Profit": [220500, 178200, 132000, 107800, 79200],
    })

    demo_inventory_risk = pd.DataFrame({
        "Product": [
            "USB-C Hub",
            "Wireless Mouse",
            "Laptop Stand",
            "Phone Charger",
        ],
        "Stock Remaining": [5, 8, 6, 4],
        "Reorder Level": [20, 15, 12, 10],
        "Risk Level": ["High", "Medium", "High", "High"],
    })

    # --------------------------------------------------
    # OPTIONAL API DATA
    # Use API values when available; otherwise use demo data
    # --------------------------------------------------

    overview = demo_overview
    top_products = None
    inventory_risk = None
    sales_trends = None

    try:
        with st.spinner("Checking analytics API..."):
            api_overview = api_get("/api/analytics/overview")
            api_top_products = api_get("/api/analytics/top-products")
            api_inventory_risk = api_get("/api/analytics/inventory-risk")
            api_sales_trends = api_get("/api/analytics/sales-trends")

        if isinstance(api_overview, dict) and "error" not in api_overview:
            # Use API overview only if it contains expected metric keys.
            if any(
                key in api_overview
                for key in [
                    "total_revenue",
                    "total_orders",
                    "average_order_value",
                    "total_profit",
                ]
            ):
                overview = {**demo_overview, **api_overview}

        if isinstance(api_top_products, dict) and "error" not in api_top_products:
            products = api_top_products.get(
                "data", api_top_products.get("products", [])
            )
            if isinstance(products, list) and products:
                top_products = pd.DataFrame(products)

        if isinstance(api_inventory_risk, dict) and "error" not in api_inventory_risk:
            risks = api_inventory_risk.get(
                "data",
                api_inventory_risk.get(
                    "products",
                    api_inventory_risk.get("inventory_risk", []),
                ),
            )
            if isinstance(risks, list) and risks:
                inventory_risk = pd.DataFrame(risks)

        if isinstance(api_sales_trends, dict) and "error" not in api_sales_trends:
            trends = api_sales_trends.get(
                "data", api_sales_trends.get("trends", [])
            )
            if isinstance(trends, list) and trends:
                api_trends_df = pd.DataFrame(trends)

                date_column = next(
                    (
                        col for col in ["date", "month", "period"]
                        if col in api_trends_df.columns
                    ),
                    None,
                )
                revenue_column = next(
                    (
                        col for col in ["revenue", "sales", "total_revenue"]
                        if col in api_trends_df.columns
                    ),
                    None,
                )

                if date_column and revenue_column:
                    demo_sales_trends = api_trends_df.rename(
                        columns={
                            date_column: "Month",
                            revenue_column: "Revenue",
                        }
                    )
                    if "Orders" not in demo_sales_trends.columns:
                        demo_sales_trends["Orders"] = 0

    except Exception:
        # The dashboard remains usable when the analytics API is unavailable.
        pass

    # --------------------------------------------------
    # BUSINESS OVERVIEW
    # --------------------------------------------------

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("Total Revenue", overview.get("total_revenue", 0), "${:,.2f}"),
        ("Total Orders", overview.get("total_orders", 0), "{:,.0f}"),
        (
            "Average Order Value",
            overview.get("average_order_value", 0),
            "${:,.2f}",
        ),
        ("Total Profit", overview.get("total_profit", 0), "${:,.2f}"),
    ]

    for column, (label, value, fmt) in zip(
        [col1, col2, col3, col4], metrics
    ):
        with column:
            try:
                display_value = fmt.format(float(value or 0))
            except (TypeError, ValueError):
                display_value = fmt.format(0)
            st.metric(label, display_value)

    st.divider()

    # --------------------------------------------------
    # SALES TRENDS — HARDCODED GRAPH
    # --------------------------------------------------

    st.subheader("Sales Trends")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.caption("Monthly Revenue")
        st.line_chart(
            demo_sales_trends.set_index("Month")["Revenue"],
            use_container_width=True,
        )

    with chart_col2:
        st.caption("Monthly Orders")
        st.bar_chart(
            demo_sales_trends.set_index("Month")["Orders"],
            use_container_width=True,
        )

    st.divider()

    # --------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------

    st.subheader("Top Products")

    products_df = top_products if top_products is not None else demo_top_products

    product_chart_column = next(
        (
            col for col in ["Revenue", "revenue", "total_revenue", "Profit", "profit"]
            if col in products_df.columns
        ),
        None,
    )

    product_col1, product_col2 = st.columns([1, 1])

    with product_col1:
        st.caption("Product Performance")
        if product_chart_column:
            product_name_column = next(
                (
                    col for col in ["Product", "product", "product_name", "name"]
                    if col in products_df.columns
                ),
                None,
            )

            chart_df = products_df.copy()
            if product_name_column:
                chart_df = chart_df.set_index(product_name_column)

            st.bar_chart(chart_df[product_chart_column])

    with product_col2:
        st.caption("Product Details")
        st.dataframe(
            products_df,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # --------------------------------------------------
    # INVENTORY RISK
    # --------------------------------------------------

    st.subheader("Inventory Risk")

    risk_df = (
        inventory_risk
        if inventory_risk is not None
        else demo_inventory_risk
    )

    risk_col1, risk_col2 = st.columns([1, 1])

    with risk_col1:
        st.caption("Stock Remaining vs Reorder Level")

        stock_column = next(
            (
                col for col in ["Stock Remaining", "stock_remaining", "stock", "quantity"]
                if col in risk_df.columns
            ),
            None,
        )
        reorder_column = next(
            (
                col for col in ["Reorder Level", "reorder_level", "minimum_stock"]
                if col in risk_df.columns
            ),
            None,
        )
        risk_product_column = next(
            (
                col for col in ["Product", "product", "product_name", "name"]
                if col in risk_df.columns
            ),
            None,
        )

        if stock_column and reorder_column:
            stock_chart = risk_df.copy()
            if risk_product_column:
                stock_chart = stock_chart.set_index(risk_product_column)

            stock_chart = stock_chart[[stock_column, reorder_column]].rename(
                columns={
                    stock_column: "Stock Remaining",
                    reorder_column: "Reorder Level",
                }
            )
            st.bar_chart(stock_chart)
        else:
            st.info("Stock and reorder-level fields are not available in this dataset.")

    with risk_col2:
        st.caption("Inventory Risk Details")
        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Demo charts use hardcoded sample data when matching API data is unavailable."
    )
