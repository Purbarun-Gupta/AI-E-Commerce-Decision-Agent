
import math

import pandas as pd
import streamlit as st

from api import api_get


# ---------------------------------------------------------
# API HELPERS
# ---------------------------------------------------------

def fetch_data(endpoint):
    """Fetch data from Flask and return explicit error details."""
    try:
        result = api_get(endpoint)

        if isinstance(result, dict) and "error" in result:
            return None, result

        if result is None:
            return None, {
                "error": "The backend returned no response.",
                "endpoint": endpoint,
            }

        return result, None

    except Exception as exc:
        return None, {
            "error": str(exc),
            "endpoint": endpoint,
        }


def to_dataframe(data):
    """Convert supported API list responses to a DataFrame."""
    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        for key in (
            "value",
            "data",
            "products",
            "trends",
            "inventory_risk",
            "results",
            "items",
        ):
            value = data.get(key)
            if isinstance(value, list):
                return pd.DataFrame(value)

    return pd.DataFrame()


def find_column(df, candidates):
    """Find a matching column without depending on capitalization."""
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        matched = lookup.get(candidate.strip().lower())
        if matched is not None:
            return matched

    return None


def money_inr(value):
    """Format valid numeric values as INR; never invent missing values."""
    if value is None or isinstance(value, bool):
        return "N/A"

    try:
        number = float(value)
        if not math.isfinite(number):
            return "N/A"
        return f"₹{number:,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def number_display(value):
    """Format counts without silently replacing missing data with zero."""
    if value is None or isinstance(value, bool):
        return "N/A"

    try:
        number = float(value)
        if not math.isfinite(number):
            return "N/A"

        return f"{int(number):,}" if number.is_integer() else f"{number:,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def show_error_details(title, error):
    """Display actionable backend error details."""
    with st.expander(title):
        st.write(error)


def numeric_chart_frame(df, category_col, value_cols):
    """Prepare valid numeric data for Streamlit charts."""
    columns = [category_col] + value_cols
    chart = df[columns].copy()

    for column in value_cols:
        chart[column] = pd.to_numeric(
            chart[column], errors="coerce"
        )

    chart = chart.dropna(subset=value_cols)

    if chart.empty:
        return chart

    chart[category_col] = chart[category_col].astype(str)
    chart = chart.set_index(category_col)

    return chart


# ---------------------------------------------------------
# ANALYTICS PAGE
# ---------------------------------------------------------

