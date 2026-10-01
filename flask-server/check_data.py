from db.connection import SessionLocal
from db.models import Customer, Product, Inventory, Order, OrderItem


db = SessionLocal()

print("Customers:", db.query(Customer).count())
print("Products:", db.query(Product).count())
print("Inventory:", db.query(Inventory).count())
print("Orders:", db.query(Order).count())
print("Order Items:", db.query(OrderItem).count())

db.close()