from flask import Blueprint, jsonify

from services.analytics_service import (
    get_total_revenue,
    get_total_orders,
    get_average_order_value,
    get_top_products,
    get_low_stock_products,
    get_product_profit,
    get_category_sales,
    get_dashboard_summary
)


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/api/analytics"
)


@analytics_bp.route("/revenue", methods=["GET"])
def total_revenue():

    return jsonify({
        "total_revenue": get_total_revenue()
    })


@analytics_bp.route("/orders", methods=["GET"])
def total_orders():

    return jsonify({
        "total_orders": get_total_orders()
    })


@analytics_bp.route("/average-order-value", methods=["GET"])
def average_order_value():

    return jsonify({
        "average_order_value": get_average_order_value()
    })


@analytics_bp.route("/top-products", methods=["GET"])
def top_products():

    return jsonify(
        get_top_products()
    )


@analytics_bp.route("/low-stock", methods=["GET"])
def low_stock():

    return jsonify(
        get_low_stock_products()
    )


@analytics_bp.route("/product-profit", methods=["GET"])
def product_profit():

    return jsonify(
        get_product_profit()
    )


@analytics_bp.route("/category-sales", methods=["GET"])
def category_sales():

    return jsonify(
        get_category_sales()
    )


@analytics_bp.route("/summary", methods=["GET"])
def dashboard_summary():

    return jsonify(
        get_dashboard_summary()
    )