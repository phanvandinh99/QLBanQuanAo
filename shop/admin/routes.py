import os
import urllib
from itertools import product
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from flask import render_template, session, request, redirect, url_for, flash, current_app, jsonify
from shop import app, db, bcrypt
import json
from shop.models import Brand, Category, Addproduct, Register, Admin, CustomerOrder, Rate, Article
from shop.email_utils import send_order_status_update_email

# Import reportlab modules at module level to avoid import errors
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
        if Register.query.filter_by(email=form.email.data).first():
            flash(f'Email Used!', 'danger')
            return redirect(url_for('admin_register_custormer'))
        if Register.query.filter_by(phone_number=form.phone_number.data).first():
            flash(f'Phone Number Used!', 'danger')
            return redirect(url_for('admin_register_custormer'))
        try:
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
            register = Register(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                                last_name=form.last_name.data, phone_number=form.phone_number.data,
                                gender=form.gender.data,
                                password=hash_password)
            db.session.add(register)
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
    customers = Register.query.all()
    
    # Kiểm tra xem mỗi customer có thể xóa hay không
    for customer in customers:
        customer_orders = CustomerOrder.query.filter_by(customer_id=customer.id).all()
        customer.can_delete = len(customer_orders) == 0
    
    return render_template('admin/customer_manager.html', title='Customer manager page', user=user[0],
                           customers=customers)


@app.route('/admin/orders')
def orders_manager():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    user = Admin.query.filter_by(email=session['email']).all()
    customers = Register.query.all()

    # Get all orders and update old statuses to new ones
    orders = CustomerOrder.query.filter(CustomerOrder.status != None).order_by(CustomerOrder.id.desc()).all()

    # Update old statuses to new ones in memory (for display)
    for order in orders:
        # Update order status
        if order.status == 'Pending':
            order.status = 'Đang xác nhận'
        elif order.status == 'Accepted':
            order.status = 'Đã giao'
        elif order.status == 'Cancelled':
            order.status = 'Hủy đơn'

        # Add payment status display
        if hasattr(order, 'payment_status'):
            # For COD orders, payment status should be "Chưa thanh toán"
            # For VNPAY orders, payment status should be "Đã thanh toán"
            if order.payment_method == 'cod':
                order.display_payment_status = 'Chưa thanh toán'
            elif order.payment_method == 'vnpay':
                order.display_payment_status = 'Đã thanh toán'
            else:
                order.display_payment_status = order.payment_status or 'N/A'
        else:
            order.display_payment_status = 'N/A'

        # Calculate totals for each order
        order_data = get_order_data(order)
        total_quantity = 0
        total_price = 0

        # Initialize enhanced products dictionary
        enhanced_products = {}

        if order_data and isinstance(order_data, dict):
            for key, product in order_data.items():
                if product and isinstance(product, dict):
                    # Create enhanced product with original data
                    enhanced_product = product.copy()

                    quantity = product.get('quantity', 0)
                    price = product.get('price', 0)
                    discount = product.get('discount', 0)

                    # Convert to numbers
                    try:
                        quantity = int(quantity) if quantity else 0
                        price = int(price) if price else 0
                        discount = int(discount) if discount else 0
                    except (ValueError, TypeError):
                        quantity = 0
                        price = 0
                        discount = 0

                    # Calculate if quantity > 0
                    if quantity > 0:
                        total_quantity += quantity

                        # Calculate prices
                        original_price = price * quantity
                        discount_amount = int(price * discount / 100) if discount > 0 else 0
                        discounted_price_per_item = price - discount_amount
                        discounted_total_per_item = discounted_price_per_item * quantity

                        # Add calculated prices to enhanced product
                        enhanced_product['original_price'] = price
                        enhanced_product['discounted_price'] = discounted_price_per_item
                        enhanced_product['discount_amount'] = discount_amount
                        enhanced_product['original_total'] = original_price
                        enhanced_product['discounted_total'] = discounted_total_per_item

                        total_price += discounted_total_per_item

                    # Try to get product image from database if we have product ID
                    if 'id' in product or key.isdigit():
                        try:
                            from shop.models import Addproduct
                            product_id = product.get('id', key if key.isdigit() else None)
                            if product_id:
                                db_product = Addproduct.query.get(int(product_id))
                                if db_product and db_product.image_1:
                                    enhanced_product['image_1'] = db_product.image_1
                        except:
                            pass  # Ignore errors, image is optional

                    enhanced_products[key] = enhanced_product

        # Calculate order totals
        order.total_quantity = total_quantity
        order.total_price = total_price
        order.total_original_price = sum(p.get('original_total', 0) for p in enhanced_products.values())
        order.total_discount_amount = sum(p.get('discount_amount', 0) * p.get('quantity', 0) for p in enhanced_products.values())

        order.product_details = enhanced_products if enhanced_products else order_data

    return render_template('admin/manage_orders.html', title='Order manager page', user=user[0], orders=orders,
                           customers=customers)


