from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, bcrypt
from shop.models import Register, Admin, CustomerOrder
from .forms import CustomerRegisterForm, CustomerLoginFrom
from shop.models import Category, Brand, Addproduct
from shop.carts.routes import clearcart, MagerDicts
from shop.email_utils import send_order_confirmation_email, send_order_status_update_email
from flask import Markup
import secrets
import os
import json
from datetime import datetime

# import pdfkit
# import stripe
def brands():
    # brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    brands = Brand.query.all()
    return brands


def categories():
    # categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    categories = Category.query.order_by(Category.name.desc()).all()
    return categories


def get_order_data(order):
    """Helper function to parse order data from JSON"""
    if order.orders:
        try:
            parsed_data = json.loads(order.orders)
            print(f"DEBUG: Parsed order data for order {order.invoice}: {len(parsed_data)} products")
            return parsed_data
        except Exception as e:
            print(f"DEBUG: Error parsing order data for order {order.invoice}: {e}")
            return {}
    print(f"DEBUG: No orders data for order {order.invoice}")
    return {}


@app.route('/myaccount', methods=['GET', 'POST'])
@login_required
def update_account():
    detail_customer = Register.query.get_or_404(current_user.id)
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    phone_number = request.form.get('phone')
    gender = request.form.get('gender')
    if request.method == "POST":
        if detail_customer.email != email:
            if Register.query.filter_by(email=email).first():
                flash(f'Email Used!', 'danger')
                return redirect(url_for('update_account'))
        if detail_customer.phone_number != phone_number:
            if Register.query.filter_by(phone_number=phone_number).first():
                flash(f'Phone Number Used!', 'danger')
                return redirect(url_for('update_account'))
        detail_customer.first_name = first_name
        detail_customer.last_name = last_name
        detail_customer.email = email
        detail_customer.phone_number = phone_number
        detail_customer.gender = gender
        flash(f'Cập nhật thành công', 'success')
        db.session.commit()
        return redirect(url_for('update_account'))
    return render_template('customers/myaccount.html', detail_customer=detail_customer, brands=brands(),
                           categories=categories(), get_order_data=get_order_data)


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    detail_password_customer = Register.query.get_or_404(current_user.id)
    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if request.method == "POST":
        if not bcrypt.check_password_hash(detail_password_customer.password, old_password.encode('utf8')):
            flash(f'Mật khẩu cũ không khớp!', 'danger')
            return redirect(url_for('change_password'))

        detail_password_customer.password = bcrypt.generate_password_hash(new_password).decode('utf8')
        flash(f'Change Password Complete!', 'success')
        db.session.commit()
        return redirect(url_for('change_password'))
    return render_template('customers/myaccount.html', detail_password_customer=detail_password_customer,
                           brands=brands(),
                           categories=categories(), get_order_data=get_order_data)


