"""
Frontend configuration for AI E-Commerce Decision Agent.
"""

import os
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = FRONTEND_DIR.parent
ASSETS_DIR = FRONTEND_DIR / "assets"


# =========================================================
# APPLICATION
# =========================================================

APP_NAME = "AI E-Commerce Decision Agent"

APP_DESCRIPTION = (
    "An AI-powered decision assistant for e-commerce analytics, "
    "inventory management, business insights, and company knowledge."
)

APP_VERSION = "1.0.0"


# =========================================================
# FLASK BACKEND
# =========================================================

BACKEND_HOST = os.getenv(
    "BACKEND_HOST",
    "127.0.0.1"
)

BACKEND_PORT = int(
    os.getenv(
        "BACKEND_PORT",
        "5000"
    )
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    f"http://{BACKEND_HOST}:{BACKEND_PORT}"
)


# =========================================================
# API ENDPOINTS
# =========================================================

API_BASE_URL = f"{BACKEND_URL}/api"

# These are kept here so the frontend has one place
# for backend endpoint configuration.

AGENT_ENDPOINT = f"{API_BASE_URL}/agent"

ANALYTICS_ENDPOINT = f"{API_BASE_URL}/analytics"

REVENUE_ENDPOINT = f"{ANALYTICS_ENDPOINT}/revenue"

ORDERS_ENDPOINT = f"{ANALYTICS_ENDPOINT}/orders"

AOV_ENDPOINT = f"{ANALYTICS_ENDPOINT}/average-order-value"

TOP_PRODUCTS_ENDPOINT = f"{ANALYTICS_ENDPOINT}/top-products"

LOW_STOCK_ENDPOINT = f"{ANALYTICS_ENDPOINT}/low-stock"

PRODUCT_PROFIT_ENDPOINT = f"{ANALYTICS_ENDPOINT}/product-profit"

PRODUCT_PERFORMANCE_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/product-performance"
)

TOTAL_PROFIT_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/total-profit"
)

PROFIT_MARGIN_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/profit-margin"
)

INVENTORY_RISK_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/inventory-risk"
)

CUSTOMER_METRICS_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/customer-metrics"
)

SALES_TRENDS_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/sales-trends"
)

CATEGORY_SALES_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/category-sales"
)

SUMMARY_ENDPOINT = (
    f"{ANALYTICS_ENDPOINT}/summary"
)


# =========================================================
# REQUEST SETTINGS
# =========================================================

API_TIMEOUT = int(
    os.getenv(
        "API_TIMEOUT",
        "60"
    )
)


# =========================================================
# CHAT SETTINGS
# =========================================================

MAX_CHAT_HISTORY = int(
    os.getenv(
        "MAX_CHAT_HISTORY",
        "50"
    )
)

MAX_RECENT_QUESTIONS = int(
    os.getenv(
        "MAX_RECENT_QUESTIONS",
        "10"
    )
)


# =========================================================
# UI SETTINGS
# =========================================================

PAGE_TITLE = APP_NAME

PAGE_ICON = "🤖"

LAYOUT = "wide"

SIDEBAR_STATE = "expanded"


# =========================================================
# FEATURE FLAGS
# =========================================================

ENABLE_ANALYTICS = True

ENABLE_INVENTORY = True

ENABLE_KNOWLEDGE_BASE = True

ENABLE_CHAT = True


# =========================================================
# DEMO / DEVELOPMENT SETTINGS
# =========================================================

# Keep this True while the frontend is being developed
# without the Flask API connection.

DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).lower() == "true"


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_api_url(endpoint: str) -> str:
    """
    Build a complete API URL.

    Example:
        get_api_url("/analytics/revenue")
    """

    if endpoint.startswith("/"):
        endpoint = endpoint[1:]

    return f"{API_BASE_URL}/{endpoint}"


def get_config() -> dict:
    """
    Return the main frontend configuration.
    """

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "backend_url": BACKEND_URL,
        "api_base_url": API_BASE_URL,
        "api_timeout": API_TIMEOUT,
        "demo_mode": DEMO_MODE,
    }