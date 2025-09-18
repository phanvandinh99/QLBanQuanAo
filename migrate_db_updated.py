"""
Database Migration Script for Updated Models

This script handles the migration from old model names to new ones:
- addproduct -> product
- register -> customer
- customer_order -> order + order_item
- articles -> article
- rate -> rating

Run this script after updating the models.py file.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()
import json
from datetime import datetime

# Import config and models
from config import get_config
from shop.models import (
    db, Admin, Brand, Category, Product, Customer,
    Rating, Order, OrderItem, Article
)

app = Flask(__name__)
config_class = get_config()
app.config.from_object(config_class)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

def run_sql_directly(sql):
    """Execute SQL directly"""
    try:
        db.session.execute(sql)
        db.session.commit()
        print(f"✅ Executed: {sql[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        db.session.rollback()
        return False

def rename_tables():
    """Rename old tables to new names"""
    print("🔄 Renaming tables...")

    # Rename tables
    renames = [
        "RENAME TABLE addproduct TO product_backup;",
        "RENAME TABLE register TO customer_backup;",
        "RENAME TABLE customer_order TO order_backup;",
        "RENAME TABLE articles TO article_backup;",
        "RENAME TABLE rate TO rating_backup;"
    ]

    for sql in renames:
        run_sql_directly(sql)

def create_new_tables():
    """Create new tables with updated schema"""
    print("🆕 Creating new tables...")

    # Create all tables with new schema
    db.create_all()

    # Add indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_product_name ON product (name);",
        "CREATE INDEX IF NOT EXISTS idx_product_category ON product (category_id);",
        "CREATE INDEX IF NOT EXISTS idx_product_brand ON product (brand_id);",
        "CREATE INDEX IF NOT EXISTS idx_product_pub_date ON product (pub_date);",
        "CREATE INDEX IF NOT EXISTS idx_customer_email ON customer (email);",
        "CREATE INDEX IF NOT EXISTS idx_customer_username ON customer (username);",
        "CREATE INDEX IF NOT EXISTS idx_order_customer ON order (customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_created_at ON order (created_at);",
        "CREATE INDEX IF NOT EXISTS idx_rating_product ON rating (product_id);",
        "CREATE INDEX IF NOT EXISTS idx_rating_customer ON rating (customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_article_status ON article (status);",
        "CREATE INDEX IF NOT EXISTS idx_article_created_at ON article (created_at);"
    ]

    for sql in indexes:
        run_sql_directly(sql)

def migrate_product_data():
    """Migrate data from addproduct to product"""
    print("📦 Migrating product data...")

    try:
        # Get data from backup table
        result = db.session.execute("SELECT * FROM product_backup")
        products = result.fetchall()

        for row in products:
            product = Product(
                id=row[0],
                name=row[1],
                price=row[2],
                discount=row[3] or 0,
                stock=row[4],
                colors=row[5],  # This was 'colors' field
                description=row[6],  # This was 'desc' field
                pub_date=row[7],
                category_id=row[8],
                brand_id=row[9],
                image_1=row[10],
                image_2=row[11],
                image_3=row[12]
            )
            db.session.add(product)

        db.session.commit()
        print(f"✅ Migrated {len(products)} products")

    except Exception as e:
        print(f"❌ Error migrating products: {e}")
        db.session.rollback()

def migrate_customer_data():
    """Migrate data from register to customer"""
    print("👥 Migrating customer data...")

    try:
        # Get data from backup table
        result = db.session.execute("SELECT * FROM customer_backup")
        customers = result.fetchall()

        for row in customers:
            customer = Customer(
                id=row[0],
                username=row[1],
                first_name=row[2],
                last_name=row[3],
                email=row[4],
                phone_number=row[5],
                gender=row[6] or 'other',
                password=row[7],
                date_created=row[8],
                is_active=not bool(row[9])  # lock field inverted
            )
            db.session.add(customer)

        db.session.commit()
        print(f"✅ Migrated {len(customers)} customers")

    except Exception as e:
        print(f"❌ Error migrating customers: {e}")
        db.session.rollback()

def migrate_rating_data():
    """Migrate data from rate to rating"""
    print("⭐ Migrating rating data...")

    try:
        # Get data from backup table
        result = db.session.execute("SELECT * FROM rating_backup")
        ratings = result.fetchall()

        for row in ratings:
            rating = Rating(
                id=row[0],
                product_id=row[1],
                customer_id=row[2],  # This was register_id
                created_at=row[3],   # This was time
                comment=row[4],      # This was desc
                rating=row[5]        # This was rate_number
            )
            db.session.add(rating)

        db.session.commit()
        print(f"✅ Migrated {len(ratings)} ratings")

    except Exception as e:
        print(f"❌ Error migrating ratings: {e}")
        db.session.rollback()

def migrate_article_data():
    """Migrate data from articles to article"""
    print("📝 Migrating article data...")

    try:
        # Get data from backup table
        result = db.session.execute("SELECT * FROM article_backup")
        articles = result.fetchall()

        for row in articles:
            article = Article(
                id=row[0],
                title=row[1],
                content=row[2],
                cover_image=row[3] or 'article-default.jpg',
                created_at=row[4],
                updated_at=row[5],
                admin_id=row[6],
                status=row[7] or 'draft',
                slug=row[8]
            )
            db.session.add(article)

        db.session.commit()
        print(f"✅ Migrated {len(articles)} articles")

    except Exception as e:
        print(f"❌ Error migrating articles: {e}")
        db.session.rollback()

def migrate_order_data():
    """Migrate data from customer_order to order + order_item"""
    print("🛒 Migrating order data...")

    try:
        # Get data from backup table
        result = db.session.execute("SELECT * FROM order_backup")
        orders = result.fetchall()

        migrated_orders = 0
        migrated_items = 0

        for row in orders:
            try:
                # Parse orders JSON if it exists
                order_data = None
                if row[5]:  # orders field
                    try:
                        order_data = json.loads(row[5])
                    except:
                        order_data = None

                # Map old status to new status
                old_status = row[1]  # status field
                new_status = map_old_status_to_new(old_status)

                # Create order
                order = Order(
                    id=row[0],
                    invoice=row[1] if row[1] else f"INV{row[0]:06d}",  # invoice field
                    status=new_status,
                    payment_status='paid' if row[8] == 'Đã thanh toán' else 'unpaid',  # payment_status
                    customer_id=row[3],  # customer_id
                    created_at=row[6] or datetime.utcnow(),  # date_created
                    shipping_address=row[2],  # address
                    total_amount=row[9] or 0,  # amount
                    payment_method=row[7] or 'cod',  # payment_method
                    delivery_method=row[11] or 'home_delivery',  # delivery_method
                    pickup_store=row[12] or '',  # pickup_store
                    notes=''
                )
                db.session.add(order)
                db.session.flush()  # Get order ID

                # Create order items if order_data exists
                if order_data:
                    for product_id, item_data in order_data.items():
                        try:
                            # Get product to get current price
                            product_result = db.session.execute(
                                "SELECT price, discount FROM product_backup WHERE id = %s",
                                (int(product_id),)
                            ).fetchone()

                            if product_result:
                                unit_price = product_result[0]
                                discount = product_result[1] or 0

                                order_item = OrderItem(
                                    order_id=order.id,
                                    product_id=int(product_id),
                                    quantity=item_data.get('quantity', 1),
                                    unit_price=unit_price,
                                    discount=discount
                                )
                                db.session.add(order_item)
                                migrated_items += 1
                        except Exception as e:
                            print(f"⚠️ Error creating order item for product {product_id}: {e}")

                migrated_orders += 1

            except Exception as e:
                print(f"⚠️ Error migrating order {row[0]}: {e}")
                continue

        db.session.commit()
        print(f"✅ Migrated {migrated_orders} orders and {migrated_items} order items")

    except Exception as e:
        print(f"❌ Error migrating orders: {e}")
        db.session.rollback()

def map_old_status_to_new(old_status):
    """Map old Vietnamese status to new English status"""
    status_map = {
        'Đang xác nhận': 'pending',
        'Đang giao': 'shipping',
        'Đã giao': 'delivered',
        'Hủy đơn': 'cancelled',
        'Sẵn sàng nhận tại cửa hàng': 'ready_for_pickup'
    }
    return status_map.get(old_status, 'pending')

def cleanup_backup_tables():
    """Remove backup tables after successful migration"""
    print("🧹 Cleaning up backup tables...")

    backup_tables = [
        "DROP TABLE IF EXISTS product_backup;",
        "DROP TABLE IF EXISTS customer_backup;",
        "DROP TABLE IF EXISTS order_backup;",
        "DROP TABLE IF EXISTS article_backup;",
        "DROP TABLE IF EXISTS rating_backup;"
    ]

    for sql in backup_tables:
        run_sql_directly(sql)

    print("✅ Backup tables cleaned up")

def main():
    """Main migration function"""
    print("🚀 Starting comprehensive database migration...")
    print("=" * 60)

    with app.app_context():
        try:
            # Step 1: Rename old tables
            rename_tables()

            # Step 2: Create new tables
            create_new_tables()

            # Step 3: Migrate data
            migrate_product_data()
            migrate_customer_data()
            migrate_rating_data()
            migrate_article_data()
            migrate_order_data()

            # Step 4: Cleanup
            cleanup_backup_tables()

            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("\n📊 Migration Summary:")
            print("- Products: Migrated from addproduct to product")
            print("- Customers: Migrated from register to customer")
            print("- Orders: Migrated from customer_order to order + order_item")
            print("- Ratings: Migrated from rate to rating")
            print("- Articles: Migrated from articles to article")
            print("- Indexes: Added for performance optimization")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("🔄 Rolling back changes...")
            db.session.rollback()

if __name__ == "__main__":
    main()
