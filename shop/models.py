from shop import db
from flask_login import UserMixin
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), nullable=False)
    profile = db.Column(db.String(180), default='profile.jpg')

    def __repr__(self):
        return f'<Admin {self.username}>'

class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    colors = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False, index=True)

    # Relationships
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))
    brand = db.relationship('Brand', backref=db.backref('products', lazy='dynamic'))

    # Image fields
    image_1 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_2 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_3 = db.Column(db.String(150), nullable=False, default='image.jpg')

    def __repr__(self):
        return f'<Product {self.name}>'

    @property
    def discounted_price(self):
        """Calculate discounted price"""
        if self.discount > 0:
            return self.price * (100 - self.discount) / 100
        return self.price

    @property
    def is_available(self):
        """Check if product is available for purchase"""
        return self.stock > 0

class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    gender = db.Column(db.String(10))  # male, female, other
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Customer {self.username}>'

    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"

    def is_locked(self):
        """Check if customer account is locked"""
        return not self.is_active

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    # Relationships
    product = db.relationship('Product', backref=db.backref('ratings', lazy='dynamic'))
    customer = db.relationship('Customer', backref=db.backref('ratings', lazy='dynamic'))

    def __repr__(self):
        return f'<Rating {self.rating} by {self.customer.username} for {self.product.name}>'

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'shipping', 'delivered', 'cancelled', 'ready_for_pickup'), default='pending')
    payment_status = db.Column(db.Enum('unpaid', 'paid', 'refunded'), default='unpaid')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipping_address = db.Column(db.String(200))
    total_amount = db.Column(db.Numeric(10,2), nullable=False, default=0)
    payment_method = db.Column(db.Enum('cod', 'vnpay'), default='cod')
    delivery_method = db.Column(db.Enum('home_delivery', 'instore_pickup'), default='home_delivery')
    pickup_store = db.Column(db.String(200))
    notes = db.Column(db.Text)

    # Relationships
    customer = db.relationship('Customer', backref=db.backref('orders', lazy='dynamic'))

    def __repr__(self):
        return f'<Order {self.invoice}>'

    @property
    def status_display(self):
        """Return human-readable status"""
        status_map = {
            'pending': 'Đang xác nhận',
            'confirmed': 'Đã xác nhận',
            'shipping': 'Đang giao',
            'delivered': 'Đã giao',
            'cancelled': 'Đã hủy',
            'ready_for_pickup': 'Sẵn sàng nhận tại cửa hàng'
        }
        return status_map.get(self.status, self.status)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)

    # Relationships
    order = db.relationship('Order', backref=db.backref('items', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('order_items', lazy='dynamic'))

    def __repr__(self):
        return f'<OrderItem {self.product.name} x{self.quantity}>'

    @property
    def total_price(self):
        """Calculate total price for this item"""
        discounted_price = self.unit_price * (100 - self.discount) / 100
        return discounted_price * self.quantity

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255), default='article-default.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, index=True)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='draft', index=True)
    slug = db.Column(db.String(255), unique=True, index=True)

    # Relationships
    admin = db.relationship('Admin', backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return f'<Article {self.title}>'

    def generate_slug(self):
        """Generate a URL-friendly slug from the title"""
        import re
        from unidecode import unidecode

        # Convert to lowercase and remove accents
        slug = unidecode(self.title.lower())

        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')

        return slug

    @property
    def is_published(self):
        """Check if article is published"""
        return self.status == 'published'