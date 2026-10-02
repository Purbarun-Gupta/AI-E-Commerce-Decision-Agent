from sqlalchemy import func

from db.connection import get_db
from db.models import Customer, Order, OrderItem, Product, Inventory


def get_total_revenue():
    db = next(get_db())

    try:
        result = (
            db.query(
                func.coalesce(
                    func.sum(Order.total_amount),
                    0
                )
            )
            .scalar()
        )

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
        result = (
            db.query(
                func.coalesce(
                    func.avg(Order.total_amount),
                    0
                )
            )
            .scalar()
        )

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
                func.sum(
                    OrderItem.quantity
                ).label("units_sold"),
                func.sum(
                    OrderItem.quantity *
                    OrderItem.unit_price
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
                func.sum(
                    OrderItem.quantity
                ).desc()
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
                Inventory.current_stock <=
                Inventory.reorder_level
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

def get_inventory_risk():
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.id,
                Product.name,
                Product.category,
                Inventory.current_stock,
                Inventory.reorder_level,
                Inventory.initial_stock
            )
            .join(
                Inventory,
                Product.id == Inventory.product_id
            )
            .all()
        )

        inventory_risk = []

        for row in results:

            if row.current_stock <= 0:
                risk_level = "CRITICAL"

            elif row.current_stock <= row.reorder_level:
                risk_level = "HIGH"

            elif row.current_stock <= row.reorder_level * 2:
                risk_level = "MEDIUM"

            else:
                risk_level = "LOW"

            shortage = max(
                row.reorder_level - row.current_stock,
                0
            )

            inventory_risk.append({
                "product_id": row.id,
                "product_name": row.name,
                "category": row.category,
                "current_stock": row.current_stock,
                "initial_stock": row.initial_stock,
                "reorder_level": row.reorder_level,
                "shortage": shortage,
                "risk_level": risk_level
            })

        return inventory_risk

    finally:
        db.close()

def get_sales_trends():
    db = next(get_db())

    try:
        results = (
            db.query(
                Order.order_date,
                func.count(Order.id).label("orders"),
                func.sum(Order.total_amount).label("revenue")
            )
            .filter(
                Order.status == "Completed"
            )
            .group_by(
                Order.order_date
            )
            .order_by(
                Order.order_date
            )
            .all()
        )

        sales_trends = []

        for row in results:

            if row.orders > 0:
                average_order_value = (
                    row.revenue / row.orders
                )
            else:
                average_order_value = 0

            sales_trends.append({
                "date": row.order_date.isoformat(),
                "orders": row.orders,
                "revenue": row.revenue,
                "average_order_value": round(
                    average_order_value,
                    2
                )
            })

        return sales_trends

    finally:
        db.close()       

def get_customer_metrics():
    db = next(get_db())

    try:
        results = (
            db.query(
                Customer.id,
                Customer.name,
                func.count(Order.id).label("total_orders"),
                func.coalesce(
                    func.sum(Order.total_amount),
                    0
                ).label("total_spent")
            )
            .join(
                Order,
                Customer.id == Order.customer_id
            )
            .filter(
                Order.status == "Completed"
            )
            .group_by(
                Customer.id,
                Customer.name
            )
            .order_by(
                func.sum(Order.total_amount).desc()
            )
            .all()
        )

        customer_metrics = []

        for row in results:

            if row.total_orders > 0:
                average_order_value = (
                    row.total_spent /
                    row.total_orders
                )
            else:
                average_order_value = 0

            customer_metrics.append({
                "customer_id": row.id,
                "customer_name": row.name,
                "total_orders": row.total_orders,
                "total_spent": row.total_spent,
                "average_order_value": round(
                    average_order_value,
                    2
                )
            })

        return customer_metrics

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
                    Product.price -
                    Product.cost_price
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


def get_product_performance():
    db = next(get_db())

    try:
        results = (
            db.query(
                Product.id,
                Product.name,
                func.coalesce(
                    func.sum(OrderItem.quantity),
                    0
                ).label("units_sold"),
                func.coalesce(
                    func.sum(
                        OrderItem.quantity *
                        OrderItem.unit_price
                    ),
                    0
                ).label("revenue"),
                func.coalesce(
                    func.sum(
                        OrderItem.quantity *
                        Product.cost_price
                    ),
                    0
                ).label("total_cost")
            )
            .join(
                OrderItem,
                Product.id == OrderItem.product_id
            )
            .join(
                Order,
                Order.id == OrderItem.order_id
            )
            .filter(
                Order.status == "Completed"
            )
            .group_by(
                Product.id,
                Product.name
            )
            .all()
        )

        performance = []

        for row in results:
            total_profit = row.revenue - row.total_cost

            if row.revenue > 0:
                profit_margin = (
                    total_profit / row.revenue
                ) * 100
            else:
                profit_margin = 0

            performance.append(
                {
                    "product_id": row.id,
                    "product_name": row.name,
                    "units_sold": row.units_sold,
                    "revenue": row.revenue,
                    "total_cost": row.total_cost,
                    "total_profit": total_profit,
                    "profit_margin": round(
                        profit_margin,
                        2
                    )
                }
            )

        return performance

    finally:
        db.close()

def get_total_profit():
    db = next(get_db())

    try:
        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        OrderItem.quantity *
                        (
                            OrderItem.unit_price -
                            Product.cost_price
                        )
                    ),
                    0
                )
            )
            .join(
                Product,
                Product.id == OrderItem.product_id
            )
            .join(
                Order,
                Order.id == OrderItem.order_id
            )
            .filter(
                Order.status == "Completed"
            )
            .scalar()
        )

        return result

    finally:
        db.close()


def get_profit_margin():
    db = next(get_db())

    try:
        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        OrderItem.quantity *
                        (
                            OrderItem.unit_price -
                            Product.cost_price
                        )
                    ),
                    0
                ).label("total_profit"),
                func.coalesce(
                    func.sum(
                        OrderItem.quantity *
                        OrderItem.unit_price
                    ),
                    0
                ).label("total_revenue")
            )
            .join(
                Product,
                Product.id == OrderItem.product_id
            )
            .join(
                Order,
                Order.id == OrderItem.order_id
            )
            .filter(
                Order.status == "Completed"
            )
            .first()
        )

        total_profit = result.total_profit
        total_revenue = result.total_revenue

        if total_revenue > 0:
            margin = (
                total_profit /
                total_revenue
            ) * 100
        else:
            margin = 0

        return round(margin, 2)

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
                    OrderItem.quantity *
                    OrderItem.unit_price
                ).label("revenue")
            )
            .join(
                OrderItem,
                Product.id == OrderItem.product_id
            )
            .group_by(
                Product.category
            )
            .order_by(
                func.sum(
                    OrderItem.quantity *
                    OrderItem.unit_price
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
        "product_performance": get_product_performance(),
        "category_sales": get_category_sales(),
        "customer_metrics": get_customer_metrics()
    }


if __name__ == "__main__":
    data = get_product_performance()

    for product in data:
        print(product)