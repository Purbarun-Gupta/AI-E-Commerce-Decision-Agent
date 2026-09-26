from db.connection import engine, Base
from db.models import Customer, Product, Order, OrderItem, Inventory


Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")