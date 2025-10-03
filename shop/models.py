from shop import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name}>'

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), nullable=False)
    profile = db.Column(db.String(180), default='profile.jpg')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=2)  # Default to 'nhanvien'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    role = db.relationship('Role', backref=db.backref('admins', lazy='dynamic'))

    def __repr__(self):
        return f'<Admin {self.username}>'

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role and self.role.name == 'admin'

    @property
    def is_nhanvien(self):
        """Check if user has nhanvien role"""
        return self.role and self.role.name == 'nhanvien'

    def has_permission(self, permission):
        """Check if user has specific permission"""
        if self.is_admin:
            return True  # Admin has all permissions
        
        # Define permissions for nhanvien
        nhanvien_permissions = [
            'view_inventory',      # Nhập hàng
            'manage_products',     # Sản phẩm
            'manage_articles',     # Bài viết
            'view_orders'          # Đơn hàng
        ]
        
        return permission in nhanvien_permissions if self.is_nhanvien else False

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
    
    # Tất cả sản phẩm đều có variants - bỏ price và stock
    # price = db.Column(db.Numeric(10,2), nullable=False)  # Đã bỏ - lấy từ variants
    # stock = db.Column(db.Integer, nullable=False, default=0)  # Đã bỏ - lấy từ variants
    sold_quantity = db.Column(db.Integer, nullable=False, default=0)  # Tự động cập nhật từ variants  
    colors = db.Column(db.Text, nullable=True)  # Không còn cần thiết vì có variants
    
    # Tất cả sản phẩm đều có variants
    has_variants = db.Column(db.Boolean, default=True)  # Luôn True - tất cả sản phẩm có variants
    min_price = db.Column(db.Numeric(10,2))  # Giá thấp nhất từ variants
    max_price = db.Column(db.Numeric(10,2))  # Giá cao nhất từ variants
    
    discount = db.Column(db.Integer, default=0)
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
    def current_price(self):
        """Get current price from variants"""
        if self.min_price is not None:
            if self.min_price == self.max_price:
                # Nếu tất cả variants có cùng giá
                if self.discount > 0:
                    return self.min_price * (100 - self.discount) / 100
                return self.min_price
            else:
                # Nếu có nhiều giá khác nhau, trả về range
                min_price = self.min_price
                max_price = self.max_price
                if self.discount > 0:
                    min_price = min_price * (100 - self.discount) / 100
                    max_price = max_price * (100 - self.discount) / 100
                return f"{min_price:,.0f}đ - {max_price:,.0f}đ"
        return 0  # Chưa có variants

    @property
    def discounted_price(self):
        """Calculate discounted price - for backward compatibility"""
        return self.current_price

    @property
    def is_available(self):
        """Check if product is available for purchase"""
        # Kiểm tra xem có variant nào có stock > 0 không
        return any(variant.stock > 0 for variant in self.variants if variant.is_active)

    @property
    def price_range(self):
        """Get price range for products with variants - for backward compatibility"""
        return self.current_price

    @property
    def display_price(self):
        """Get formatted display price"""
        current_price = self.current_price
        if isinstance(current_price, str):
            return current_price  # Already formatted as range
        else:
            return f"{current_price:,.0f}đ"
    
    @property
    def total_stock(self):
        """Get total stock from all variants"""
        total = sum(variant.stock for variant in self.variants if variant.is_active)
        return total if total is not None else 0
    
    @property
    def stock(self):
        """Backward compatibility - get total stock from variants"""
        return self.total_stock

    @property
    def total_sold_quantity(self):
        """Get total sold quantity from all variants"""
        return sum(variant.sold_quantity for variant in self.variants.filter_by(is_active=True))

    def get_available_sizes(self):
        """Get available sizes for this product"""
        return db.session.query(Size).join(ProductVariant).filter(
            ProductVariant.product_id == self.id,
            ProductVariant.is_active == True,
            ProductVariant.stock > 0
        ).order_by(Size.sort_order).all()

    def get_available_colors(self):
        """Get available colors for this product"""
        return db.session.query(Color).join(ProductVariant).filter(
            ProductVariant.product_id == self.id,
            ProductVariant.is_active == True,
            ProductVariant.stock > 0
        ).all()
    
    def get_cheapest_variant(self):
        """Get the cheapest available variant"""
        
        return self.variants.filter_by(is_active=True).filter(
            ProductVariant.stock > 0
        ).order_by(ProductVariant.price.asc()).first()

    def get_variant_by_attributes(self, size_id=None, color_id=None):
        """Get variant by size and color"""
        if not self.has_variants:
            return None
        
        query = self.variants.filter_by(is_active=True)
        if size_id:
            query = query.filter_by(size_id=size_id)
        if color_id:
            query = query.filter_by(color_id=color_id)
        
        return query.first()