def render_analytics():
    """Render the live CommerceAI analytics dashboard."""

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

    # Fetch live data on every page run.
    with st.spinner("Loading live business analytics..."):
        summary, summary_error = fetch_data(
            "/api/analytics/summary"
        )
        profit_data, profit_error = fetch_data(
            "/api/analytics/total-profit"
        )
        trends_data, trends_error = fetch_data(
            "/api/analytics/sales-trends"
        )
        products_data, products_error = fetch_data(
            "/api/analytics/top-products"
        )
        risk_data, risk_error = fetch_data(
            "/api/analytics/inventory-risk"
        )
        category_data, category_error = fetch_data(
            "/api/analytics/category-sales"
        )

    # -----------------------------------------------------
    # BUSINESS OVERVIEW
    # -----------------------------------------------------

    st.subheader("Business Overview")

    if summary_error:
        st.error("Unable to retrieve the business analytics summary.")
        show_error_details("Summary API error", summary_error)
        return

    if not isinstance(summary, dict):
        st.error(
            "The summary endpoint returned an unexpected response."
        )
        show_error_details("Summary response", summary)
        return

    total_revenue = summary.get("total_revenue")
    total_orders = summary.get("total_orders")
    average_order_value = summary.get("average_order_value")

    total_profit = None

    if profit_error:
        st.warning("Total profit is currently unavailable.")
    elif isinstance(profit_data, dict):
        total_profit = profit_data.get("total_profit")
    else:
        st.warning("The total-profit endpoint returned an unexpected response.")

    metrics = [
        ("Total Revenue", money_inr(total_revenue)),
        ("Total Orders", number_display(total_orders)),
        ("Average Order Value", money_inr(average_order_value)),
        ("Total Profit", money_inr(total_profit)),
    ]

    columns = st.columns(4)

    for column, (label, value) in zip(columns, metrics):
        with column:
            st.metric(label, value)

    if profit_error:
        show_error_details("Total profit API error", profit_error)

    st.divider()

    # -----------------------------------------------------
    # SALES TRENDS
    # -----------------------------------------------------

    st.subheader("Sales Trends")

    trends_df = to_dataframe(trends_data)

    if trends_error:
        st.error("Unable to retrieve sales trends.")
        show_error_details("Sales trends API error", trends_error)

    elif trends_df.empty:
        st.info("No sales-trend records were returned by the backend.")

    else:
        date_col = find_column(
            trends_df,
            ["month", "date", "period", "year_month", "order_month"],
        )
        revenue_col = find_column(
            trends_df,
            ["revenue", "sales", "total_revenue", "monthly_revenue"],
        )
        orders_col = find_column(
            trends_df,
            ["orders", "total_orders", "order_count", "monthly_orders"],
        )

        col1, col2 = st.columns(2)

        with col1:
            st.caption("Revenue over time")

            if date_col and revenue_col:
                chart = numeric_chart_frame(
                    trends_df, date_col, [revenue_col]
                )

                if not chart.empty:
                    chart = chart.rename(
                        columns={revenue_col: "Revenue (₹)"}
                    )
                    st.line_chart(chart)
                else:
                    st.info("No valid revenue values are available.")
            else:
                st.info(
                    "The API response does not contain recognizable "
                    "date and revenue fields."
                )

        with col2:
            st.caption("Orders over time")

            if date_col and orders_col:
                chart = numeric_chart_frame(
                    trends_df, date_col, [orders_col]
                )

                if not chart.empty:
                    chart = chart.rename(
                        columns={orders_col: "Orders"}
                    )
                    st.bar_chart(chart)
                else:
                    st.info("No valid order-count values are available.")
            else:
                st.info(
                    "The API response does not contain recognizable "
                    "date and order-count fields."
                )

        with st.expander("Sales trends data"):
            st.dataframe(
                trends_df,
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    # -----------------------------------------------------
    # TOP PRODUCTS
    # -----------------------------------------------------

    st.subheader("Top Products")

    products_df = to_dataframe(products_data)

    if products_error:
        st.error("Unable to retrieve top products.")
        show_error_details("Top products API error", products_error)

    elif products_df.empty:
        st.info("No top-product records were returned by the backend.")

    else:
        product_col = find_column(
            products_df,
            ["product_name", "product", "productname", "name"],
        )
        revenue_col = find_column(
            products_df,
            ["revenue", "total_revenue", "sales"],
        )
        units_col = find_column(
            products_df,
            ["units_sold", "quantity_sold", "units", "total_units"],
        )

        chart_col, table_col = st.columns(2)

        with chart_col:
            st.caption("Product Revenue")

            if product_col and revenue_col:
                chart = numeric_chart_frame(
                    products_df, product_col, [revenue_col]
                )

                if not chart.empty:
                    chart = chart.rename(
                        columns={revenue_col: "Revenue (₹)"}
                    )
                    st.bar_chart(chart)
                else:
                    st.info("No valid product-revenue values are available.")
            else:
                st.info(
                    "Product names or revenue fields are missing "
                    "from the API response."
                )

        with table_col:
            st.caption("Product Details")

            display_df = products_df.rename(
                columns={
                    "product_id": "Product ID",
                    "product_name": "Product",
                    "units_sold": "Units Sold",
                    "revenue": "Revenue (₹)",
                }
            )

            # Include profit only if the API actually provides it.
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

        if units_col:
            total_units = pd.to_numeric(
                products_df[units_col], errors="coerce"
            ).sum(min_count=1)

            if pd.notna(total_units):
                st.caption(
                    f"Units sold across returned top-product records: "
                    f"{number_display(total_units)}"
                )

    st.divider()

    # -----------------------------------------------------
    # CATEGORY SALES
    # -----------------------------------------------------

    st.subheader("Category Sales")

    category_df = to_dataframe(category_data)

    if category_error:
        st.error("Unable to retrieve category sales.")
        show_error_details("Category sales API error", category_error)

    elif category_df.empty:
        st.info("No category-sales records were returned by the backend.")

    else:
        category_col = find_column(
            category_df,
            ["category", "category_name", "product_category", "name"],
        )
        category_revenue_col = find_column(
            category_df,
            ["revenue", "total_revenue", "sales", "category_revenue"],
        )

        if category_col and category_revenue_col:
            chart = numeric_chart_frame(
                category_df, category_col, [category_revenue_col]
            )

            if not chart.empty:
                chart = chart.rename(
                    columns={category_revenue_col: "Revenue (₹)"}
                )
                st.bar_chart(chart)
            else:
                st.info("No valid category-revenue values are available.")
        else:
            st.info(
                "Category or revenue fields were not recognized. "
                "The raw API response is shown below."
            )

        with st.expander("Category sales data"):
            st.dataframe(
                category_df,
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    # -----------------------------------------------------
    # INVENTORY RISK
    # -----------------------------------------------------

    st.subheader("Inventory Risk")

    risk_df = to_dataframe(risk_data)

    if risk_error:
        st.error("Unable to retrieve inventory-risk data.")
        show_error_details("Inventory risk API error", risk_error)

    elif risk_df.empty:
        st.info("No inventory-risk records were returned by the backend.")

    else:
        stock_col = find_column(
            risk_df,
            ["current_stock", "stock_remaining", "stock", "quantity"],
        )
        reorder_col = find_column(
            risk_df,
            ["reorder_level", "minimum_stock", "reorder_point"],
        )
        product_col = find_column(
            risk_df,
            ["product_name", "product", "name"],
        )

        chart_col, table_col = st.columns(2)

        with chart_col:
            st.caption("Stock vs Reorder Level")

            if stock_col and reorder_col:
                chart = numeric_chart_frame(
                    risk_df,
                    product_col if product_col else stock_col,
                    [stock_col, reorder_col],
                )

                if not chart.empty:
                    if not product_col:
                        chart.index.name = "Product / Stock"

                    chart = chart.rename(
                        columns={
                            stock_col: "Current Stock",
                            reorder_col: "Reorder Level",
                        }
                    )
                    st.bar_chart(chart)
                else:
                    st.info("No valid stock and reorder values are available.")
            else:
                st.info(
                    "Stock or reorder-level fields were not recognized."
                )

        with table_col:
            st.caption("Inventory Risk Details")
            st.dataframe(
                risk_df,
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        "Data is retrieved from the Flask analytics API. "
        "Missing or unavailable data is not replaced with demo figures."
    )
