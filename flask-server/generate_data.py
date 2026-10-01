from datetime import date, timedelta
import random

from db.connection import SessionLocal
from db.models import (
    Customer,
    Product,
    Inventory,
    Order,
    OrderItem
)


# =========================
# DATASET SIZE
# =========================

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 5000

def generate_customers(db):
    customers = []

    first_names = [
        "Aarav", "Vivaan", "Aditya", "Arjun", "Rahul",
        "Rohan", "Aman", "Vikram", "Karan", "Ankit",
        "Priya", "Ananya", "Sneha", "Neha", "Kavya",
        "Pooja", "Isha", "Riya", "Meera", "Aditi"
    ]

    last_names = [
        "Sharma", "Singh", "Gupta", "Patel", "Kumar",
        "Das", "Roy", "Mehta", "Verma", "Kapoor",
        "Nair", "Joshi", "Chatterjee", "Reddy", "Malhotra"
    ]

    locations = [
        "Kolkata",
        "Delhi",
        "Mumbai",
        "Bangalore",
        "Chennai",
        "Hyderabad",
        "Pune",
        "Ahmedabad",
        "Jaipur",
        "Lucknow"
    ]

    for i in range(NUM_CUSTOMERS):

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        name = f"{first_name} {last_name}"

        email = f"customer{i + 1}@example.com"

        registration_date = (
            date.today()
            - timedelta(days=random.randint(30, 1000))
        )

        customer = Customer(
            name=name,
            email=email,
            location=random.choice(locations),
            registration_date=registration_date
        )

        customers.append(customer)

    db.add_all(customers)
    db.commit()

    print(f"{len(customers)} customers generated.")

    return customers

def generate_products(db):
    products = []

    product_templates = [
        ("Wireless Mouse", "Accessories"),
        ("Mechanical Keyboard", "Accessories"),
        ("USB-C Cable", "Accessories"),
        ("Laptop Stand", "Accessories"),
        ("Bluetooth Speaker", "Electronics"),
        ("Wireless Headphones", "Electronics"),
        ("Smart Watch", "Electronics"),
        ("Webcam", "Electronics"),
        ("Power Bank", "Electronics"),
        ("External SSD", "Computers"),
        ("Gaming Mouse", "Accessories"),
        ("Monitor", "Computers"),
        ("Laptop Backpack", "Accessories"),
        ("Phone Charger", "Accessories"),
        ("Tablet", "Computers"),
        ("Smartphone", "Electronics"),
        ("Desk Lamp", "Home"),
        ("Earbuds", "Electronics"),
        ("HDMI Cable", "Accessories"),
        ("Graphics Tablet", "Computers")
    ]

    for i in range(NUM_PRODUCTS):

        template_name, category = random.choice(product_templates)

        cost_price = random.randint(300, 30000)

        price = cost_price + random.randint(100, 15000)

        product = Product(
            name=f"{template_name} {i + 1}",
            category=category,
            price=price,
            cost_price=cost_price
        )

        products.append(product)

    db.add_all(products)
    db.commit()

    print(f"{len(products)} products generated.")

    return products

def generate_inventory(db, products):
    inventory_records = []

    for product in products:

        initial_stock = random.randint(50, 300)

        reorder_level = random.randint(20, 60)

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

    print(f"{len(inventory_records)} inventory records generated.")

    return inventory_records

def generate_orders(db, customers, products):
    orders = []

    for _ in range(NUM_ORDERS):

        customer = random.choice(customers)

        order_date = (
            date.today()
            - timedelta(days=random.randint(0, 365))
        )

        status = random.choices(
            [
                "Completed",
                "Pending",
                "Cancelled"
            ],
            weights=[
                75,
                15,
                10
            ],
            k=1
        )[0]

        order = Order(
            customer_id=customer.id,
            order_date=order_date,
            total_amount=0,
            status=status
        )

        orders.append(order)

    db.add_all(orders)
    db.commit()

    print(f"{len(orders)} orders generated.")

    return orders

def generate_order_items(db, orders, products):
    order_items = []

    for order in orders:

        # Each order contains 1–5 different products
        number_of_products = random.randint(1, 5)

        selected_products = random.sample(
            products,
            number_of_products
        )

        total_amount = 0

        for product in selected_products:

            quantity = random.randint(1, 5)

            unit_price = product.price

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price
            )

            order_items.append(order_item)

            total_amount += quantity * unit_price

        order.total_amount = total_amount

    db.add_all(order_items)
    db.commit()

    print(f"{len(order_items)} order items generated.")

    return order_items

def update_inventory(db):
    inventory_records = db.query(Inventory).all()

    for inventory in inventory_records:

        completed_items = (
            db.query(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                OrderItem.product_id == inventory.product_id,
                Order.status == "Completed"
            )
            .all()
        )

        total_sold = sum(
            item.quantity for item in completed_items
        )

        inventory.current_stock = max(
            0,
            inventory.initial_stock - total_sold
        )

        inventory.last_updated = date.today()

    db.commit()

    print("Inventory updated based on completed sales.")

def main():
    db = SessionLocal()

    try:
        print("Starting synthetic data generation...")
        print()

        # 1. Generate customers
        customers = generate_customers(db)

        # 2. Generate products
        products = generate_products(db)

        # 3. Generate inventory
        generate_inventory(db, products)

        # 4. Generate orders
        orders = generate_orders(db, customers, products)

        # 5. Generate order items
        generate_order_items(db, orders, products)

        # 6. Update inventory based on completed sales
        update_inventory(db)

        print()
        print("Synthetic data generation completed successfully!")

    except Exception as e:
        db.rollback()
        print()
        print("ERROR:", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()    