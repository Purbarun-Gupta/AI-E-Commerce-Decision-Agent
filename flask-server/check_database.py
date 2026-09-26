from sqlalchemy import inspect

from db.connection import engine


inspector = inspect(engine)

tables = inspector.get_table_names()

print("\nTables in database:")
print("===================")

for table in tables:
    print(f"\nTable: {table}")

    columns = inspector.get_columns(table)

    for column in columns:
        print(
            f"  - {column['name']} "
            f"({column['type']})"
        )