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

class Addproduct(db.Model):
    __tablename__ = 'addproduct'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    
    # Add these relationships
    category = db.relationship('Category', backref='products')
    brand = db.relationship('Brand', backref='products')
    image_1 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_2 = db.Column(db.String(150), nullable=False, default='image.jpg')
    image_3 = db.Column(db.String(150), nullable=False, default='image.jpg')

class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    phone_number = db.Column(db.String(50), unique=True)
    gender = db.Column(db.String(5))
    password = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False)
    lock = db.Column(db.Boolean)

class Rate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('addproduct.id'), nullable=False)
    register_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    rate_number = db.Column(db.Integer, nullable=False)

class CustomerOrder(db.Model):
    __tablename__ = 'customer_order'
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Đang xác nhận')  # Order status: Đang xác nhận, Đang giao, Đã giao, Hủy đơn, Sẵn sàng nhận tại cửa hàng
    payment_status = db.Column(db.String(20), default='Chưa thanh toán')  # Payment status: Chưa thanh toán (COD), Đã thanh toán (VNPAY)
    customer_id = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.Column(db.Text)
    address = db.Column(db.String(200))
    amount = db.Column(db.Numeric(10,2), default=0)
    payment_method = db.Column(db.String(20), default='cod')
    delivery_method = db.Column(db.String(20), default='home_delivery')  # home_delivery or instore_pickup
    pickup_store = db.Column(db.String(200), default='')  # Store location for pickup

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255), default='article-default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='draft')
    slug = db.Column(db.String(255), unique=True)

    # Relationships
    admin = db.relationship('Admin', backref='articles')

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