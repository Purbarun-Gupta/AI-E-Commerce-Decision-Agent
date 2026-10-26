
from pathlib import Path

import pandas as pd
import streamlit as st

from api import api_get, api_put


# ============================================================
# HELPERS
# ============================================================

def fetch_inventory_records(response):
    """Extract inventory records from supported API response formats."""

    if isinstance(response, list):
        return response

    if isinstance(response, dict):
        for key in (
            "inventory_risk",
            "data",
            "products",
            "items",
            "value",
        ):
            records = response.get(key)

            if isinstance(records, list):
                return records

    return None


def fetch_product_prices(response):
    """Return actual selling prices keyed by product ID."""

    if not isinstance(response, dict):
        return {}

    records = response.get("product_profit", [])

    if not isinstance(records, list):
        return {}

    prices = {}

    for item in records:
        if not isinstance(item, dict):
            continue

        product_id = item.get("product_id")
        price = pd.to_numeric(item.get("price"), errors="coerce")

        if product_id is None or pd.isna(price):
            continue

        if price < 0:
            continue

        prices[product_id] = float(price)

    return prices


def stock_status(stock, reorder_level):
    """Classify stock using the configured reorder threshold."""

    if stock <= 0:
        return "Out of stock"

    if stock <= reorder_level:
        return "Reorder"

    if stock <= reorder_level * 1.5:
        return "Monitor"

    return "Healthy"


def money_inr(value):
    """Format a valid monetary value without inventing missing data."""

    if value is None or pd.isna(value):
        return "N/A"

    return f"₹{value:,.2f}"


# ============================================================
# INVENTORY PAGE
# ============================================================

