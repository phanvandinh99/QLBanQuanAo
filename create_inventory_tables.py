"""
Quick migration script to create missing inventory tables (purchase, purchase_item).

Usage (Windows PowerShell):
  venv\Scripts\python.exe create_inventory_tables.py
"""

from shop import app, db
from sqlalchemy import inspect


def ensure_inventory_tables():
    engine = db.engine
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())

    needed = {"supplier", "purchase", "purchase_item"}
    missing = [t for t in needed if t not in existing]

    if not missing:
        print("✅ Inventory tables already exist: purchase, purchase_item")
        return

    print(f"ℹ️ Missing tables: {', '.join(missing)}. Creating...")
    # create_all() will create only the missing tables for defined models
    db.create_all()
    # Ensure purchase.supplier_id exists if purchase existed before
    inspector = inspect(engine)
    purchase_cols = {c['name'] for c in inspector.get_columns('purchase')}
    if 'supplier_id' not in purchase_cols:
        from sqlalchemy import text
        db.session.execute(text('ALTER TABLE purchase ADD COLUMN supplier_id INTEGER NULL'))
        db.session.commit()
        print("➕ Added column purchase.supplier_id")
    print("🎉 Created missing tables successfully.")


if __name__ == "__main__":
    with app.app_context():
        ensure_inventory_tables()


