"""
Business logic services
"""

from shop import db
from shop.models import Product, Customer, Order, OrderItem, Rating, Category, Brand
from shop.utilities import generate_invoice_number, calculate_cart_total
from shop.validation import (
    validate_product_name, validate_price, validate_discount,
    validate_stock, validate_description, validate_username,
    validate_email, validate_password, validate_phone_number
)
from shop.errors import ValidationError, DatabaseError
from sqlalchemy.exc import IntegrityError
from flask import current_app
import os

class ProductService:
    """Service for product-related operations"""

    @staticmethod
    def create_product(data, image_files):
        """Create a new product"""
        try:
            # Validate input data
            name = validate_product_name(data.get('name'))
            price = validate_price(data.get('price'))
            discount = validate_discount(data.get('discount', 0))
            stock = validate_stock(data.get('stock', 0))
            colors = data.get('colors', '').strip()
            description = validate_description(data.get('description'))

            # Create product
            product = Product(
                name=name,
                price=price,
                discount=discount,
                stock=stock,
                colors=colors,
                description=description,
                category_id=data.get('category_id'),
                brand_id=data.get('brand_id')
            )

            # Handle image uploads
            if image_files:
                ProductService._handle_image_uploads(product, image_files)

            db.session.add(product)
            db.session.commit()

            return product

        except IntegrityError as e:
            db.session.rollback()
            raise ValidationError("Sản phẩm với thông tin này đã tồn tại")
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể tạo sản phẩm: {str(e)}")

    @staticmethod
    def update_product(product_id, data, image_files=None):
        """Update an existing product"""
        try:
            product = Product.query.get_or_404(product_id)

            # Update fields if provided
            if 'name' in data:
                product.name = validate_product_name(data['name'])
            if 'price' in data:
                product.price = validate_price(data['price'])
            if 'discount' in data:
                product.discount = validate_discount(data['discount'])
            if 'stock' in data:
                product.stock = validate_stock(data['stock'])
            if 'colors' in data:
                product.colors = data['colors'].strip()
            if 'description' in data:
                product.description = validate_description(data['description'])
            if 'category_id' in data:
                product.category_id = data['category_id']
            if 'brand_id' in data:
                product.brand_id = data['brand_id']

            # Handle image uploads
            if image_files:
                ProductService._handle_image_uploads(product, image_files, update=True)

            db.session.commit()
            return product

        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể cập nhật sản phẩm: {str(e)}")

    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        try:
            product = Product.query.get_or_404(product_id)

            # Delete associated images
            ProductService._delete_product_images(product)

            # Delete ratings
            Rating.query.filter_by(product_id=product_id).delete()

            # Delete the product
            db.session.delete(product)
            db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể xóa sản phẩm: {str(e)}")

    @staticmethod
    def _handle_image_uploads(product, image_files, update=False):
        """Handle image file uploads for product"""
        from flask_uploads import UploadNotAllowed
        from shop import photos

        # Delete old images if updating
        if update:
            ProductService._delete_product_images(product)

        # Upload new images
        for i, file_key in enumerate(['image_1', 'image_2', 'image_3'], 1):
            if file_key in image_files and image_files[file_key].filename:
                try:
                    filename = photos.save(image_files[file_key], name=f"{product.id}_image_{i}.")
                    setattr(product, f"image_{i}", filename)
                except UploadNotAllowed:
                    raise ValidationError(f"File ảnh {i} không được phép tải lên")

    @staticmethod
    def _delete_product_images(product):
        """Delete product image files"""
        for i in range(1, 4):
            image_field = getattr(product, f"image_{i}")
            if image_field and image_field != 'image.jpg':
                try:
                    image_path = os.path.join(current_app.root_path, "static/images", image_field)
                    if os.path.exists(image_path):
                        os.unlink(image_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete image {image_field}: {e}")

class CustomerService:
    """Service for customer-related operations"""

    @staticmethod
    def create_customer(data):
        """Create a new customer"""
        try:
            # Validate input data
            username = validate_username(data.get('username'))
            email = validate_email(data.get('email'))
            password = validate_password(data.get('password'))
            phone_number = validate_phone_number(data.get('phone_number'))

            # Check for existing username/email
            if Customer.query.filter_by(username=username).first():
                raise ValidationError("Tên đăng nhập đã được sử dụng")
            if Customer.query.filter_by(email=email).first():
                raise ValidationError("Email đã được sử dụng")
            if Customer.query.filter_by(phone_number=phone_number).first():
                raise ValidationError("Số điện thoại đã được sử dụng")

            # Create customer
            from shop import bcrypt
            customer = Customer(
                username=username,
                first_name=data.get('first_name', '').strip(),
                last_name=data.get('last_name', '').strip(),
                email=email,
                phone_number=phone_number,
                gender=data.get('gender', 'other'),
                password=bcrypt.generate_password_hash(password).decode('utf-8')
            )

            db.session.add(customer)
            db.session.commit()

            return customer

        except IntegrityError:
            db.session.rollback()
            raise ValidationError("Thông tin đăng ký đã tồn tại")
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể tạo tài khoản: {str(e)}")

class OrderService:
    """Service for order-related operations"""

    @staticmethod
    def create_order(customer_id, cart_items, shipping_address, payment_method='cod', delivery_method='home_delivery'):
        """Create a new order from cart items"""
        try:
            customer = Customer.query.get_or_404(customer_id)

            # Calculate total
            total_amount = calculate_cart_total(cart_items)

            # Create order
            order = Order(
                invoice=generate_invoice_number(),
                customer_id=customer_id,
                shipping_address=shipping_address,
                total_amount=total_amount,
                payment_method=payment_method,
                delivery_method=delivery_method
            )

            db.session.add(order)
            db.session.flush()  # Get order ID

            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product.id,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                    discount=cart_item.product.discount
                )
                db.session.add(order_item)

                # Update product stock
                cart_item.product.stock -= cart_item.quantity

            db.session.commit()
            return order

        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể tạo đơn hàng: {str(e)}")

