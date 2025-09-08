import os
import urllib
from itertools import product
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from flask import render_template, session, request, redirect, url_for, flash, current_app
from shop import app, db, bcrypt
import json
from shop.models import Brand, Category, Addproduct, Register, Admin, CustomerOrder, Rate, Article
from .forms import LoginForm, RegistrationForm
from shop.customers.forms import CustomerRegisterForm


# def synchronization():
#     try:
#         urllib.request.urlopen("https://console.firebase.google.com/")  # Python 3.x
#         ls = ['background.png', 'Assets.png', 'bg.jpg', 'AdminLTELogo.png']
#         for i in ls:
#             if not os.path.isfile(os.path.join(current_app.root_path, "static/images/" + i)):
#                 storage.child("images/" + i).download(
#                     os.path.join(current_app.root_path, "static/images/" + i))
#         products = Addproduct.query.all();
#         for product in products:
#             if not os.path.isfile(os.path.join(current_app.root_path, "static/images/" + product.image_1)):
#                 storage.child("images/" + product.image_1).download(
#                     os.path.join(current_app.root_path, "static/images/" + product.image_1))
#             if not os.path.isfile(os.path.join(current_app.root_path, "static/images/" + product.image_2)):
#                 storage.child("images/" + product.image_2).download(
#                     os.path.join(current_app.root_path, "static/images/" + product.image_2))
#             if not os.path.isfile(os.path.join(current_app.root_path, "static/images/" + product.image_3)):
#                 storage.child("images/" + product.image_3).download(
#                     os.path.join(current_app.root_path, "static/images/" + product.image_3))
#         return True
#     except:
#         return False


# @app.route('/synchronization')
# def data_syn():
#     if 'email' not in session:
#         flash(f'Yêu cầu đăng nhập', 'danger')
#         return redirect(url_for('login'))
#     if synchronization():
#         flash(f'Synchronization Data Success', 'success')
#         return redirect(url_for('admin_manager'))
#     else:
#         flash(f'Synchronization Data Failure, Please Reconnect Internet', 'danger')
#         return redirect(url_for('admin_manager'))


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
    # page = request.args.get('page', 1, type=int)
    user = Admin.query.filter_by(email=session['email']).all()
    customers = Register.query.all()
    # products = Addproduct.query.order_by(Addproduct.id.desc())
    # orders = CustomerOrder.query.filter(CustomerOrder.status != None).filter(
    #     CustomerOrder.status != "Cancelled").order_by(CustomerOrder.id.desc()).paginate(page=page, per_page=10)\

    # Get all orders and update old statuses to new ones
    orders = CustomerOrder.query.filter(CustomerOrder.status != None).order_by(CustomerOrder.id.desc()).all()

    # Update old statuses to new ones in memory (for display)
    for order in orders:
        if order.status == 'Pending':
            order.status = 'Đang xác nhận'
        elif order.status == 'Accepted':
            order.status = 'Đã giao'
        elif order.status == 'Cancelled':
            order.status = 'Hủy đơn'

        # Calculate totals for each order
        order_data = get_order_data(order)
        total_quantity = 0
        total_price = 0

        if order_data and isinstance(order_data, dict):
            for key, product in order_data.items():
                if product and isinstance(product, dict):
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
                        discount_amount = int(price * discount / 100)
                        item_total = (price - discount_amount) * quantity
                        total_price += item_total

        # Add calculated totals and product details to order object
        order.total_quantity = total_quantity
        order.total_price = total_price
        order.product_details = order_data if order_data else {}

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
        flash('Đơn hàng đã được cập nhật thành "Đã giao"', 'success')
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
    # products = Addproduct.query.all()
    # page = request.args.get('page', 1, type=int)
    # products = Addproduct.query.order_by(Addproduct.id.desc()).paginate(page=page, per_page=10)
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
    print(f"DEBUG: Order ID {order.id}")
    print(f"DEBUG: Raw orders field: {order.orders}")
    print(f"DEBUG: Orders field type: {type(order.orders)}")
    print(f"DEBUG: Orders field is None: {order.orders is None}")

    if order.orders:
        try:
            parsed_data = json.loads(order.orders)
            print(f"DEBUG: Successfully parsed: {parsed_data}")
            print(f"DEBUG: Parsed type: {type(parsed_data)}")
            print(f"DEBUG: Parsed length: {len(parsed_data) if isinstance(parsed_data, dict) else 'N/A'}")
            return parsed_data
        except Exception as e:
            print(f"DEBUG: JSON parse error: {e}")
            return {}
    print("DEBUG: No orders data found")
    return {}


# ============= TEST ROUTE FOR DEBUGGING =============
@app.route('/admin/test_orders')
def test_orders():
    """Test route to check order data structure"""
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    # Get all orders
    orders = CustomerOrder.query.filter(CustomerOrder.status != None).order_by(CustomerOrder.id.desc()).limit(5).all()

    test_results = []
    for order in orders:
        result = {
            'order_id': order.id,
            'invoice': order.invoice,
            'status': order.status,
            'raw_orders': order.orders,
            'orders_type': str(type(order.orders)),
            'orders_is_none': order.orders is None,
            'parsed_data': get_order_data(order)
        }
        test_results.append(result)

    return render_template('admin/test_orders.html', test_results=test_results)


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
