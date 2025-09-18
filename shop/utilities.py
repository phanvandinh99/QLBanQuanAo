"""
Utility functions for the application
"""

from shop import db
from shop.models import Brand, Category, Rating, Customer, Product
from sqlalchemy import func

def get_brands():
    """Get all brands ordered by name"""
    return Brand.query.order_by(Brand.name.asc()).all()

def get_categories():
    """Get all categories ordered by name descending"""
    return Category.query.order_by(Category.name.desc()).all()

def get_product_ratings():
    """Calculate average rating for each product"""
    # Get all products with their average ratings and count
    ratings = db.session.query(
        Rating.product_id,
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('count')
    ).group_by(Rating.product_id).all()

    # Create a dictionary with product_id as key and [avg_rating, count] as value
    rating_dict = {}
    for rating in ratings:
        rating_dict[rating.product_id] = [float(rating.avg_rating), rating.count]

    return rating_dict

def get_customers():
    """Get all customers"""
    return Customer.query.all()

def generate_invoice_number():
    """Generate unique invoice number"""
    import uuid
    from datetime import datetime

    # Format: INV + YYYYMMDD + 6-char UUID
    date_str = datetime.utcnow().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:6].upper()
    return f"INV{date_str}{unique_id}"

def calculate_cart_total(cart_items):
    """Calculate total price of cart items"""
    total = 0
    for item in cart_items:
        if hasattr(item, 'product') and hasattr(item, 'quantity'):
            total += item.product.discounted_price * item.quantity
    return total

def validate_image_file(filename):
    """Validate image file extension"""
    if not filename:
        return False

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_string(text):
    """Basic string sanitization"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    import re
    return re.sub(r'[<>]', '', str(text).strip())

def format_currency(amount):
    """Format amount as Vietnamese currency"""
    try:
        return f"{int(amount):,} ₫"
    except (ValueError, TypeError):
        return f"{amount} ₫"

def get_popular_products(limit=8):
    """Get popular products based on ratings and stock"""
    return Product.query.filter(
        Product.stock > 0
    ).order_by(
        Product.discount.desc(),
        Product.price.desc()
    ).limit(limit).all()

def get_new_products(limit=8):
    """Get newest products"""
    return Product.query.filter(
        Product.stock > 0
    ).order_by(
        Product.pub_date.desc()
    ).limit(limit).all()

def search_products(query, limit=20):
    """Search products by name"""
    search_term = f"%{query.lower()}%"
    return Product.query.filter(
        Product.name.ilike(search_term),
        Product.stock > 0
    ).limit(limit).all()

def get_products_by_category(category_id, page=1, per_page=12):
    """Get paginated products by category"""
    return Product.query.filter_by(
        category_id=category_id,
        stock__gt=0
    ).paginate(page=page, per_page=per_page, error_out=False)

def get_products_by_brand(brand_id, page=1, per_page=12):
    """Get paginated products by brand"""
    return Product.query.filter_by(
        brand_id=brand_id,
        stock__gt=0
    ).paginate(page=page, per_page=per_page, error_out=False)

def update_product_stock(product_id, quantity_change):
    """Update product stock safely"""
    product = Product.query.get(product_id)
    if product:
        product.stock = max(0, product.stock + quantity_change)
        db.session.commit()
        return True
    return False

def get_customer_orders(customer_id, page=1, per_page=10):
    """Get paginated orders for a customer"""
    from shop.models import Order
    return Order.query.filter_by(
        customer_id=customer_id
    ).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
