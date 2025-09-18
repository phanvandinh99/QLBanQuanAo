from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, bcrypt
from shop.models import Customer, Admin, Order, OrderItem
from .forms import CustomerRegisterForm, CustomerLoginFrom
from shop.models import Category, Brand, Product
from shop.carts.routes import clearcart, MagerDicts
from shop.email_utils import send_order_confirmation_email, send_order_status_update_email
from flask import Markup
import secrets
import os
import json
from datetime import datetime

def brands():
    return Brand.query.all()


def categories():
    return Category.query.order_by(Category.name.desc()).all()


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
                'price': float(item.unit_price),  # Convert to float for VNĐ filter to work properly
                'discount': item.discount,
                'quantity': item.quantity,
                'color': getattr(item.product, 'colors', ''),
                'image': item.product.image_1
            }
        return order_data
    except Exception as e:
        print(f"Error getting order data: {e}")
        return {}


@app.route('/myaccount', methods=['GET', 'POST'])
@login_required
def update_account():
    detail_customer = Customer.query.get_or_404(current_user.id)
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    phone_number = request.form.get('phone')
    gender = request.form.get('gender')
    if request.method == "POST":
        if detail_customer.email != email:
            if Customer.query.filter_by(email=email).first():
                flash(f'Email Used!', 'danger')
                return redirect(url_for('update_account'))
        if detail_customer.phone_number != phone_number:
            if Customer.query.filter_by(phone_number=phone_number).first():
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
    detail_password_customer = Customer.query.get_or_404(current_user.id)
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
        if Admin.query.filter_by(email=form.email.data).first():
            flash(f'Email đã được sử dụng!', 'danger')
            return redirect(url_for('customer_register'))
        if Customer.query.filter_by(email=form.email.data).first():
            flash(f'Email đã được đăng ký!', 'danger')
            return redirect(url_for('customer_register'))
        
        if Customer.query.filter_by(username=form.username.data).first():
            flash(f'Tên đăng nhập đã được sử dụng!', 'danger')
            return redirect(url_for('customer_register'))
        
        if Customer.query.filter_by(phone_number=form.phone_number.data).first():
            flash(f'Số điện thoại đã được đăng ký!', 'danger')
            return redirect(url_for('customer_register'))
        
        try:
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
        user = Customer.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data.encode('utf8')):
            if not user.is_active:
                flash(Markup(
                    "Account has been locked ! <a href='mailto: viethoang@gmail.com' class='alert-link' >Help here</a>"),
                    'danger')
                return redirect(url_for('customer_login'))
            login_user(user)

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
        user = Customer.query.filter_by(email=form.email.data).first()
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
    
    if 'Shoppingcart' not in session or not session['Shoppingcart']:
        flash('Giỏ hàng trống!', 'danger')
        return redirect(url_for('getCart'))
    
    customer_id = current_user.id
    customer = Customer.query.filter_by(id=customer_id).first()
    
    subtotals = 0
    discounttotal = 0
    for key, product in session['Shoppingcart'].items():
        discounttotal += float(product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
        subtotals += float(product['price']) * int(product['quantity'])
    subtotals -= discounttotal
    
    return render_template('customers/order.html', subtotals=subtotals, customer=customer,
                           brands=brands(), categories=categories(), get_order_data=get_order_data)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    from shop.customers.forms import CheckoutForm
    form = CheckoutForm()

    if 'Shoppingcart' in session:
        subtotal = 0
        for key, item in session['Shoppingcart'].items():
            subtotal += float(item['price']) * int(item['quantity'])

        discount = 0
        for key, item in session['Shoppingcart'].items():
            if 'discount' in item:
                discount += (float(item['discount']) / 100) * (float(item['price']) * int(item['quantity']))

        total = subtotal - discount
    else:
        subtotal = 0
        discount = 0
        total = 0

    if form.validate_on_submit():
        if 'Shoppingcart' not in session or not session['Shoppingcart']:
            flash('Giỏ hàng trống. Vui lòng thêm sản phẩm vào giỏ hàng trước khi đặt hàng.', 'warning')
            return redirect(url_for('carts'))

        delivery_method = form.delivery_method.data
        payment_method = form.payment_method.data
        customer_address = form.customer_address.data.strip() if delivery_method == 'home_delivery' and form.customer_address.data else ''
        pickup_store = form.pickup_store.data if delivery_method == 'instore_pickup' else ''

        total_amount = 0
        for key, item in session['Shoppingcart'].items():
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 0))
            discount = float(item.get('discount', 0))
            item_total = price * quantity * (1 - discount / 100)
            total_amount += item_total

        # Create order with new Order/OrderItem structure
        invoice = secrets.token_hex(5)
        order = Order(
            invoice=invoice,
            customer_id=current_user.id,
            status="pending",  # Use English status
            payment_status="unpaid" if payment_method == "cod" else "paid",
            shipping_address=customer_address,
            total_amount=total_amount,
            payment_method=payment_method,
            delivery_method=delivery_method,
            pickup_store=pickup_store
        )

        try:
            db.session.add(order)
            db.session.flush()  # Get order ID for OrderItems

            # Create OrderItem objects for each cart item
            for product_id, item in session['Shoppingcart'].items():
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

            db.session.commit()

            # Handle payment method
            if payment_method == 'vnpay':
                # For VNPAY, create a temporary form submission to vnpay_payment
                # We need to redirect to a page that will auto-submit the form
                session['vnpay_pending_order'] = invoice
                return render_template('customers/vnpay_redirect.html',
                                     invoice=invoice,
                                     customer_address=customer_address or '',
                                     customer_email=current_user.email,
                                     customer_name=f"{current_user.first_name} {current_user.last_name}",
                                     customer_phone=current_user.phone_number)
            else:
                # COD - Send confirmation email and redirect to payment history
                customer = Customer.query.get(current_user.id)
                if customer and customer.email:
                    send_order_confirmation_email(customer, order)

                # Clear cart
                session.pop('Shoppingcart', None)

                flash('Đơn hàng đã được đặt thành công! Email xác nhận đã được gửi đến địa chỉ email của bạn.', 'success')
                return redirect(url_for('payment_history'))

        except Exception:
            db.session.rollback()
            flash('Có lỗi xảy ra khi đặt hàng. Vui lòng thử lại.', 'danger')

    return render_template('customers/checkout.html', form=form, subtotal=subtotal, discount=discount, total=total)


