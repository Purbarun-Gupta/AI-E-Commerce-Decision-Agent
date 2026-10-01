from datetime import date, timedelta
import random

from db.connection import SessionLocal
from db.models import Customer, Product, Inventory, Order, OrderItem


def seed_customers():
    db = SessionLocal()

    existing_customer = db.query(Customer).first()

    if existing_customer:
        print("Customers already exist. Skipping customer seeding.")
        db.close()
        return

    customers = [
        Customer(
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            location="Kolkata",
            registration_date=date(2026, 1, 10)
        ),
        Customer(
            name="Ananya Singh",
            email="ananya.singh@example.com",
            location="Delhi",
            registration_date=date(2026, 1, 15)
        ),
        Customer(
            name="Arjun Mehta",
            email="arjun.mehta@example.com",
            location="Mumbai",
            registration_date=date(2026, 2, 3)
        ),
        Customer(
            name="Priya Das",
            email="priya.das@example.com",
            location="Bangalore",
            registration_date=date(2026, 2, 18)
        ),
        Customer(
            name="Rohan Gupta",
            email="rohan.gupta@example.com",
            location="Chennai",
            registration_date=date(2026, 3, 2)
        ),
        Customer(
            name="Sneha Roy",
            email="sneha.roy@example.com",
            location="Kolkata",
            registration_date=date(2026, 3, 12)
        ),
        Customer(
            name="Vikram Patel",
            email="vikram.patel@example.com",
            location="Ahmedabad",
            registration_date=date(2026, 4, 5)
        ),
        Customer(
            name="Neha Kapoor",
            email="neha.kapoor@example.com",
            location="Pune",
            registration_date=date(2026, 4, 20)
        ),
        Customer(
            name="Aman Verma",
            email="aman.verma@example.com",
            location="Hyderabad",
            registration_date=date(2026, 5, 8)
        ),
        Customer(
            name="Kavya Nair",
            email="kavya.nair@example.com",
            location="Kochi",
            registration_date=date(2026, 5, 25)
        )
    ]

    db.add_all(customers)
    db.commit()
    db.close()

    print("10 customers added successfully!")


def seed_products():
    db = SessionLocal()

    existing_product = db.query(Product).first()

    if existing_product:
        print("Products already exist. Skipping product seeding.")
        db.close()
        return

    product_names = [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "USB-C Cable",
        "Laptop Stand",
        "Bluetooth Speaker",
        "Wireless Headphones",
        "Smart Watch",
        "Webcam",
        "Power Bank",
        "External SSD",
        "Gaming Mouse",
        "Monitor",
        "Laptop Backpack",
        "Phone Charger",
        "Tablet",
        "Smartphone",
        "Desk Lamp",
        "Earbuds",
        "HDMI Cable",
        "Graphics Tablet"
    ]

    categories = [
        "Electronics",
        "Accessories",
        "Computers"
    ]

    products = []

    for name in product_names:
        cost_price = random.randint(300, 50000)
        price = cost_price + random.randint(100, 15000)

        product = Product(
            name=name,
            category=random.choice(categories),
            price=price,
            cost_price=cost_price
        )

        products.append(product)

    db.add_all(products)
    db.commit()
    db.close()

    print("20 products added successfully!")

def seed_inventory():
    db = SessionLocal()

    existing_inventory = db.query(Inventory).first()

    if existing_inventory:
        print("Inventory already exists. Skipping inventory seeding.")
        db.close()
        return

    products = db.query(Product).all()

    inventory_records = []

    for product in products:
        initial_stock = random.randint(50, 150)

        reorder_level = random.randint(10, 30)

        inventory = Inventory(
        product_id=product.id,
        initial_stock=initial_stock,
        current_stock=initial_stock,
        reorder_level=reorder_level,
        last_updated=date.today()
    )

        inventory_records.append(inventory)

    db.add_all(inventory_records)
    db.commit()
    db.close()

    print(f"{len(inventory_records)} inventory records added successfully!")

def seed_orders():
    db = SessionLocal()

    existing_order = db.query(Order).first()

    if existing_order:
        print("Orders already exist. Skipping order seeding.")
        db.close()
        return

    customers = db.query(Customer).all()
    products = db.query(Product).all()

    if not customers:
        print("No customers found.")
        db.close()
        return

    if not products:
        print("No products found.")
        db.close()
        return

    for _ in range(50):

        customer = random.choice(customers)

        order_date = date.today() - timedelta(
            days=random.randint(0, 180)
        )

        order = Order(
            customer_id=customer.id,
            order_date=order_date,
            total_amount=0,
            status=random.choice([
                "Completed",
                "Completed",
                "Completed",
                "Pending",
                "Cancelled"
            ])
        )

        db.add(order)

        # Generate the order ID
        db.flush()

        total_amount = 0

        selected_products = random.sample(
            products,
            random.randint(1, 4)
        )

        for product in selected_products:

            quantity = random.randint(1, 5)

            unit_price = product.price

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price
            )

            db.add(order_item)

            total_amount += quantity * unit_price

        order.total_amount = total_amount

    db.commit()
    db.close()

    print("50 orders and their order items added successfully!")

def update_inventory_after_sales():
    db = SessionLocal()

    inventory_records = db.query(Inventory).all()

    for inventory in inventory_records:

        order_items = (
            db.query(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                OrderItem.product_id == inventory.product_id,
                Order.status == "Completed"
            )
            .all()
        )

        total_sold = sum(
            item.quantity for item in order_items
        )

        inventory.current_stock = max(
            0,
            inventory.initial_stock - total_sold
        )

        inventory.last_updated = date.today()

    db.commit()
    db.close()

    print("Inventory updated based on completed sales!")

if __name__ == "__main__":
    seed_customers()
    seed_products()
    seed_inventory()
    seed_orders()
    update_inventory_after_sales()