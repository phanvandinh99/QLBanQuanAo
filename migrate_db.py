#!/usr/bin/env python3
"""Database migration script to add new columns to customer_order table"""

from shop import db
from sqlalchemy import text

def migrate_database():
    """Add missing columns to customer_order table"""
    try:
        with db.engine.connect() as conn:
            # Check current table structure
            result = conn.execute(text('DESCRIBE customer_order'))
            columns = [row[0] for row in result.fetchall()]
            print('Current columns:', columns)

            # Check if new columns exist
            missing_columns = []
            if 'delivery_method' not in columns:
                missing_columns.append('delivery_method')
            if 'pickup_store' not in columns:
                missing_columns.append('pickup_store')

            print('Missing columns:', missing_columns)

            # Add missing columns
            if missing_columns:
                print('Adding missing columns...')

                if 'delivery_method' in missing_columns:
                    conn.execute(text("ALTER TABLE customer_order ADD COLUMN delivery_method VARCHAR(20) DEFAULT 'home_delivery'"))
                    print('✅ Added delivery_method column')

                if 'pickup_store' in missing_columns:
                    conn.execute(text("ALTER TABLE customer_order ADD COLUMN pickup_store VARCHAR(200) DEFAULT ''"))
                    print('✅ Added pickup_store column')

                conn.commit()
                print('🎉 Migration completed successfully!')
            else:
                print('✅ All columns already exist')

    except Exception as e:
        print('❌ Migration error:', e)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_database()