@app.route('/register', methods=['GET', 'POST'])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        # Kiểm tra email đã tồn tại chưa
        if Admin.query.filter_by(email=form.email.data).first():
            flash(f'Email đã được sử dụng!', 'danger')
            return redirect(url_for('customer_register'))
        if Register.query.filter_by(email=form.email.data).first():
            flash(f'Email đã được đăng ký!', 'danger')
            return redirect(url_for('customer_register'))
        
        # Kiểm tra username đã tồn tại chưa
        if Register.query.filter_by(username=form.username.data).first():
            flash(f'Tên đăng nhập đã được sử dụng!', 'danger')
            return redirect(url_for('customer_register'))
        
        # Kiểm tra số điện thoại đã tồn tại chưa
        if Register.query.filter_by(phone_number=form.phone_number.data).first():
            flash(f'Số điện thoại đã được đăng ký!', 'danger')
            return redirect(url_for('customer_register'))
        
        try:
            # Tạo user mới
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
            register = Register(
                username=form.username.data, 
                email=form.email.data, 
                first_name=form.first_name.data,
                last_name=form.last_name.data, 
                phone_number=form.phone_number.data,
                gender=form.gender.data,
                password=hash_password,
                date_created=datetime.utcnow(),
                lock=False
            )
            db.session.add(register)
            db.session.commit()
            
            flash(f'Chào mừng {form.first_name.data} {form.last_name.data}! Cảm ơn bạn đã đăng ký', 'success')
            return redirect(url_for('customer_login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra khi đăng ký! Vui lòng thử lại.', 'danger')
            return redirect(url_for('customer_register'))

    return render_template('customers/register.html', form=form, brands=brands(), categories=categories())


@app.route('/login', methods=['GET', 'POST'])
def customer_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        # Register.query.filter_by(lock=False).first()
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data.encode('utf8')):
            if user.lock == True:
                flash(Markup(
                    "Account has been locked ! <a href='mailto: viethoang@gmail.com' class='alert-link' >Help here</a>"),
                    'danger')
                return redirect(url_for('customer_login'))
            login_user(user)

            # Xu ly gio hang
            if 'Shoppingcart' in session:
                orders = CustomerOrder.query.filter(CustomerOrder.customer_id == current_user.id).filter(
                    CustomerOrder.status == None).order_by(CustomerOrder.id.desc()).all()
                product_id = [order.orders for order in orders]
                for key, item in session['Shoppingcart'].items():
                    if key not in product_id:
                        customer_id = current_user.id
                        invoice = secrets.token_hex(5)
                        order = CustomerOrder(invoice=invoice, customer_id=customer_id,
                                              orders=json.dumps({key: session['Shoppingcart'][key]}),
                                              status=None)
                        db.session.add(order)
                        db.session.commit()
            session.pop('Shoppingcart', None)
            orders = CustomerOrder.query.filter(CustomerOrder.customer_id == current_user.id).filter(
                CustomerOrder.status == None).order_by(CustomerOrder.id.desc()).all()
            session.modified = True
            for order in orders:
                if order.orders:
                    order_data = json.loads(order.orders)
                    for product_id, DictItems in order_data.items():
                        DictItems = {product_id: DictItems}
                        if 'Shoppingcart' not in session:
                            session['Shoppingcart'] = DictItems
                        else:
                            session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)

            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Email hoặc mật khẩu không đúng', 'danger')
        return redirect(url_for('customer_login'))
    return render_template('customers/login.html', form=form, brands=brands(), categories=categories())


@app.route('/login/<string:page>_<int:id>', methods=['GET', 'POST'])
def customer_login_page(page, id):
    if current_user.is_authenticated:
        if page == "rate":
            return redirect(url_for('detail', id))
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data.encode('utf8')):
            login_user(user)
            return redirect(url_for('detail', id=id))
        flash('Email hoặc mật khẩu không đúng', 'danger')
        return redirect(url_for('customer_login_page', page=page, id=id))
    return render_template('customers/login.html', form=form, brands=brands(), categories=categories())


@app.route('/logout')
@login_required
def customer_logout():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    logout_user()
    clearcart()
    return redirect(url_for('home'))