@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    # Legacy route for backward compatibility
    address = request.form.get('CustomerAddress', '')
    delivery_method = request.form.get('delivery_method', 'home_delivery')
    pickup_store = request.form.get('pickup_store', '')

    if request.method == "POST":
        try:
            # Create new order from session cart
            if 'Shoppingcart' in session and session['Shoppingcart']:
                total_amount = 0
                for key, item in session['Shoppingcart'].items():
                    price = float(item.get('price', 0))
                    quantity = int(item.get('quantity', 0))
                    discount = float(item.get('discount', 0))
                    item_total = price * quantity * (1 - discount / 100)
                    total_amount += item_total

                customer_id = current_user.id
                invoice = secrets.token_hex(5)
                order = Order(
                    invoice=invoice,
                    customer_id=customer_id,
                    status="pending",
                    payment_status="unpaid",
                    shipping_address=address,
                    total_amount=total_amount,
                    payment_method="cod",
                    delivery_method=delivery_method,
                    pickup_store=pickup_store
                )
                db.session.add(order)
                db.session.flush()  # Get order ID

                # Create OrderItem objects
                for product_id, item in session['Shoppingcart'].items():
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

                db.session.commit()

                # Gửi email xác nhận đơn hàng
                customer = Customer.query.get(customer_id)
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

        except Exception:
            flash('Có lỗi xảy ra khi đặt hàng', 'danger')

    return redirect(url_for('payment_history'))


@app.route('/payment_history')
@login_required
def payment_history():
    # Get orders and update old statuses to new ones
    orders = Order.query.filter(Order.customer_id == current_user.id).filter(
        Order.status != None).order_by(Order.id.desc()).all()
    
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
    order = Order.query.filter_by(
        invoice=invoice, 
        customer_id=current_user.id
    ).first()
    
    if not order:
        flash('Không tìm thấy đơn hàng!', 'danger')
        return redirect(url_for('payment_history'))
    
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
    
    # Update old statuses to new ones in memory (for display)
    if order.status == 'Pending':
        order.status = 'Đang xác nhận'
    elif order.status == 'Accepted':
        order.status = 'Đã giao'
    elif order.status == 'Cancelled':
        order.status = 'Hủy đơn'
    
    # Get customer info
    customer = Customer.query.filter_by(id=current_user.id).first()
    
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
    order = Order.query.filter_by(
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
    except Exception:
        db.session.rollback()
        flash('Có lỗi xảy ra khi hủy đơn hàng', 'danger')
    
    return redirect(url_for('order_detail', invoice=invoice))









