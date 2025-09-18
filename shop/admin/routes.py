import os
import urllib
import secrets
from datetime import datetime
from itertools import product
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# QR Code generation (optional)
try:
    import qrcode
    from io import BytesIO
    import base64
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

from flask import render_template, session, request, redirect, url_for, flash, current_app, jsonify
from shop import app, db, bcrypt
import json
from shop.models import Brand, Category, Product, Customer, Admin, Order, Rating, Article
from shop.email_utils import send_order_status_update_email

# Import reportlab modules at module level to avoid import errors

# CSRF protection temporarily disabled in app config
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not available. Invoice export will not work.")
from .forms import LoginForm, RegistrationForm
from shop.customers.forms import CustomerRegisterForm




@app.route('/admin/customer_register', methods=['GET', 'POST'])
def admin_register_custormer():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        if Admin.query.filter_by(email=form.email.data).first():
            flash(f'Email Used!', 'danger')
            return redirect(url_for('admin_register_custormer'))
        if Customer.query.filter_by(email=form.email.data).first():
            flash(f'Email Used!', 'danger')
            return redirect(url_for('admin_register_custormer'))
        if Customer.query.filter_by(phone_number=form.phone_number.data).first():
            flash(f'Phone Number Used!', 'danger')
            return redirect(url_for('admin_register_custormer'))
        try:
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
            customer = Customer(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                                last_name=form.last_name.data, phone_number=form.phone_number.data,
                                gender=form.gender.data,
                                password=hash_password)
            db.session.add(customer)
            flash(f'Register account " {form.first_name.data} {form.last_name.data} " success', 'success')
            db.session.commit()
            return redirect(url_for('admin_register_custormer'))
        except:
            flash(f'Error!', 'danger')
            return redirect(url_for('admin_register_custormer'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/customer_register.html', form=form, user=user[0])


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('admin_manager'))


@app.route('/admin_manager')
def admin_manager():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    admins = Admin.query.all()
    return render_template('admin/admin-manager.html', title='Admin manager page', user=user[0], admins=admins)


@app.route('/customer_manager')
def customer_manager():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    customers = Customer.query.all()
    
    for customer in customers:
        customer_orders = Order.query.filter_by(customer_id=customer.id).all()
        customer.can_delete = len(customer_orders) == 0
    
    return render_template('admin/customer_manager.html', title='Customer manager page', user=user[0],
                           customers=customers)


@app.route('/admin/orders')
def orders_manager():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    customers = Customer.query.all()

    orders = Order.query.filter(Order.status != None).order_by(Order.id.desc()).all()

    # Update old statuses to new ones in memory (for display)
    for order in orders:
        if order.status == 'Pending':
            order.status = 'Đang xác nhận'
        elif order.status == 'Accepted':
            order.status = 'Đã giao'
        elif order.status == 'Cancelled':
            order.status = 'Hủy đơn'

        # Add payment status display
        if hasattr(order, 'payment_status'):
            if order.payment_method == 'cod':
                order.display_payment_status = 'Chưa thanh toán'
            elif order.payment_method == 'vnpay':
                order.display_payment_status = 'Đã thanh toán'
            else:
                order.display_payment_status = order.payment_status or 'N/A'
        else:
            order.display_payment_status = 'N/A'

        order_data = get_order_data(order)
        total_quantity = 0
        total_price = 0

        enhanced_products = {}

        if order_data and isinstance(order_data, dict):
            for key, product in order_data.items():
                if product and isinstance(product, dict):
                    enhanced_product = product.copy()

                    quantity = product.get('quantity', 0)
                    price = product.get('price', 0)
                    discount = product.get('discount', 0)

                    try:
                        quantity = int(quantity) if quantity else 0
                        price = float(price) if price else 0.0
                        discount = float(discount) if discount else 0.0
                    except (ValueError, TypeError):
                        quantity = 0
                        price = 0.0
                        discount = 0.0

                    if quantity > 0:
                        total_quantity += quantity

                        original_price = price * quantity

                        # Calculate discount amount per item
                        discount_amount_per_item = (price * discount / 100) if discount > 0 else 0.0

                        discounted_price_per_item = price - discount_amount_per_item

                        discounted_total_per_item = discounted_price_per_item * quantity

                        total_discount_for_item = discount_amount_per_item * quantity

                        enhanced_product['original_price'] = price
                        enhanced_product['discounted_price'] = discounted_price_per_item
                        enhanced_product['discount_amount'] = discount_amount_per_item
                        enhanced_product['original_total'] = original_price
                        enhanced_product['discounted_total'] = discounted_total_per_item
                        enhanced_product['total_discount'] = total_discount_for_item

                        total_price += discounted_total_per_item

                    # Try to get product image from database if we have product ID
                    if 'id' in product or key.isdigit():
                        try:
                            from shop.models import Product
                            product_id = product.get('id', key if key.isdigit() else None)
                            if product_id:
                                db_product = Product.query.get(int(product_id))
                                if db_product and db_product.image_1:
                                    enhanced_product['image_1'] = db_product.image_1
                        except:
                            pass  # Ignore errors, image is optional

                    enhanced_products[key] = enhanced_product

        # Calculate order totals
        order.total_quantity = total_quantity
        order.total_price = total_price
        order.total_original_price = sum(p.get('original_total', 0) for p in enhanced_products.values())
        order.total_discount_amount = sum(p.get('total_discount', 0) for p in enhanced_products.values())


        order.product_details = enhanced_products if enhanced_products else order_data

    return render_template('admin/manage_orders.html', title='Order manager page', user=user[0], orders=orders,
                           customers=customers)


@app.route('/accept_order/<int:id>', methods=['GET', 'POST'])
def accept_order(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    
    if request.method == "POST":
        customer_order = Order.query.get_or_404(id)
        # Process order items using OrderItem relationships
        order_items = customer_order.items  # Get all order items
        stock_exhausted = False

        for order_item in order_items:
            product = order_item.product
            if (product.stock - order_item.quantity) >= 0:
                product.stock -= order_item.quantity
                customer_order.status = 'shipping'  # Use English status
                db.session.commit()
            else:
                stock_exhausted = True
                flash(f'Quantity in stock has been exhausted for product: {product.name}', 'danger')

        if not stock_exhausted:
            flash('Order status updated successfully', 'success')
            return redirect(url_for('orders_manager'))

            # Send email notification to customer
            customer = Customer.query.get(customer_order.customer_id)
            if customer:
                send_order_status_update_email(customer, customer_order, action_by="admin")

        return redirect(url_for('orders_manager'))
    
    return redirect(url_for('orders_manager'))


@app.route('/delivered_order/<int:id>', methods=['GET', 'POST'])
def delivered_order(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    
    if request.method == "POST":
        customer_order = Order.query.get_or_404(id)
        customer_order.status = 'Đã giao'
        db.session.commit()

        # Send email notification to customer
        customer = Customer.query.get(customer_order.customer_id)
        if customer:
            send_order_status_update_email(customer, customer_order, action_by="admin")

        flash('Đơn hàng đã được cập nhật thành "Đã giao"', 'success')
        return redirect(url_for('orders_manager'))
    
    return redirect(url_for('orders_manager'))


@app.route('/ready_for_pickup/<int:id>', methods=['GET', 'POST'])
def ready_for_pickup(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    if request.method == "POST":
        customer_order = Order.query.get_or_404(id)

        # Only allow for instore pickup orders
        if customer_order.delivery_method != 'instore_pickup':
            flash('Chỉ áp dụng cho đơn hàng nhận tại cửa hàng!', 'warning')
            return redirect(url_for('orders_manager'))

        customer_order.status = 'Sẵn sàng nhận tại cửa hàng'
        db.session.commit()

        # Send email notification to customer
        customer = Customer.query.get(customer_order.customer_id)
        if customer:
            send_order_status_update_email(customer, customer_order, action_by="admin")

        flash('Đơn hàng đã được cập nhật thành "Sẵn sàng nhận tại cửa hàng"', 'success')
        return redirect(url_for('orders_manager'))

    return redirect(url_for('orders_manager'))


@app.route('/delete_order/<int:id>', methods=['GET', 'POST'])
def delete_order(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Order.query.get_or_404(id)
    if request.method == "POST":
        customer.status = "Hủy đơn"
        db.session.commit()

        # Send email notification to customer
        customer_info = Customer.query.get(customer.customer_id)
        if customer_info:
            send_order_status_update_email(customer_info, customer, action_by="admin")

        flash('Đơn hàng đã được hủy thành công', 'success')
        return redirect(url_for('orders_manager'))
    return redirect(url_for('orders_manager'))


@app.route('/lock_customer/<int:id>', methods=['GET', 'POST'])
def lock_customer(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Customer.query.get_or_404(id)
    if request.method == "POST":
        customer.is_active = False
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/unlock_customer/<int:id>', methods=['GET', 'POST'])
def unlock_customer(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Customer.query.get_or_404(id)
    if request.method == "POST":
        customer.is_active = True
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/delete_customer/<int:id>', methods=['GET', 'POST'])
def delete_customer(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Customer.query.get_or_404(id)
    
    customer_orders = Order.query.filter_by(customer_id=id).all()
    if customer_orders:
        flash(f"Tài khoản {customer.username} đã đặt hàng (Ràng buộc khóa) không thể xóa.", "danger")
        return redirect(url_for('customer_manager'))
    
    if request.method == "POST":
        # Xóa các đánh giá của customer trước
        rates = Rating.query.filter(Rating.customer_id == id).all()
        for rate in rates:
            db.session.delete(rate)
            db.session.commit()
        
        # Xóa customer
        db.session.delete(customer)
        db.session.commit()
        flash(f"Tài khoản {customer.username} đã được xóa thành công", "success")
        return redirect(url_for('customer_manager'))
    
    flash(f"Tài khoản {customer.username} không thể xóa", "warning")
    return redirect(url_for('customer_manager'))


@app.route('/delete_admin/<int:id>', methods=['GET', 'POST'])
def delete_admin(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    admin = Admin.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(admin)
        db.session.commit()
        flash(f"The admin {admin.name} was deleted from your database", "success")
        return redirect(url_for('admin_manager'))
    flash(f"The admin {admin.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin_manager'))


@app.route('/product')
def product():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    products = Product.query.all()
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/index.html', title='Product page', products=products, user=user[0])


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    brands = Brand.query.join(Category).add_columns(Category.name).filter(Brand.category_id == Category.id).order_by(
        Brand.id.desc()).all()
    print(brands)
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/manage_brand.html', title='brands', brands=brands, user=user[0])


@app.route('/categories')
def categories():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/manage_brand.html', title='categories', categories=categories, user=user[0])


@app.route('/admin/changepassword', methods=['GET', 'POST'])
def changes_password():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email'])
    detail_password_admin = Admin.query.get_or_404(user[0].id)
    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if request.method == "POST":
        if not bcrypt.check_password_hash(detail_password_admin.password, old_password.encode('utf8')):
            flash(f'Old passwords do not match!', 'danger')
            return redirect(url_for('changes_password'))
        detail_password_admin.password = bcrypt.generate_password_hash(new_password).decode('utf8')
        flash(f'Change Password Complete!', 'success')
        db.session.commit()
        return redirect(url_for('changes_password'))
    return render_template('admin/change_password.html', title='Change Password', user=user[0])


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = Admin(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f' Wellcom {form.name.data} Thanks for registering', 'success')
        return redirect(url_for('register'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('admin/admin_register.html', form=form, title='Registration page', user=user[0])


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Admin.query.filter_by(email=form.email.data).first()
        password = form.password.data.encode('utf8')
        if user and bcrypt.check_password_hash(user.password, password):
            session['email'] = form.email.data
            flash(f'welcome {form.email.data} you are logedin now', 'success')
            return redirect(url_for('admin'))
        else:
            flash(f'Wrong email and password', 'danger')
            return redirect(url_for('login'))
    return render_template('admin/login.html', title='Login page', form=form)


@app.route('/admin/logout')
def logout():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
    else:
        session.pop('email', None)
    return redirect(url_for('login'))


def get_order_data(order):
    """Helper function to get order items data from OrderItem relationships"""
    try:
        # Get all order items for this order
        order_items = order.items  # This uses the relationship defined in the Order model

        # Convert to the old format for compatibility with templates
        order_data = {}
        for item in order_items:
            order_data[str(item.product_id)] = {
                'name': item.product.name,
                'price': str(item.unit_price),
                'discount': item.discount,
                'quantity': item.quantity,
                'color': getattr(item.product, 'colors', ''),
                'image': item.product.image_1
            }
        return order_data
    except Exception as e:
        print(f"Error getting order data: {e}")
        return {}




# ============= ARTICLE MANAGEMENT ROUTES =============

@app.route('/admin/articles')
def articles_manager():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    user = Admin.query.filter_by(email=session['email']).first()
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles_manager.html', title='Quản lý bài viết', user=user, articles=articles)


@app.route('/admin/article/add', methods=['GET', 'POST'])
def add_article():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    user = Admin.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        status = request.form.get('status', 'draft')

        if not title or not content:
            flash('Vui lòng điền đầy đủ thông tin', 'danger')
            return redirect(url_for('add_article'))

        # Handle cover image upload
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.root_path, 'static/images/articles', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                cover_image = filename

        # Create article
        article = Article(
            title=title,
            content=content,
            cover_image=cover_image or 'article-default.jpg',
            admin_id=user.id,
            status=status
        )

        # Generate slug
        article.slug = article.generate_slug()

        try:
            db.session.add(article)
            db.session.commit()
            flash('Bài viết đã được tạo thành công!', 'success')
            return redirect(url_for('articles_manager'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi tạo bài viết: {str(e)}', 'danger')
            return redirect(url_for('add_article'))

    return render_template('admin/add_article.html', title='Thêm bài viết', user=user)


@app.route('/admin/article/edit/<int:id>', methods=['GET', 'POST'])
def edit_article(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    user = Admin.query.filter_by(email=session['email']).first()
    article = Article.query.get_or_404(id)

    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.status = request.form.get('status', 'draft')

        # Handle cover image upload
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.root_path, 'static/images/articles', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                article.cover_image = filename

        # Update slug if title changed
        article.slug = article.generate_slug()

        try:
            db.session.commit()
            flash('Bài viết đã được cập nhật thành công!', 'success')
            return redirect(url_for('articles_manager'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật bài viết: {str(e)}', 'danger')

    return render_template('admin/edit_article.html', title='Chỉnh sửa bài viết', user=user, article=article)


@app.route('/admin/article/delete/<int:id>', methods=['POST'])
def delete_article(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    article = Article.query.get_or_404(id)

    try:
        # Delete cover image file if it exists
        if article.cover_image and article.cover_image != 'article-default.jpg':
            image_path = os.path.join(current_app.root_path, 'static/images/articles', article.cover_image)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(article)
        db.session.commit()
        flash('Bài viết đã được xóa thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa bài viết: {str(e)}', 'danger')

    return redirect(url_for('articles_manager'))


@app.route('/admin/article/toggle-status/<int:id>', methods=['POST'])
def toggle_article_status(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    article = Article.query.get_or_404(id)

    # Toggle status between published and draft
    if article.status == 'published':
        article.status = 'draft'
        flash('Bài viết đã được chuyển về bản nháp!', 'info')
    else:
        article.status = 'published'
        flash('Bài viết đã được xuất bản!', 'success')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi cập nhật trạng thái: {str(e)}', 'danger')

    return redirect(url_for('articles_manager'))


# Route xuất hóa đơn
@app.route('/admin/orders/<int:order_id>/export-invoice')
def export_invoice(order_id):
    try:
        current_app.logger.info(f"Starting PDF export for order {order_id}")
        from shop.models import Order, Product, Customer
        from flask import make_response, send_file, jsonify
        import io
        import json

        # Check if ReportLab is available
        if not REPORTLAB_AVAILABLE:
            return jsonify({'error': 'ReportLab library is not available. Please install it to export invoices.'}), 500

        # Lấy thông tin đơn hàng
        order = Order.query.get_or_404(order_id)
        current_app.logger.info(f"Order found: {order.invoice}")

        # Validate order has required attributes
        if not hasattr(order, 'created_at'):
            current_app.logger.error(f"Order {order_id} missing created_at attribute")
            return jsonify({'error': 'Đơn hàng thiếu thông tin ngày tạo'}), 400

        # Lấy thông tin khách hàng
        customer = Customer.query.get(order.customer_id)
        if not customer:
            current_app.logger.error(f"Customer not found for order {order_id}")
            return jsonify({'error': 'Không tìm thấy thông tin khách hàng'}), 404

        current_app.logger.info(f"Customer found: {customer.first_name} {customer.last_name}")

        # Parse dữ liệu sản phẩm
        order_data = get_order_data(order)
        current_app.logger.info(f"Order data keys: {list(order_data.keys()) if order_data else 'None'}")
        products = []

        if order_data and isinstance(order_data, dict):
            for key, product in order_data.items():
                if product and isinstance(product, dict):
                    quantity = product.get('quantity', 0)
                    price = product.get('price', 0)
                    discount = product.get('discount', 0)

                    try:
                        quantity = int(quantity) if quantity else 0
                        price = float(price) if price else 0.0
                        discount = float(discount) if discount else 0.0
                    except (ValueError, TypeError):
                        quantity = 0
                        price = 0.0
                        discount = 0.0

                    if quantity > 0:
                        # Calculate discount amount per item (same logic as admin orders)
                        discount_amount_per_item = (price * discount / 100) if discount > 0 else 0.0

                        # Calculate discounted price per item
                        final_price = price - discount_amount_per_item

                        # Calculate total for this item after discount
                        total = final_price * quantity

                        # Calculate total discount for this item
                        total_discount = discount_amount_per_item * quantity

                        # Lấy thông tin sản phẩm từ database nếu có
                        product_info = None
                        try:
                            if 'id' in product or str(key).isdigit():
                                product_id = product.get('id', key if str(key).isdigit() else None)
                                if product_id:
                                    product_info = Product.query.get(int(product_id))
                        except:
                            pass

                        products.append({
                            'name': product.get('name', 'N/A'),
                            'brand': product_info.brand.name if product_info and product_info.brand and hasattr(product_info.brand, 'name') else product.get('brand', 'N/A'),
                            'color': product_info.colors if product_info else product.get('color', 'N/A'),
                            'quantity': quantity,
                            'original_price': price,
                            'discount': discount,
                            'discount_amount': discount_amount_per_item,
                            'final_price': final_price,
                            'total': total,
                            'total_discount': total_discount
                        })

        # Tạo PDF với encoding UTF-8
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Hàm để đảm bảo text được encode đúng
        def ensure_unicode(text):
            if isinstance(text, str):
                return text
            try:
                return str(text)
            except:
                return "N/A"

        # Cập nhật font mặc định cho tất cả styles với font hỗ trợ Unicode tốt
        try:
            # Thử sử dụng font có hỗ trợ Unicode tốt hơn
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Đăng ký font Arial từ Windows Fonts để hỗ trợ tiếng Việt
            try:
                arial_font_path = r"C:\Windows\Fonts\arial.ttf"
                arial_bold_path = r"C:\Windows\Fonts\arialbd.ttf"

                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_font_path))
                pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', arial_bold_path))

                default_font = 'ArialUnicode'
                print(f"Successfully registered Arial font for Vietnamese support")
            except Exception as e:
                print(f"Failed to register Arial font: {e}")
                # Fallback về font có sẵn
                default_font = 'Helvetica'

        except Exception as e:
            print(f"Error setting up fonts: {e}")
            default_font = 'Helvetica'

        # Cập nhật font mặc định cho các styles chính
        try:
            styles['Heading1'].fontName = default_font
            styles['Normal'].fontName = default_font
        except KeyError:
            # Bỏ qua nếu style không tồn tại
            pass

        # Tạo Heading2 style nếu chưa có
        try:
            styles['Heading2'].fontName = default_font + '-Bold'
        except KeyError:
            # Tạo style Heading2 mới nếu không tồn tại
            heading2_base = ParagraphStyle(
                'Heading2',
                parent=styles['Normal'],
                fontName=default_font + '-Bold' if default_font != 'Helvetica' else default_font,
                fontSize=16,
                spaceAfter=15,
                alignment=0
            )
            # Thêm vào stylesheet nếu có thể
            try:
                styles.add(heading2_base)
            except:
                # Nếu không thể add, chỉ sử dụng local style
                pass

        # Style cho title với font Unicode
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            alignment=1,  # Center alignment
            spaceAfter=20,
            fontName=default_font  # Sử dụng font đã chọn
        )

        # Style cho thông tin với font Unicode
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            fontName=default_font  # Sử dụng font đã chọn
        )

        # Tiêu đề
        elements.append(Paragraph(ensure_unicode("HÓA ĐƠN BÁN HÀNG"), title_style))
        elements.append(Spacer(1, 0.5*inch))

        # Thông tin cửa hàng
        elements.append(Paragraph(ensure_unicode("<b>CỬA HÀNG Belluni</b>"), info_style))
        elements.append(Paragraph(ensure_unicode("Địa chỉ: Số 298 Đ. Cầu Diễn, Minh Khai, Bắc Từ Liêm, Hà Nội"), info_style))
        elements.append(Paragraph(ensure_unicode("Điện thoại: 0033.219.4677"), info_style))
        elements.append(Paragraph(ensure_unicode("Email: VietHoang@gmail.com"), info_style))
        elements.append(Spacer(1, 0.3*inch))

        # Thông tin đơn hàng
        elements.append(Paragraph(ensure_unicode(f"<b>Mã đơn hàng:</b> #{order_id}"), info_style))
        # Format date safely
        order_date = 'N/A'
        if order.created_at:
            try:
                order_date = order.created_at.strftime('%d/%m/%Y %H:%M')
                current_app.logger.debug(f"Order date formatted: {order_date}")
            except Exception as e:
                current_app.logger.warning(f"Could not format order date: {e}")
                order_date = str(order.created_at)

        elements.append(Paragraph(ensure_unicode(f"<b>Ngày đặt:</b> {order_date}"), info_style))
        elements.append(Paragraph(ensure_unicode(f"<b>Trạng thái:</b> {order.status}"), info_style))
        elements.append(Spacer(1, 0.2*inch))

        # Thông tin khách hàng
        try:
            heading2_style = styles['Heading2']
        except KeyError:
            heading2_style = heading2_base  # Sử dụng style đã tạo
        elements.append(Paragraph(ensure_unicode("<b>THÔNG TIN KHÁCH HÀNG</b>"), heading2_style))
        elements.append(Paragraph(ensure_unicode(f"<b>Họ tên:</b> {customer.first_name} {customer.last_name}"), info_style))
        elements.append(Paragraph(ensure_unicode(f"<b>Email:</b> {customer.email}"), info_style))
        elements.append(Paragraph(ensure_unicode(f"<b>SĐT:</b> {customer.phone_number}"), info_style))
        elements.append(Paragraph(ensure_unicode(f"<b>Địa chỉ:</b> {order.shipping_address}"), info_style))
        elements.append(Spacer(1, 0.3*inch))

        # Bảng sản phẩm
        elements.append(Paragraph(ensure_unicode("<b>CHI TIẾT SẢN PHẨM</b>"), heading2_style))

        # Tạo dữ liệu cho bảng
        table_data = [[ensure_unicode('STT'), ensure_unicode('Tên sản phẩm'), ensure_unicode('SL'),
                       ensure_unicode('Đơn giá'), ensure_unicode('Giảm giá'), ensure_unicode('Thành tiền')]]

        total_amount = 0
        total_discount = 0

        for i, product in enumerate(products, 1):
            discount_text = f"{product.get('discount', 0)}%" if product.get('discount', 0) > 0 else '-'
            # Use the calculated discount amount from earlier calculation
            discount_amount = product.get('total_discount', 0)

            table_data.append([
                ensure_unicode(str(i)),
                ensure_unicode(f"{product['name']}\n({product['brand']} - {product['color']})"),
                ensure_unicode(str(product['quantity'])),
                ensure_unicode(f"{product['original_price']:,}₫"),
                ensure_unicode(discount_text),
                ensure_unicode(f"{product['total']:,}₫")
            ])

            total_amount += product['original_price'] * product['quantity']
            total_discount += discount_amount

        # Tạo bảng với font Unicode
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 0.5*inch, 1*inch, 0.8*inch, 1.2*inch])

        # Tạo table style với font đã chọn
        bold_font = default_font + '-Bold' if default_font != 'Helvetica' else default_font

        table_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTNAME', (0, 1), (-1, -1), default_font),  # Font cho data rows
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # Font size cho data
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Canh giữa dọc
        ]

        table.setStyle(TableStyle(table_styles))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Tóm tắt
        final_total = total_amount - total_discount
        elements.append(Paragraph(ensure_unicode(f"<b>Tổng tiền gốc:</b> {total_amount:,.0f}₫"), info_style))
        if total_discount > 0:
            elements.append(Paragraph(ensure_unicode(f"<b>Tổng tiền giảm:</b> {total_discount:,.0f}₫"), info_style))
        total_style = ParagraphStyle('Total', parent=info_style, fontSize=14, textColor=colors.red, fontName=default_font)
        elements.append(Paragraph(ensure_unicode(f"<b>Tổng thanh toán:</b> {final_total:,.0f}₫"), total_style))

        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=11,
            fontName=default_font if default_font != 'Helvetica' else 'Helvetica',
            alignment=1,
            textColor=colors.grey
        )
        elements.append(Paragraph(ensure_unicode("<i>Cảm ơn quý khách đã mua hàng tại Belluni!</i>"), footer_style))

        # Tạo PDF
        current_app.logger.info("Building PDF document")
        doc.build(elements)
        current_app.logger.info("PDF document built successfully")

        buffer.seek(0)
        pdf_size = len(buffer.getvalue())
        current_app.logger.info(f"PDF size: {pdf_size} bytes")

        # Trả về file PDF
        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f'hoa-don-{order_id}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Error generating invoice for order {order_id}: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Có lỗi xảy ra khi tạo hóa đơn'}), 500


# Admin Order Management Routes
@app.route('/admin/orders/create', methods=['GET', 'POST'])
def admin_create_order():
    """Admin create order at counter"""
    if 'email' not in session:
        flash('Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    from .forms import AdminOrderForm, AdminOrderItemForm
    from shop.models import OrderItem

    form = AdminOrderForm()
    item_form = AdminOrderItemForm()

    # Get all products for selection (products with stock > 0)
    products = Product.query.filter(Product.stock > 0).all()

    # Initialize cart for admin order
    if 'admin_cart' not in session:
        session['admin_cart'] = {}

    admin_cart = session['admin_cart']

    # Calculate totals
    subtotal = 0
    total_discount = 0
    total_quantity = 0

    cart_items = []
    for product_id, item in admin_cart.items():
        product = Product.query.get(int(product_id))
        if product:
            quantity = int(item.get('quantity', 0))
            discount_percent = float(item.get('discount', 0))
            unit_price = float(product.price)
            discount_amount = (discount_percent / 100) * unit_price * quantity
            final_price = unit_price * quantity - discount_amount

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_percent': discount_percent,
                'discount_amount': discount_amount,
                'final_price': final_price
            })

            subtotal += unit_price * quantity
            total_discount += discount_amount
            total_quantity += quantity

    total_amount = subtotal - total_discount

    if request.method == 'POST':
        # Handle adding item to cart
        if 'add_item' in request.form:
            if item_form.validate_on_submit():
                product_id = str(item_form.product_id.data)
                quantity = item_form.quantity.data
                discount = item_form.discount.data or 0

                # Check stock
                product = Product.query.get(product_id)
                if not product:
                    flash('Sản phẩm không tồn tại!', 'danger')
                    return redirect(url_for('admin_create_order'))

                if quantity > product.stock:
                    flash(f'Không đủ hàng trong kho. Chỉ còn {product.stock} sản phẩm!', 'danger')
                    return redirect(url_for('admin_create_order'))

                # Add to cart
                admin_cart[product_id] = {
                    'quantity': quantity,
                    'discount': discount
                }
                session['admin_cart'] = admin_cart
                flash('Đã thêm sản phẩm vào đơn hàng!', 'success')
                return redirect(url_for('admin_create_order'))

        # Handle removing item from cart
        elif 'remove_item' in request.form:
            product_id = request.form.get('product_id')
            if product_id in admin_cart:
                del admin_cart[product_id]
                session['admin_cart'] = admin_cart
                flash('Đã xóa sản phẩm khỏi đơn hàng!', 'success')
            return redirect(url_for('admin_create_order'))

        # Handle creating order
        elif 'create_order' in request.form:
            if not admin_cart:
                flash('Vui lòng thêm sản phẩm vào đơn hàng!', 'danger')
                return redirect(url_for('admin_create_order'))

            if form.validate_on_submit():
                try:
                    # Check if customer exists by phone number
                    customer = Customer.query.filter_by(phone_number=form.customer_phone.data).first()

                    if not customer:
                        # Create new customer
                        # Generate username from phone number
                        username = form.customer_phone.data.replace(' ', '').replace('+', '')
                        base_username = username

                        # Ensure unique username
                        counter = 1
                        while Customer.query.filter_by(username=username).first():
                            username = f"{base_username}_{counter}"
                            counter += 1

                        # Split name into first and last name
                        customer_name = form.customer_name.data.strip()
                        name_parts = customer_name.split(' ', 1)
                        first_name = name_parts[0] if name_parts else ''
                        last_name = name_parts[1] if len(name_parts) > 1 else ''

                        customer = Customer(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=form.customer_email.data or None,
                            phone_number=form.customer_phone.data,
                            is_active=True
                        )
                        db.session.add(customer)
                        db.session.flush()  # Get customer ID

                        flash(f'Đã tạo tài khoản mới cho khách hàng {customer_name}!', 'info')
                    else:
                        # Update existing customer information if provided
                        if form.customer_name.data and form.customer_name.data != customer.first_name + ' ' + customer.last_name:
                            name_parts = form.customer_name.data.strip().split(' ', 1)
                            customer.first_name = name_parts[0] if name_parts else ''
                            customer.last_name = name_parts[1] if len(name_parts) > 1 else ''

                        if form.customer_email.data and form.customer_email.data != customer.email:
                            customer.email = form.customer_email.data

                        flash(f'Đã cập nhật thông tin khách hàng {customer.first_name} {customer.last_name}!', 'info')

                    # Create order
                    invoice = secrets.token_hex(5)
                    order = Order(
                        invoice=invoice,
                        customer_id=customer.id,
                        status='delivered',  # Admin orders are delivered immediately
                        payment_status='paid',  # Payment completed at counter
                        delivery_method='instore_pickup',  # At store pickup
                        payment_method=form.payment_method.data,
                        total_amount=total_amount,
                        notes=form.notes.data or None
                    )

                    db.session.add(order)
                    db.session.flush()  # Get order ID

                    # Create order items
                    for product_id, item in admin_cart.items():
                        product = Product.query.get(int(product_id))
                        if product:
                            quantity = int(item.get('quantity', 0))
                            discount = float(item.get('discount', 0))

                            order_item = OrderItem(
                                order_id=order.id,
                                product_id=int(product_id),
                                quantity=quantity,
                                unit_price=product.price,
                                discount=discount
                            )
                            db.session.add(order_item)

                            # Update product stock
                            product.stock -= quantity

                    db.session.commit()

                    # Clear admin cart
                    session.pop('admin_cart', None)

                    # Generate QR code for payment if selected
                    qr_data = None
                    qr_code_url = None
                    if form.payment_method.data == 'qr_code':
                        qr_data = {
                            'amount': total_amount,
                            'invoice': invoice,
                            'customer': form.customer_name.data,
                            'phone': form.customer_phone.data
                        }

                        # Generate QR code
                        if QRCODE_AVAILABLE:
                            try:
                                # Create QR code data (you can customize this format for your payment gateway)
                                qr_content = f"BANK_TRANSFER\nAMOUNT:{total_amount}\nINVOICE:{invoice}\nCUSTOMER:{form.customer_name.data}\nPHONE:{form.customer_phone.data}"

                                # Generate QR code
                                qr = qrcode.QRCode(
                                    version=1,
                                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                                    box_size=10,
                                    border=4,
                                )
                                qr.add_data(qr_content)
                                qr.make(fit=True)

                                # Create QR code image
                                img = qr.make_image(fill_color="black", back_color="white")

                                # Convert to base64 for display in HTML
                                buffered = BytesIO()
                                img.save(buffered, format="PNG")
                                qr_code_url = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

                            except Exception as e:
                                current_app.logger.error(f"Error generating QR code: {str(e)}")
                                qr_code_url = None
                        else:
                            current_app.logger.warning("qrcode library not available, using placeholder")
                            qr_code_url = None

                    flash(f'Đơn hàng #{invoice} đã được tạo thành công!', 'success')

                    # Redirect to order detail or payment page
                    if form.payment_method.data == 'qr_code':
                        return render_template('admin/order_qr_payment.html',
                                             order=order,
                                             customer=customer,
                                             qr_data=qr_data,
                                             qr_code_url=qr_code_url,
                                             cart_items=cart_items,
                                             total_amount=total_amount)
                    else:
                        return redirect(url_for('orders_manager'))

                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error creating admin order: {str(e)}")
                    flash('Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại!', 'danger')
                    return redirect(url_for('admin_create_order'))

    return render_template('admin/create_order.html',
                         form=form,
                         item_form=item_form,
                         products=products,
                         cart_items=cart_items,
                         admin_cart=admin_cart,
                         subtotal=subtotal,
                         total_discount=total_discount,
                         total_amount=total_amount,
                         total_quantity=total_quantity)


@app.route('/admin/orders/<int:order_id>/qr-payment')
def admin_order_qr_payment(order_id):
    """Display QR payment page for admin orders"""
    if 'email' not in session:
        flash('Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    order = Order.query.get_or_404(order_id)

    # Get order items
    from shop.customers.routes import get_order_data
    order_data = get_order_data(order)

    total_quantity = 0
    total_amount = 0
    if order_data:
        for key, product in order_data.items():
            total_quantity += int(product['quantity'])
            total_amount += float(product['price']) * int(product['quantity']) * (1 - float(product.get('discount', 0))/100)

    qr_data = {
        'amount': order.total_amount,
        'invoice': order.invoice,
        'customer': order.customer.first_name + ' ' + order.customer.last_name,
        'phone': order.customer.phone_number
    }

    return render_template('admin/order_qr_payment.html',
                         order=order,
                         qr_data=qr_data,
                         total_quantity=total_quantity,
                         total_amount=total_amount)


@app.route('/admin/orders/clear-cart')
def admin_clear_cart():
    """Clear admin cart"""
    if 'email' not in session:
        flash('Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    session.pop('admin_cart', None)
    flash('Đã xóa toàn bộ giỏ hàng!', 'success')
    return redirect(url_for('admin_create_order'))



@app.route('/admin/api/session-status', methods=['GET'])
def session_status():
    """Check admin session status"""
    return jsonify({
        'logged_in': 'email' in session,
        'admin_email': session.get('email', None),
        'session_keys': list(session.keys()),
        'csrf_token': session.get('csrf_token', 'NO_TOKEN'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/admin/api/test-no-csrf', methods=['POST'])
def test_no_csrf():
    """Test API without CSRF requirement"""
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'API works without CSRF!',
            'received_data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/admin/debug', methods=['GET'])
def debug_page():
    """Debug page to check admin login status"""
    return f"""
    <h1>Admin Debug Page</h1>
    <h2>Session Status:</h2>
    <ul>
        <li>Logged in: {'email' in session}</li>
        <li>Admin email: {session.get('email', 'None')}</li>
        <li>Session keys: {list(session.keys())}</li>
    </ul>

    <h3>Test API Calls:</h3>
    <button onclick="testAPI()" style="margin-right: 10px; background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Test API with CSRF</button>
    <button onclick="testAPINoCSRF()" style="margin-right: 10px; background-color: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Test API without CSRF</button>
    <button onclick="checkSession()" style="background-color: #17a2b8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Check Session Details</button>
    <div id="apiResult" style="margin-top: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background-color: #f8f9fa; min-height: 200px;"></div>

    <p><a href="/admin/login">Login</a> | <a href="/admin/orders/create">Create Order</a></p>

    <script>
    function testAPI() {{
        const csrfToken = '{session.get('csrf_token', '')}';
        console.log('Testing API with CSRF token:', csrfToken);

        document.getElementById('apiResult').innerHTML = '<div style="color: blue;">⏳ Testing API with CSRF...</div>';

        fetch('/admin/api/check-customer-phone', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }},
            body: JSON.stringify({{ phone_number: '0971010281' }})
        }})
        .then(response => {{
            console.log('API Response status:', response.status);
            console.log('API Response headers:', response.headers.get('content-type'));

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {{
                return response.text().then(html => {{
                    console.log('Received HTML response instead of JSON');
                    throw new Error('Server returned HTML instead of JSON. Check if you are logged in.');
                }});
            }}

            return response.json().then(data => {{
                if (!response.ok) {{
                    throw new Error(data.error || `HTTP ${{response.status}}`);
                }}
                return data;
            }});
        }})
        .then(data => {{
            console.log('API Success:', data);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: green;">✅ API Test with CSRF Successful!</div>' +
                '<pre style="background: #f0f8f0; padding: 10px; margin-top: 10px; border-radius: 4px;">' +
                JSON.stringify(data, null, 2) + '</pre>';
        }})
        .catch(error => {{
            console.error('API Error:', error);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: red;">❌ API Test with CSRF Failed!</div>' +
                '<div style="color: red; margin-top: 10px;"><strong>Error:</strong> ' + error.message + '</div>' +
                '<div style="color: #666; margin-top: 10px; font-size: 12px;">Check console (F12) for more details</div>';
        }});
    }}

    function testAPINoCSRF() {{
        console.log('Testing API without CSRF...');

        document.getElementById('apiResult').innerHTML = '<div style="color: green;">⏳ Testing API without CSRF...</div>';

        fetch('/admin/api/test-no-csrf', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{ test: 'data', phone: '0971010281' }})
        }})
        .then(response => {{
            console.log('No-CSRF Response status:', response.status);
            return response.json().then(data => {{
                console.log('No-CSRF Response data:', data);
                return data;
            }});
        }})
        .then(data => {{
            console.log('No-CSRF Success:', data);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: green;">✅ API Test without CSRF Successful!</div>' +
                '<pre style="background: #f0f8f0; padding: 10px; margin-top: 10px; border-radius: 4px;">' +
                JSON.stringify(data, null, 2) + '</pre>';
        }})
        .catch(error => {{
            console.error('No-CSRF Error:', error);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: red;">❌ API Test without CSRF Failed!</div>' +
                '<div style="color: red; margin-top: 10px;"><strong>Error:</strong> ' + error.message + '</div>' +
                '<div style="color: #666; margin-top: 10px; font-size: 12px;">Check console (F12) for more details</div>';
        }});
    }}

    function checkSession() {{
        console.log('Checking session status...');

        document.getElementById('apiResult').innerHTML = '<div style="color: #17a2b8;">⏳ Checking session details...</div>';

        fetch('/admin/api/session-status')
        .then(response => response.json())
        .then(data => {{
            console.log('Session data:', data);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: #17a2b8;">✅ Session Check Complete!</div>' +
                '<pre style="background: #e7f3ff; padding: 10px; margin-top: 10px; border-radius: 4px;">' +
                JSON.stringify(data, null, 2) + '</pre>';
        }})
        .catch(error => {{
            console.error('Session check error:', error);
            document.getElementById('apiResult').innerHTML =
                '<div style="color: red;">❌ Session Check Failed!</div>' +
                '<div style="color: red; margin-top: 10px;"><strong>Error:</strong> ' + error.message + '</div>' +
                '<div style="color: #666; margin-top: 10px; font-size: 12px;">Check console (F12) for more details</div>';
        }});
    }}
    </script>
    """

@app.route('/admin/api/check-customer-phone', methods=['POST'])
def api_check_customer_phone():
    """API to check if customer exists by phone number"""

    if 'email' not in session:
        current_app.logger.warning("Unauthorized access attempt - no email in session")
        # Return JSON response for API calls, not HTML redirect
        return jsonify({
            'error': 'Unauthorized - please login again',
            'redirect_url': url_for('login'),
            'session_expired': True
        }), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        phone_number = data.get('phone_number', '').strip()

        if not phone_number:
            return jsonify({'error': 'Số điện thoại không được để trống'}), 400

        # Validate phone number format
        if not phone_number.isdigit() or len(phone_number) < 10 or len(phone_number) > 15:
            return jsonify({'error': 'Số điện thoại không hợp lệ'}), 400

        customer = Customer.query.filter_by(phone_number=phone_number).first()

        if customer:
            customer_data = {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email or '',
                'phone_number': customer.phone_number,
                'full_name': f"{customer.first_name} {customer.last_name}".strip(),
                'is_active': customer.is_active
            }
            return jsonify({
                'exists': True,
                'customer': customer_data
            })
        else:
            return jsonify({
                'exists': False,
                'message': 'Số điện thoại chưa được đăng ký trong hệ thống'
            })

    except Exception as e:
        current_app.logger.error(f"Error checking customer phone: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Có lỗi xảy ra khi kiểm tra số điện thoại'}), 500

