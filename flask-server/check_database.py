from sqlalchemy import inspect
from db.connection import engine

inspector = inspect(engine)

tables = inspector.get_table_names()

print("Tables in database:")
for table in tables:
    print("-", table)