def render_inventory():
    """Render the live CommerceAI inventory dashboard."""

    # --------------------------------------------------------
    # LOAD STYLES
    # --------------------------------------------------------

    base_dir = Path(__file__).resolve().parent.parent
    css_path = base_dir / "assets" / "style.css"

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

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

    if st.button("Refresh inventory", key="refresh_inventory"):
        st.rerun()

    # --------------------------------------------------------
    # FETCH LIVE DATA
    # --------------------------------------------------------

    with st.spinner("Loading live inventory data..."):
        inventory_response = api_get(
            "/api/analytics/inventory-risk"
        )

    if (
        isinstance(inventory_response, dict)
        and "error" in inventory_response
    ):
        st.error("Unable to load inventory from Flask.")
        st.write(inventory_response["error"])
        return

    records = fetch_inventory_records(inventory_response)

    if records is None:
        st.error("The inventory API returned an unexpected response.")
        st.write(inventory_response)
        return

    if not records:
        st.info("No inventory records were returned by the backend.")
        return

    # Fetch prices from the existing summary endpoint.
    with st.spinner("Loading product prices..."):
        summary_response = api_get("/api/analytics/summary")

    price_error = (
        isinstance(summary_response, dict)
        and "error" in summary_response
    )

    product_prices = (
        {}
        if price_error
        else fetch_product_prices(summary_response)
    )

    if price_error:
        st.warning(
            "Product prices could not be loaded. "
            "Inventory value will be shown as unavailable."
        )

    # --------------------------------------------------------
    # NORMALIZE INVENTORY DATA
    # --------------------------------------------------------

    df = pd.DataFrame(records)

    aliases = {
        "product_id": "Product ID",
        "product": "Product",
        "product_name": "Product",
        "name": "Product",
        "sku": "SKU",
        "category": "Category",
        "current_stock": "Stock",
        "stock": "Stock",
        "quantity": "Stock",
        "initial_stock": "Initial Stock",
        "reorder_level": "Reorder Level",
        "minimum_stock": "Reorder Level",
        "risk_level": "Risk Level",
        "shortage": "Shortage",
    }

    rename = {}

    for column in df.columns:
        normalized = str(column).strip().lower()

        if normalized in aliases:
            rename[column] = aliases[normalized]

    df = df.rename(columns=rename)

    required = [
        "Product ID",
        "Product",
        "Stock",
        "Reorder Level",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        st.error(
            "Inventory data is missing required fields: "
            + ", ".join(missing)
        )
        st.caption("Fields returned by the API:")
        st.write(list(df.columns))
        return

    # Validate product IDs and numeric inventory fields.
    df["Product ID"] = pd.to_numeric(
        df["Product ID"], errors="coerce"
    )

    for column in ("Stock", "Reorder Level"):
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    if df[
        ["Product ID", "Stock", "Reorder Level"]
    ].isna().any().any():
        st.error(
            "Some inventory records have invalid product IDs, "
            "stock quantities, or reorder levels."
        )
        return

    if (df["Stock"] < 0).any() or (df["Reorder Level"] < 0).any():
        st.error("Stock quantities and reorder levels cannot be negative.")
        return

    if df["Product ID"].duplicated().any():
        st.error(
            "The inventory API returned duplicate product IDs. "
            "Inventory totals cannot be calculated reliably."
        )
        return

    df["Product ID"] = df["Product ID"].astype(int)

    # Optional display fields.
    if "SKU" not in df.columns:
        df["SKU"] = "N/A"

    if "Category" not in df.columns:
        df["Category"] = "Uncategorized"

    if "Initial Stock" in df.columns:
        df["Initial Stock"] = pd.to_numeric(
            df["Initial Stock"], errors="coerce"
        )

    if "Shortage" in df.columns:
        df["Shortage"] = pd.to_numeric(
            df["Shortage"], errors="coerce"
        )

    # --------------------------------------------------------
    # MATCH ACTUAL PRODUCT PRICES
    # --------------------------------------------------------

    df["Unit Price"] = df["Product ID"].map(product_prices)

    df["Stock Value"] = (
        df["Stock"] * df["Unit Price"]
    )

    # Selling-price valuation:
    # current stock × actual selling price from the products data.
    if not price_error:
        missing_prices = df["Unit Price"].isna().sum()

        if missing_prices:
            st.warning(
                f"Prices are unavailable for {missing_prices} product(s). "
                "The total inventory value will be shown as N/A."
            )

    # --------------------------------------------------------
    # STOCK STATUS
    # --------------------------------------------------------

    df["Status"] = df.apply(
        lambda row: stock_status(
            row["Stock"],
            row["Reorder Level"],
        ),
        axis=1,
    )

    if "Risk Level" in df.columns:
        df["Risk Level"] = (
            df["Risk Level"]
            .fillna("Unknown")
            .astype(str)
            .str.upper()
        )

    # --------------------------------------------------------
    # INVENTORY METRICS
    # --------------------------------------------------------

    total_products = len(df)

    reorder_count = int(
        df["Status"].isin(
            ["Reorder", "Out of stock"]
        ).sum()
    )

    monitor_count = int(
        (df["Status"] == "Monitor").sum()
    )

    total_value = (
        float(df["Stock Value"].sum())
        if df["Unit Price"].notna().all()
        else None
    )

    k1, k2, k3, k4 = st.columns([1, 1.1, 1.1, 1.3])

    with k1:
        st.metric(
            "TOTAL PRODUCTS",
            f"{total_products:,}",
        )

    with k2:
        st.metric(
            "REORDER REQUIRED",
            f"{reorder_count:,}",
        )

    with k3:
        st.metric(
            "STOCK TO MONITOR",
            f"{monitor_count:,}",
        )

    with k4:
        st.metric(
            "INVENTORY VALUE",
            f"₹{total_value / 100000:.2f} L" if total_value is not None else "N/A"f"₹{total_value / 100000:.2f} L"
            if total_value is not None
            else "N/A",
            help=(
                f"Full inventory value: {money_inr(total_value)}"
                if total_value is not None
                else "Inventory value is unavailable."
            ),
        )

    if total_value is None:
        st.caption(
            "Inventory value is unavailable because a valid selling price "
            "was not returned for every product."
        )
    else:
        st.caption(
            "Inventory value is estimated using current stock multiplied "
            "by each product's selling price."
        )

    # --------------------------------------------------------
    # PRODUCT INVENTORY AND FILTERS
    # --------------------------------------------------------

    st.markdown("## Product inventory")

    f1, f2, f3 = st.columns([2, 1, 1])

    with f1:
        search = st.text_input(
            "Search product or SKU",
            key="inv_search",
        )

    with f2:
        categories = sorted(
            df["Category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        category = st.selectbox(
            "Category",
            ["All categories"] + categories,
            key="inv_category",
        )

    with f3:
        status_filter = st.selectbox(
            "Status",
            [
                "All statuses",
                "Healthy",
                "Monitor",
                "Reorder",
                "Out of stock",
            ],
            key="inv_status",
        )

    filtered = df.copy()

    if search.strip():
        term = search.strip()

        filtered = filtered[
            filtered["Product"].astype(str).str.contains(
                term,
                case=False,
                na=False,
            )
            | filtered["SKU"].astype(str).str.contains(
                term,
                case=False,
                na=False,
            )
        ]

    if category != "All categories":
        filtered = filtered[
            filtered["Category"].astype(str) == category
        ]

    if status_filter != "All statuses":
        filtered = filtered[
            filtered["Status"] == status_filter
        ]

    st.caption(
        f"Showing {len(filtered)} of {len(df)} products"
    )

    # --------------------------------------------------------
    # DISPLAY TABLE
    # --------------------------------------------------------

    display = filtered.copy()

    for column in ("Unit Price", "Stock Value"):
        if column in display.columns:
            display[column] = display[column].map(
                money_inr
            )

    preferred_columns = [
        "Product ID",
        "Product",
        "SKU",
        "Category",
        "Initial Stock",
        "Stock",
        "Reorder Level",
        "Risk Level",
        "Shortage",
        "Unit Price",
        "Stock Value",
        "Status",
    ]

    display_columns = [
        column
        for column in preferred_columns
        if column in display.columns
    ]

    display = display[display_columns]

    column_config = {
        "Product ID": st.column_config.NumberColumn(
            "Product ID",
            format="%d",
        ),
        "Stock": st.column_config.NumberColumn(
            "Stock",
            format="%d units",
        ),
        "Initial Stock": st.column_config.NumberColumn(
            "Initial stock",
            format="%d units",
        ),
        "Reorder Level": st.column_config.NumberColumn(
            "Reorder level",
            format="%d units",
        ),
        "Shortage": st.column_config.NumberColumn(
            "Shortage",
            format="%d units",
        ),
    }

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )

    # --------------------------------------------------------
    # REORDER RECOMMENDATIONS
    # --------------------------------------------------------

    st.markdown("## Reorder recommendations")

    reorder = df[
        df["Status"].isin(
            ["Reorder", "Out of stock"]
        )
    ]

    if reorder.empty:
        st.success(
            "No products currently require replenishment."
        )
    else:
        for _, row in reorder.iterrows():
            suggested = max(
                int(row["Reorder Level"] * 2 - row["Stock"]),
                int(row["Reorder Level"]),
            )

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(
                        f"**{row['Product']}**"
                    )

                    st.caption(
                        f"Product ID: {row['Product ID']} · "
                        f"{row['Category']} · "
                        f"{row['Status']}"
                    )

                with col2:
                    st.metric(
                        "Current stock",
                        f"{int(row['Stock'])} units",
                    )

                with col3:
                    st.metric(
                        "Suggested top-up",
                        f"{suggested} units",
                    )

    st.caption(
        "Inventory records and product prices are retrieved from the Flask API."
    )


    # --------------------------------------------------------
    # STOCK MANAGEMENT
    # --------------------------------------------------------

    st.markdown("## Stock management")
    st.caption(
        "Restock a product or correct its current quantity. "
        "Changes are saved to the database through Flask."
    )

    product_options = {
        f"{int(row['Product ID'])} — {row['Product']} "
        f"(Current stock: {int(row['Stock'])})":
            int(row["Product ID"])
        for _, row in df.iterrows()
    }

    with st.form("inventory_stock_update"):
        selected_product = st.selectbox(
            "Select product",
            options=list(product_options.keys()),
            key="stock_update_product",
        )

        operation = st.radio(
            "Update type",
            ["Restock", "Set stock quantity"],
            horizontal=True,
            key="stock_update_operation",
        )

        quantity = st.number_input(
            "Quantity to add" if operation == "Restock"
            else "New stock quantity",
            min_value=0,
            step=1,
            value=1 if operation == "Restock" else 0,
            key="stock_update_quantity",
        )

        submitted = st.form_submit_button(
            "Save stock update",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            product_id = product_options[selected_product]
            current_row = df.loc[
                df["Product ID"] == product_id
            ].iloc[0]

            current_stock = int(current_row["Stock"])

            if operation == "Restock":
                if quantity <= 0:
                    st.error("Enter a restock quantity greater than zero.")
                    st.stop()

                new_stock = current_stock + int(quantity)
            else:
                new_stock = int(quantity)

            if new_stock < 0:
                st.error("Stock cannot be negative.")
                st.stop()

            try:
                with st.spinner("Saving stock update..."):
                    result = api_put(
                        f"/api/inventory/{product_id}",
                        {
                            "current_stock": new_stock,
                        },
                    )

                if isinstance(result, dict) and result.get("error"):
                    st.error(
                        f"Stock update failed: {result['error']}"
                    )

                elif isinstance(result, dict) and result.get("inventory"):
                    saved_stock = result["inventory"].get(
                        "current_stock"
                    )

                    if saved_stock != new_stock:
                        st.warning(
                            "The backend response did not match "
                            "the requested stock quantity. "
                            "Please refresh and verify the database."
                        )
                    else:
                        st.success(
                            f"Stock updated successfully! "
                            f"Product ID {product_id}: "
                            f"{current_stock} → {saved_stock} units."
                        )
                        # Remove the old selectbox selection so its label
                        # is rebuilt using the latest stock value on rerun.
                        st.session_state.pop("stock_update_product", None)

                        # Rerun the page: all inventory data, KPIs, the table,
                        # recommendations, and selector are fetched/rebuilt.
                        st.rerun()

                else:
                    st.error(
                        "The backend returned an unexpected response. "
                        "Refresh inventory and verify the saved quantity."
                    )

            except Exception as exc:
                st.error(f"Unable to update stock: {exc}")