@app.route('/getorder/')
@login_required
def get_order():
    if not current_user.is_authenticated:
        return redirect(url_for('customer_login'))
    
    # Check if cart is empty
    if 'Shoppingcart' not in session or not session['Shoppingcart']:
        flash('Giỏ hàng trống!', 'danger')
        return redirect(url_for('getCart'))
    
    customer_id = current_user.id
    customer = Register.query.filter_by(id=customer_id).first()
    
    # Calculate totals from session cart
    subtotals = 0
    discounttotal = 0
    for key, product in session['Shoppingcart'].items():
        discounttotal += float(product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
        subtotals += float(product['price']) * int(product['quantity'])
    subtotals -= discounttotal
    
    return render_template('customers/order.html', subtotals=subtotals, customer=customer,
                           brands=brands(), categories=categories(), get_order_data=get_order_data)


@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    address = request.form.get('CustomerAddress')

    if request.method == "POST":
        try:
            # Create new order from session cart
            if 'Shoppingcart' in session and session['Shoppingcart']:
                customer_id = current_user.id
                invoice = secrets.token_hex(5)
                order = CustomerOrder(invoice=invoice, customer_id=customer_id,
                                      orders=json.dumps(session['Shoppingcart']),
                                      status="Đang xác nhận", address=address,
                                      payment_status="Chưa thanh toán", payment_method="cod")
                db.session.add(order)
                db.session.commit()

                # Gửi email xác nhận đơn hàng
                customer = Register.query.get(customer_id)
                if customer and customer.email:
                    email_sent = send_order_confirmation_email(customer, order)
                    if email_sent:
                        print(f"Email xác nhận đã gửi đến {customer.email}")
                    else:
                        print(f"Không thể gửi email xác nhận đến {customer.email}")

                # Clear cart
                session.pop('Shoppingcart', None)
                flash('Đơn hàng đã được đặt thành công! Email xác nhận đã được gửi đến địa chỉ email của bạn.', 'success')
            else:
                flash('Giỏ hàng trống!', 'danger')

        except Exception as e:
            print("Submit Order Error:", e)
            flash('Có lỗi xảy ra khi đặt hàng', 'danger')

    return redirect(url_for('payment_history'))


@app.route('/payment_history')
@login_required
def payment_history():
    # Get orders and update old statuses to new ones
    orders = CustomerOrder.query.filter(CustomerOrder.customer_id == current_user.id).filter(
        CustomerOrder.status != None).order_by(CustomerOrder.id.desc()).all()
    
    # Calculate totals for each order
    orders_with_totals = []
    for order in orders:
        # Update old statuses to new ones in memory (for display)
        if order.status == 'Pending':
            order.status = 'Đang xác nhận'
        elif order.status == 'Accepted':
            order.status = 'Đã giao'
        elif order.status == 'Cancelled':
            order.status = 'Hủy đơn'
        
        # Calculate totals
        order_data = get_order_data(order)
        total_quantity = 0
        total_amount = 0
        
        if order_data:
            for key, product in order_data.items():
                product_total = float(product['price']) * int(product['quantity'])
                # Safely get discount, default to 0 if not found
                product_discount_percent = float(product.get('discount', 0))
                product_discount = (product_discount_percent / 100) * product_total
                total_quantity += int(product['quantity'])
                total_amount += (product_total - product_discount)
        
        orders_with_totals.append({
            'order': order,
            'total_quantity': total_quantity,
            'total_amount': total_amount
        })
    
    return render_template('customers/myaccount.html', orders_with_totals=orders_with_totals, brands=brands(), categories=categories(), get_order_data=get_order_data)


@app.route('/order_detail/<invoice>')
@login_required
def order_detail(invoice):
    if not current_user.is_authenticated:
        return redirect(url_for('customer_login'))
    
    # Get the specific order by invoice
    order = CustomerOrder.query.filter_by(
        invoice=invoice, 
        customer_id=current_user.id
    ).first()
    
    if not order:
        flash('Không tìm thấy đơn hàng!', 'danger')
        return redirect(url_for('payment_history'))
    
    # Debug: Print order data
    print(f"DEBUG: Order {order.invoice} - Raw orders data: {order.orders}")
    
    # Calculate totals in Python
    order_data = get_order_data(order)
    total_before_discount = 0
    total_discount = 0
    
    if order_data:
        for key, product in order_data.items():
            product_total = float(product['price']) * int(product['quantity'])
            product_discount = (float(product.get('discount', 0)) / 100) * product_total
            total_before_discount += product_total
            total_discount += product_discount
    
    final_total = total_before_discount - total_discount
    
    print(f"DEBUG: Calculated totals - Before: {total_before_discount}, Discount: {total_discount}, Final: {final_total}")
    
    # Update old statuses to new ones in memory (for display)
    if order.status == 'Pending':
        order.status = 'Đang xác nhận'
    elif order.status == 'Accepted':
        order.status = 'Đã giao'
    elif order.status == 'Cancelled':
        order.status = 'Hủy đơn'
    
    # Get customer info
    customer = Register.query.filter_by(id=current_user.id).first()
    
    return render_template('customers/order_detail.html', 
                         order=order, 
                         customer=customer,
                         brands=brands(), 
                         categories=categories(), 
                         get_order_data=get_order_data,
                         total_before_discount=total_before_discount,
                         total_discount=total_discount,
                         final_total=final_total)


@app.route('/cancel_order/<invoice>', methods=['POST'])
@login_required
def cancel_order(invoice):
    """Cancel an order"""
    if not current_user.is_authenticated:
        return redirect(url_for('customer_login'))
    
    # Get the specific order by invoice
    order = CustomerOrder.query.filter_by(
        invoice=invoice, 
        customer_id=current_user.id
    ).first()
    
    if not order:
        flash('Không tìm thấy đơn hàng!', 'danger')
        return redirect(url_for('payment_history'))
    
    # Check if order can be cancelled (only pending orders)
    if order.status != 'Đang xác nhận':
        flash('Chỉ có thể hủy đơn hàng đang xác nhận!', 'warning')
        return redirect(url_for('order_detail', invoice=invoice))
    
    try:
        # Update order status to cancelled
        order.status = 'Hủy đơn'
        db.session.commit()

        # Send email notification to customer
        send_order_status_update_email(current_user, order, action_by="customer")

        flash('Đơn hàng đã được hủy thành công!', 'success')
    except Exception as e:
        print("Cancel Order Error:", e)
        flash('Có lỗi xảy ra khi hủy đơn hàng', 'danger')
    
    return redirect(url_for('order_detail', invoice=invoice))


@app.route('/debug_order_data/<invoice>')
@login_required
def debug_order_data(invoice):
    """Debug route to check order data"""
    order = CustomerOrder.query.filter_by(
        invoice=invoice, 
        customer_id=current_user.id
    ).first()
    
    if not order:
        return "Order not found"
    
    order_data = get_order_data(order)
    
    # Calculate totals manually
    total_before_discount = 0
    total_discount = 0
    
    if order_data:
        for key, product in order_data.items():
            product_total = float(product['price']) * int(product['quantity'])
            product_discount = (float(product.get('discount', 0)) / 100) * product_total
            total_before_discount += product_total
            total_discount += product_discount
    
    final_total = total_before_discount - total_discount
    
    debug_info = {
        'order_id': order.id,
        'invoice': order.invoice,
        'status': order.status,
        'address': order.address,
        'raw_orders': order.orders,
        'parsed_orders': order_data,
        'order_count': len(order_data) if order_data else 0,
        'total_before_discount': total_before_discount,
        'total_discount': total_discount,
        'final_total': final_total
    }
    
    return f"""
    <h2>Debug Order Info</h2>
    <pre>{debug_info}</pre>

    <h3>Raw Orders Data:</h3>
    <pre>{order.orders}</pre>

    <h3>Parsed Orders:</h3>
    <pre>{order_data}</pre>

    <h3>Calculations:</h3>
    <p>Total before discount: {total_before_discount}</p>
    <p>Total discount: {total_discount}</p>
    <p>Final total: {final_total}</p>
    """


@app.route('/test_email/<invoice>')
@login_required
def test_email(invoice):
    """Test route để gửi email xác nhận đơn hàng"""
    if not current_user.is_authenticated:
        return "Vui lòng đăng nhập trước"

    # Tìm đơn hàng
    order = CustomerOrder.query.filter_by(
        invoice=invoice,
        customer_id=current_user.id
    ).first()

    if not order:
        return f"Không tìm thấy đơn hàng với mã {invoice}"

    # Gửi email test
    email_sent = send_order_confirmation_email(current_user, order)

    if email_sent:
        return f"""
        <h2>✅ Email đã gửi thành công!</h2>
        <p>Đã gửi email xác nhận đến: {current_user.email}</p>
        <p>Mã đơn hàng: {invoice}</p>
        <a href="{url_for('payment_history')}">Quay lại lịch sử đơn hàng</a>
        """
    else:
        return f"""
        <h2>❌ Gửi email thất bại!</h2>
        <p>Không thể gửi email đến: {current_user.email}</p>
        <p>Mã đơn hàng: {invoice}</p>
        <a href="{url_for('payment_history')}">Quay lại lịch sử đơn hàng</a>
        """


@app.route('/test_email_config')
def test_email_config():
    """Test route để kiểm tra cấu hình email"""
    from shop import mail

    try:
        # Kiểm tra cấu hình mail
        config_info = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USE_SSL': app.config.get('MAIL_USE_SSL'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER'),
            'HAS_MAIL_PASSWORD': bool(app.config.get('MAIL_PASSWORD'))
        }

        return f"""
        <h2>Mail Configuration Test</h2>
        <pre>{config_info}</pre>

        <h3>Test Results:</h3>
        <p>Mail object initialized: {'✅' if mail else '❌'}</p>
        <p>Mail server configured: {'✅' if config_info['MAIL_SERVER'] else '❌'}</p>
        <p>Mail credentials: {'✅' if config_info['HAS_MAIL_PASSWORD'] else '❌'}</p>

        <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
            <h4>⚠️ Lưu ý cấu hình:</h4>
            <p>Để gửi email thực sự, bạn cần:</p>
            <ol>
                <li>Thay 'your-email@gmail.com' bằng email thật của bạn</li>
                <li>Thay 'your-app-password' bằng App Password từ Gmail</li>
                <li>Kiểm tra file shop/__init__.py</li>
            </ol>
        </div>
        """
    except Exception as e:
        return f"<h2>Error testing mail config:</h2><p>{e}</p>"



