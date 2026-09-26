from sqlalchemy import func

from db.models import Order, OrderItem, Product, Inventory
from db.connection import get_db


def get_total_revenue():
    db = next(get_db())

    try:
        result = db.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).scalar()

        return result

    finally:
        db.close()


def get_total_orders():
    db = next(get_db())

    try:
        return db.query(Order).count()

    finally:
        db.close()


def get_average_order_value():
    db = next(get_db())

    try:
        result = db.query(
            func.coalesce(func.avg(Order.total_amount), 0)
        ).scalar()

        return round(float(result), 2)

    finally:
        db.close()


def get_top_products(limit=5):
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(
                    OrderItem.quantity * OrderItem.unit_price
                ).label("revenue")
            )
            .join(
                OrderItem,
                Product.id == OrderItem.product_id
            )
            .group_by(
                Product.id,
                Product.name
            )
            .order_by(
                func.sum(OrderItem.quantity).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.id,
                "product_name": row.name,
                "units_sold": row.units_sold,
                "revenue": row.revenue
            }
            for row in results
        ]

    finally:
        db.close()


def get_low_stock_products():
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.id,
                Product.name,
                Inventory.current_stock,
                Inventory.reorder_level
            )
            .join(
                Inventory,
                Product.id == Inventory.product_id
            )
            .filter(
                Inventory.current_stock <= Inventory.reorder_level
            )
            .all()
        )

        return [
            {
                "product_id": row.id,
                "product_name": row.name,
                "current_stock": row.current_stock,
                "reorder_level": row.reorder_level
            }
            for row in results
        ]

    finally:
        db.close()


def get_product_profit():
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.id,
                Product.name,
                Product.price,
                Product.cost_price,
                (
                    Product.price - Product.cost_price
                ).label("profit_per_unit")
            )
            .all()
        )

        return [
            {
                "product_id": row.id,
                "product_name": row.name,
                "price": row.price,
                "cost_price": row.cost_price,
                "profit_per_unit": row.profit_per_unit
            }
            for row in results
        ]

    finally:
        db.close()


def get_category_sales():
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.category,
                func.sum(
                    OrderItem.quantity
                ).label("units_sold"),
                func.sum(
                    OrderItem.quantity * OrderItem.unit_price
                ).label("revenue")
            )
            .join(
                OrderItem,
                Product.id == OrderItem.product_id
            )
            .group_by(Product.category)
            .order_by(
                func.sum(
                    OrderItem.quantity * OrderItem.unit_price
                ).desc()
            )
            .all()
        )

        return [
            {
                "category": row.category,
                "units_sold": row.units_sold,
                "revenue": row.revenue
            }
            for row in results
        ]

    finally:
        db.close()


def get_dashboard_summary():

    return {
        "total_revenue": get_total_revenue(),
        "total_orders": get_total_orders(),
        "average_order_value": get_average_order_value(),
        "top_products": get_top_products(),
        "low_stock_products": get_low_stock_products(),
        "product_profit": get_product_profit(),
        "category_sales": get_category_sales()
    }