class RatingService:
    """Service for rating-related operations"""

    @staticmethod
    def create_rating(customer_id, product_id, rating, comment):
        """Create a new product rating"""
        try:
            from shop.validation import validate_rating, validate_comment

            # Validate input
            rating_value = validate_rating(rating)
            comment_text = validate_comment(comment)

            # Check if customer already rated this product
            existing_rating = Rating.query.filter_by(
                customer_id=customer_id,
                product_id=product_id
            ).first()

            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating_value
                existing_rating.comment = comment_text
                existing_rating.created_at = db.func.now()
            else:
                # Create new rating
                new_rating = Rating(
                    customer_id=customer_id,
                    product_id=product_id,
                    rating=rating_value,
                    comment=comment_text
                )
                db.session.add(new_rating)

            db.session.commit()
            return existing_rating or new_rating

        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Không thể tạo đánh giá: {str(e)}")

class SearchService:
    """Service for search operations"""

    @staticmethod
    def search_products(query, category_id=None, brand_id=None, min_price=None, max_price=None,
                       sort_by='name', page=1, per_page=12):
        """Advanced product search"""
        try:
            # Base query
            products_query = Product.query.filter(Product.stock > 0)

            # Text search
            if query:
                search_term = f"%{query.lower()}%"
                products_query = products_query.filter(Product.name.ilike(search_term))

            # Category filter
            if category_id:
                products_query = products_query.filter_by(category_id=category_id)

            # Brand filter
            if brand_id:
                products_query = products_query.filter_by(brand_id=brand_id)

            # Price range filter
            if min_price is not None:
                products_query = products_query.filter(Product.discounted_price >= min_price)
            if max_price is not None:
                products_query = products_query.filter(Product.discounted_price <= max_price)

            # Sorting
            if sort_by == 'price_asc':
                products_query = products_query.order_by(Product.discounted_price.asc())
            elif sort_by == 'price_desc':
                products_query = products_query.order_by(Product.discounted_price.desc())
            elif sort_by == 'newest':
                products_query = products_query.order_by(Product.pub_date.desc())
            elif sort_by == 'rating':
                # This would require a more complex query with ratings
                products_query = products_query.order_by(Product.name.asc())
            else:
                products_query = products_query.order_by(Product.name.asc())

            # Paginate
            return products_query.paginate(page=page, per_page=per_page, error_out=False)

        except Exception as e:
            raise DatabaseError(f"Không thể tìm kiếm sản phẩm: {str(e)}")
