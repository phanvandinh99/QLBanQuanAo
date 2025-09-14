#!/usr/bin/env python3
"""
Add payment_status column to customer_order table
"""

from shop import app, db

def update_database():
    with app.app_context():
        try:
            # Check if payment_status column exists
            result = db.engine.execute('SELECT payment_status FROM customer_order LIMIT 1')
            print('payment_status column already exists')
        except:
            print('Adding payment_status column...')
            try:
                db.engine.execute('ALTER TABLE customer_order ADD COLUMN payment_status VARCHAR(20) DEFAULT \'Chưa thanh toán\'')
                print('✅ payment_status column added')
            except Exception as e:
                print(f'Error adding column: {e}')

if __name__ == "__main__":
    update_database()
