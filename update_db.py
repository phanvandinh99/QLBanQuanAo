#!/usr/bin/env python3
"""
Script để update database thêm cột mới
"""

from shop import app, db

def update_database():
    """Add new columns to customer_order table"""
    with app.app_context():
        try:
            # Check if columns exist by trying to query
            test_order = db.session.query(db.text("SELECT amount, payment_method FROM customer_order LIMIT 1")).first()
            print("Columns already exist")
        except:
            print("Adding new columns...")

            try:
                # Add amount column
                db.engine.execute('ALTER TABLE customer_order ADD COLUMN amount DECIMAL(10,2) DEFAULT 0')
                print("Added amount column")
            except Exception as e:
                print(f"Error adding amount column: {e}")

            try:
                # Add payment_method column
                db.engine.execute("ALTER TABLE customer_order ADD COLUMN payment_method VARCHAR(20) DEFAULT 'cod'")
                print("Added payment_method column")
            except Exception as e:
                print(f"Error adding payment_method column: {e}")

            print("Database update completed!")

if __name__ == "__main__":
    update_database()
