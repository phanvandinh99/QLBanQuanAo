"""
Performance optimization utilities
"""

from flask import current_app, g
from shop import db
import time
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available, performance monitoring limited")

class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def optimize_product_queries():
        """Add database indexes and optimize queries for products"""
        # This would be run during migration
        # SQL commands to add indexes:

        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_product_name ON product (name);",
            "CREATE INDEX IF NOT EXISTS idx_product_category ON product (category_id);",
            "CREATE INDEX IF NOT EXISTS idx_product_brand ON product (brand_id);",
            "CREATE INDEX IF NOT EXISTS idx_product_stock ON product (stock);",
            "CREATE INDEX IF NOT EXISTS idx_product_pub_date ON product (pub_date);",
            "CREATE INDEX IF NOT EXISTS idx_product_price ON product (price);",

            "CREATE INDEX IF NOT EXISTS idx_customer_email ON customer (email);",
            "CREATE INDEX IF NOT EXISTS idx_customer_username ON customer (username);",

            "CREATE INDEX IF NOT EXISTS idx_order_customer ON order (customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_order_created_at ON order (created_at);",
            "CREATE INDEX IF NOT EXISTS idx_order_status ON order (status);",

            "CREATE INDEX IF NOT EXISTS idx_rating_product ON rating (product_id);",
            "CREATE INDEX IF NOT EXISTS idx_rating_customer ON rating (customer_id);",

            "CREATE INDEX IF NOT EXISTS idx_article_status ON article (status);",
            "CREATE INDEX IF NOT EXISTS idx_article_created_at ON article (created_at);",
        ]

        return indexes_sql

    @staticmethod
    def get_products_with_ratings(page=1, per_page=12):
        """Optimized query to get products with their ratings"""
        from shop.models import Product, Rating
        from sqlalchemy import func

        # Use subquery for better performance
        rating_subquery = db.session.query(
            Rating.product_id,
            func.avg(Rating.rating).label('avg_rating'),
            func.count(Rating.id).label('rating_count')
        ).group_by(Rating.product_id).subquery()

        products = db.session.query(
            Product,
            rating_subquery.c.avg_rating,
            rating_subquery.c.rating_count
        ).outerjoin(
            rating_subquery, Product.id == rating_subquery.c.product_id
        ).filter(
            Product.stock > 0
        ).order_by(
            Product.pub_date.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return products

class ImageOptimizer:
    """Image optimization utilities"""

    @staticmethod
    def optimize_image_on_upload(image_path, max_width=800, max_height=600, quality=85):
        """Optimize uploaded images"""
        try:
            from PIL import Image
            import os

            if not os.path.exists(image_path):
                return False

            # Open image
            img = Image.open(image_path)

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.LANCZOS)

            # Save with optimization
            img.save(image_path, 'JPEG', quality=quality, optimize=True)

            return True

        except Exception as e:
            current_app.logger.error(f"Image optimization failed: {e}")
            return False

    @staticmethod
    def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
        """Create thumbnail for image"""
        try:
            from PIL import Image
            import os

            if not os.path.exists(image_path):
                return False

            # Open image
            img = Image.open(image_path)

            # Create thumbnail
            img.thumbnail(size, Image.LANCZOS)

            # Ensure directory exists
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)

            return True

        except Exception as e:
            current_app.logger.error(f"Thumbnail creation failed: {e}")
            return False

class PerformanceMonitor:
    """Performance monitoring utilities"""

    @staticmethod
    def start_timer():
        """Start performance timer"""
        g.start_time = time.time()

    @staticmethod
    def end_timer():
        """End performance timer and log duration"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            current_app.logger.info(".4f")
            return duration
        return None

    @staticmethod
    def get_system_stats():
        """Get system performance statistics"""
        if not PSUTIL_AVAILABLE:
            return {'status': 'psutil not available'}

        try:
            stats = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'process_memory_mb': psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            }
            return stats
        except Exception as e:
            current_app.logger.error(f"Could not get system stats: {e}")
            return {}

    @staticmethod
    def log_slow_queries(threshold=1.0):
        """Log slow database queries (SQLAlchemy event listener)"""
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop()
            if total > threshold:
                current_app.logger.warning(".4f")

class DatabaseOptimizer:
    """Database optimization utilities"""

    @staticmethod
    def get_query_plan(sql_query):
        """Get EXPLAIN plan for a query (MySQL)"""
        try:
            result = db.session.execute(f"EXPLAIN {sql_query}")
            return [dict(row) for row in result]
        except Exception as e:
            current_app.logger.error(f"Could not get query plan: {e}")
            return []

    @staticmethod
    def analyze_table(table_name):
        """Analyze table for optimization"""
        try:
            db.session.execute(f"ANALYZE TABLE {table_name}")
            return True
        except Exception as e:
            current_app.logger.error(f"Could not analyze table {table_name}: {e}")
            return False

    @staticmethod
    def optimize_table(table_name):
        """Optimize table"""
        try:
            db.session.execute(f"OPTIMIZE TABLE {table_name}")
            return True
        except Exception as e:
            current_app.logger.error(f"Could not optimize table {table_name}: {e}")
            return False

class LazyLoader:
    """Lazy loading utilities for better performance"""

    @staticmethod
    def load_related_data(query, *relationships):
        """Load related data efficiently"""
        for relationship in relationships:
            query = query.options(db.joinedload(relationship))
        return query

    @staticmethod
    def batch_load_products(product_ids):
        """Batch load products by IDs"""
        from shop.models import Product
        return Product.query.filter(Product.id.in_(product_ids)).all()

    @staticmethod
    def prefetch_product_ratings(products):
        """Prefetch ratings for multiple products"""
        from shop.models import Rating
        product_ids = [p.id for p in products]

        ratings = Rating.query.filter(Rating.product_id.in_(product_ids)).all()

        # Group ratings by product
        ratings_by_product = {}
        for rating in ratings:
            if rating.product_id not in ratings_by_product:
                ratings_by_product[rating.product_id] = []
            ratings_by_product[rating.product_id].append(rating)

        # Attach ratings to products
        for product in products:
            product.ratings_data = ratings_by_product.get(product.id, [])

        return products