class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    contact_name = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Supplier {self.name}>'

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
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)

    # Relationships
    order = db.relationship('Order', backref=db.backref('items', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('order_items', lazy='dynamic'))
    product_variant = db.relationship('ProductVariant', backref=db.backref('order_items', lazy='dynamic'))

    def __repr__(self):
        if self.product_variant:
            return f'<OrderItem {self.product_variant.display_name} x{self.quantity}>'
        return f'<OrderItem {self.product.name} x{self.quantity}>'

    @property
    def total_price(self):
        """Calculate total price for this item"""
        discounted_price = self.unit_price * (100 - self.discount) / 100
        return discounted_price * self.quantity

    @property
    def item_display_name(self):
        """Get display name for order item"""
        if self.product_variant:
            return self.product_variant.display_name
        return self.product.name

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


# ================= INVENTORY (PURCHASE) MODELS =================
class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(30), unique=True, index=True)
    supplier_name = db.Column(db.String(120))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), index=True)

    # Relationships
    admin = db.relationship('Admin', backref=db.backref('purchases', lazy='dynamic'))
    supplier = db.relationship('Supplier', backref=db.backref('purchases', lazy='dynamic'))

    def __repr__(self):
        return f'<Purchase #{self.id} - {self.invoice_number}>'


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_item'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10,2), nullable=False, default=0)

    # Relationships
    purchase = db.relationship('Purchase', backref=db.backref('items', lazy='dynamic', cascade='all, delete-orphan'))
    product = db.relationship('Product', backref=db.backref('purchase_items', lazy='dynamic'))
    product_variant = db.relationship('ProductVariant', backref=db.backref('purchase_items', lazy='dynamic'))

    def __repr__(self):
        return f'<PurchaseItem P{self.product_id} x{self.quantity}>'


# ================= NEW MODELS FOR VARIANTS =================

class Size(db.Model):
    __tablename__ = 'size'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    display_name = db.Column(db.String(20), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Size {self.name}>'


class Color(db.Model):
    __tablename__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    hex_code = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Color {self.name}>'


class ProductVariant(db.Model):
    __tablename__ = 'product_variant'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), index=True)
    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), index=True)
    sku = db.Column(db.String(100), unique=True)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sold_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', backref=db.backref('variants', lazy='dynamic'))
    size = db.relationship('Size', backref=db.backref('variants', lazy='dynamic'))
    color = db.relationship('Color', backref=db.backref('variants', lazy='dynamic'))

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('product_id', 'size_id', 'color_id', name='unique_variant'),
    )

    def __repr__(self):
        size_name = self.size.name if self.size else 'No Size'
        color_name = self.color.name if self.color else 'No Color'
        return f'<ProductVariant {self.product.name} - {size_name} - {color_name}>'

    @property
    def display_name(self):
        """Get display name for variant"""
        parts = [self.product.name]
        if self.color:
            parts.append(self.color.name)
        if self.size:
            parts.append(f"Size {self.size.name}")
        return " - ".join(parts)

    @property
    def discounted_price(self):
        """Calculate discounted price based on product discount"""
        if self.product.discount > 0:
            return self.price * (100 - self.product.discount) / 100
        return self.price

    @property
    def is_available(self):
        """Check if variant is available for purchase"""
        return self.is_active and self.stock > 0

    def generate_sku(self):
        """Generate SKU for this variant"""
        if self.sku:
            return self.sku
            
        product_prefix = ''.join([c.upper() for c in self.product.name.replace(' ', '') if c.isalnum()])[:3]
        product_id_str = f"{self.product_id:03d}"
        size_str = self.size.name if self.size else 'OS'
        color_prefix = ''.join([c.upper() for c in self.color.name.replace(' ', '') if c.isalnum()])[:3] if self.color else 'DEF'
        
        return f"{product_prefix}-{product_id_str}-{size_str}-{color_prefix}"


class StockMovement(db.Model):
    __tablename__ = 'stock_movement'
    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False, index=True)
    movement_type = db.Column(db.Enum('in', 'out', 'adjustment'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.Enum('purchase', 'order', 'adjustment', 'return'))
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), index=True)

    # Relationships
    product_variant = db.relationship('ProductVariant', backref=db.backref('stock_movements', lazy='dynamic'))
    admin = db.relationship('Admin', backref=db.backref('stock_movements', lazy='dynamic'))

    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} for Variant {self.product_variant_id}>'