@app.route('/accept_order/<int:id>', methods=['GET', 'POST'])
def accept_order(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    
    if request.method == "POST":
        customer_order = CustomerOrder.query.get_or_404(id)
        if customer_order.orders:
            order_data = json.loads(customer_order.orders)
            for key, product in order_data.items():
                product_order = Addproduct.query.get_or_404(key)
                if (product_order.stock - int(product['quantity'])) >= 0:
                    product_order.stock -= int(product['quantity'])
                    db.session.commit()
                    customer_order.status = 'Đang giao'
                    db.session.commit()
                else:
                    flash('Quantity in stock has been exhausted', 'danger')
                    return redirect(url_for('orders_manager'))

            # Send email notification to customer
            customer = Register.query.get(customer_order.customer_id)
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
        customer_order = CustomerOrder.query.get_or_404(id)
        customer_order.status = 'Đã giao'
        db.session.commit()

        # Send email notification to customer
        customer = Register.query.get(customer_order.customer_id)
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
        customer_order = CustomerOrder.query.get_or_404(id)

        # Only allow for instore pickup orders
        if customer_order.delivery_method != 'instore_pickup':
            flash('Chỉ áp dụng cho đơn hàng nhận tại cửa hàng!', 'warning')
            return redirect(url_for('orders_manager'))

        customer_order.status = 'Sẵn sàng nhận tại cửa hàng'
        db.session.commit()

        # Send email notification to customer
        customer = Register.query.get(customer_order.customer_id)
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
    customer = CustomerOrder.query.get_or_404(id)
    if request.method == "POST":
        customer.status = "Hủy đơn"
        db.session.commit()

        # Send email notification to customer
        customer_info = Register.query.get(customer.customer_id)
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
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        customer.lock = 1
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/unlock_customer/<int:id>', methods=['GET', 'POST'])
def unlock_customer(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    if request.method == "POST":
        customer.lock = 0
        db.session.commit()
        return redirect(url_for('customer_manager'))
    return redirect(url_for('customer_manager'))


@app.route('/delete_customer/<int:id>', methods=['GET', 'POST'])
def delete_customer(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    customer = Register.query.get_or_404(id)
    
    # Kiểm tra xem customer có đơn hàng nào không
    customer_orders = CustomerOrder.query.filter_by(customer_id=id).all()
    if customer_orders:
        flash(f"Tài khoản {customer.username} đã đặt hàng (Ràng buộc khóa) không thể xóa.", "danger")
        return redirect(url_for('customer_manager'))
    
    if request.method == "POST":
        # Xóa các đánh giá của customer trước
        rates = Rate.query.filter(Rate.register_id == id).all()
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
    products = Addproduct.query.all()
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
    """Helper function to parse order data from JSON"""
    if order.orders:
        try:
            return json.loads(order.orders)
        except Exception:
            return {}
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
        from shop.models import CustomerOrder, Addproduct, Register
        from flask import make_response, send_file, jsonify
        import io
        import json

        # Check if ReportLab is available
        if not REPORTLAB_AVAILABLE:
            return jsonify({'error': 'ReportLab library is not available. Please install it to export invoices.'}), 500

        # Lấy thông tin đơn hàng
        order = CustomerOrder.query.get_or_404(order_id)

        # Lấy thông tin khách hàng
        customer = Register.query.get(order.customer_id)

        if not customer:
            return jsonify({'error': 'Không tìm thấy thông tin khách hàng'}), 404

        # Parse dữ liệu sản phẩm
        order_data = get_order_data(order)
        products = []

        if order_data and isinstance(order_data, dict):
            for key, product in order_data.items():
                if product and isinstance(product, dict):
                    quantity = product.get('quantity', 0)
                    price = product.get('price', 0)
                    discount = product.get('discount', 0)

                    try:
                        quantity = int(quantity) if quantity else 0
                        price = int(price) if price else 0
                        discount = int(discount) if discount else 0
                    except (ValueError, TypeError):
                        quantity = 0
                        price = 0
                        discount = 0

                    if quantity > 0:
                        discount_amount = int(price * discount / 100) if discount > 0 else 0
                        final_price = price - discount_amount
                        total = final_price * quantity

                        # Lấy thông tin sản phẩm từ database nếu có
                        product_info = None
                        try:
                            if 'id' in product or str(key).isdigit():
                                product_id = product.get('id', key if str(key).isdigit() else None)
                                if product_id:
                                    product_info = Addproduct.query.get(int(product_id))
                        except:
                            pass

                        products.append({
                            'name': product.get('name', 'N/A'),
                            'brand': product_info.brand if product_info else product.get('brand', 'N/A'),
                            'color': product_info.colors if product_info else product.get('color', 'N/A'),
                            'quantity': quantity,
                            'original_price': price,
                            'discount': discount,
                            'final_price': final_price,
                            'total': total
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
        elements.append(Paragraph(ensure_unicode(f"<b>Ngày đặt:</b> {order.date_created.strftime('%d/%m/%Y %H:%M') if order.date_created else 'N/A'}"), info_style))
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
        elements.append(Paragraph(ensure_unicode(f"<b>Địa chỉ:</b> {order.address}"), info_style))
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
            discount_amount = product['original_price'] * product['quantity'] * product.get('discount', 0) / 100

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
        doc.build(elements)

        buffer.seek(0)

        # Trả về file PDF
        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f'hoa-don-{order_id}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error generating invoice: {str(e)}")
        return jsonify({'error': 'Có lỗi xảy ra khi tạo hóa đơn'}), 500
