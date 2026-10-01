from db.connection import SessionLocal
from db.models import Product, Inventory, OrderItem, Order


db = SessionLocal()

products = db.query(Product).all()

for product in products:

    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == product.id)
        .first()
    )

    sold_quantity = (
    db.query(OrderItem)
    .join(Order, Order.id == OrderItem.order_id)
    .filter(
        OrderItem.product_id == product.id,
        Order.status == "Completed"
    )
    .all()
)

    total_sold = sum(
        item.quantity for item in sold_quantity
    )

    print(
        f"{product.name}: "
        f"Initial={inventory.initial_stock}, "
        f"Sold={total_sold}, "
        f"Current={inventory.current_stock}"
    )

db.close()