from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, bcrypt
from shop.models import Register, Admin, CustomerOrder
from .forms import CustomerRegisterForm, CustomerLoginFrom
from shop.models import Category, Brand, Addproduct
from shop.carts.routes import clearcart, MagerDicts
from flask import Markup
import secrets
import os
from datetime import datetime
import json

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
        flash(f'Information change complete!', 'success')
        db.session.commit()
        return redirect(url_for('update_account'))
    return render_template('customers/myaccount.html', detail_customer=detail_customer, brands=brands(),
                           categories=categories())


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    detail_password_customer = Register.query.get_or_404(current_user.id)
    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if request.method == "POST":
        if not bcrypt.check_password_hash(detail_password_customer.password, old_password.encode('utf8')):
            flash(f'Old passwords do not match!', 'danger')
            return redirect(url_for('change_password'))

        detail_password_customer.password = bcrypt.generate_password_hash(new_password).decode('utf8')
        flash(f'Change Password Complete!', 'success')
        db.session.commit()
        return redirect(url_for('change_password'))
    return render_template('customers/myaccount.html', detail_password_customer=detail_password_customer,
                           brands=brands(),
                           categories=categories())


@app.route('/register', methods=['GET', 'POST'])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = CustomerRegisterForm()
    print(f"[REGISTER DEBUG] Form created, request method: {request.method}")
    
    if request.method == 'POST':
        print(f"[REGISTER DEBUG] POST request received")
        print(f"[REGISTER DEBUG] Form data: {request.form}")
        print(f"[REGISTER DEBUG] Form errors: {form.errors}")
    
    if form.validate_on_submit():
        print(f"[REGISTER DEBUG] Form validation passed")
        if Admin.query.filter_by(email=form.email.data).first():
            flash(f'Email Used!', 'danger')
            return redirect(url_for('customer_register'))
        if Register.query.filter_by(email=form.email.data).first():
            flash(f'Email Used!', 'danger')
            return redirect(url_for('customer_register'))
        if Register.query.filter_by(phone_number=form.phone_number.data).first():
            flash(f'Phone Number Used!', 'danger')
            return redirect(url_for('customer_register'))
        try:
            print(f"[REGISTER DEBUG] Starting registration process for email: {form.email.data}")
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
            print(f"[REGISTER DEBUG] Password hashed successfully")
            
            register = Register(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                                last_name=form.last_name.data, phone_number=form.phone_number.data,
                                gender=form.gender.data,
                                password=hash_password, date_created=datetime.utcnow(), lock=False)
            print(f"[REGISTER DEBUG] Register object created successfully")
            
            db.session.add(register)
            print(f"[REGISTER DEBUG] Added to session successfully")
            
            db.session.commit()
            print(f"[REGISTER DEBUG] Committed to database successfully")
            
            flash(f'Welcome {form.first_name.data} {form.last_name.data} Thank you for registering', 'success')
        except Exception as e:
            print(f"[REGISTER ERROR] Registration failed: {str(e)}")
            print(f"[REGISTER ERROR] Exception type: {type(e).__name__}")
            import traceback
            print(f"[REGISTER ERROR] Full traceback: {traceback.format_exc()}")
            db.session.rollback()
            flash(f'Registration Error: {str(e)}', 'danger')
            return redirect(url_for('customer_register'))

        return redirect(url_for('customer_login'))
    else:
        if request.method == 'POST':
            print(f"[REGISTER DEBUG] Form validation failed")
            print(f"[REGISTER DEBUG] Form errors: {form.errors}")
    
    return render_template('customers/register.html', form=form, brands=brands(), categories=categories())

@app.route('/debug_register')
def debug_register():
    """Debug route to check registration form"""
    try:
        print("=== DEBUG REGISTER ROUTE ===")
        
        # Test database connection
        from shop.models import Register, Admin
        register_count = Register.query.count()
        admin_count = Admin.query.count()
        print(f"Current users in database: {register_count}")
        print(f"Current admins in database: {admin_count}")
        
        # Test form creation
        from .forms import CustomerRegisterForm
        form = CustomerRegisterForm()
        print(f"Form created successfully: {type(form)}")
        
        # Test model creation (without saving)
        from datetime import datetime
        test_register = Register(
            username='test_debug',
            email='debug@test.com',
            first_name='Debug',
            last_name='Test',
            phone_number='0987654321',
            gender='Male',
            password='hashed_password',
            date_created=datetime.utcnow(),
            lock=False
        )
        print(f"Test register object created: {test_register.username}")
        
        return f"""
        <h2>Debug Registration</h2>
        <p>Database connection: OK</p>
        <p>Current users: {register_count}</p>
        <p>Current admins: {admin_count}</p>
        <p>Form creation: OK</p>
        <p>Model creation: OK</p>
        <p>Check terminal for detailed logs</p>
        <a href="/register">Go to Registration</a>
        """
        
    except Exception as e:
        print(f"[DEBUG ERROR] {str(e)}")
        import traceback
        print(f"[DEBUG ERROR] Full traceback: {traceback.format_exc()}")
        return f"Error: {str(e)}"

@app.route('/test_form')
def test_form():
    """Test form creation and validation"""
    try:
        from .forms import CustomerRegisterForm
        form = CustomerRegisterForm()
        
        html = f"""
        <h2>Test Form Fields</h2>
        <p>Form created: {type(form)}</p>
        <ul>
            <li>Username field: {hasattr(form, 'username')}</li>
            <li>First name field: {hasattr(form, 'first_name')}</li>
            <li>Last name field: {hasattr(form, 'last_name')}</li>
            <li>Email field: {hasattr(form, 'email')}</li>
            <li>Phone number field: {hasattr(form, 'phone_number')}</li>
            <li>Gender field: {hasattr(form, 'gender')}</li>
            <li>Password field: {hasattr(form, 'password')}</li>
            <li>Confirm field: {hasattr(form, 'confirm')}</li>
            <li>Submit field: {hasattr(form, 'submit')}</li>
        </ul>
        <a href="/register">Go to Registration</a>
        """
        
        return html
        
    except Exception as e:
        return f"Form test error: {str(e)}"


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
                # Get all product IDs from existing orders
                existing_product_ids = []
                for order in orders:
                    if order.orders:
                        try:
                            order_data = json.loads(order.orders)
                            existing_product_ids.extend(order_data.keys())
                        except:
                            pass
                
                for key, item in session['Shoppingcart'].items():
                    if key not in existing_product_ids:
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
        flash('Incorrect email and password', 'danger')
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
        flash('Incorrect email and password', 'danger')
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
    
    customer_id = current_user.id
    customer = Register.query.filter_by(id=customer_id).first()
    
    # Get all pending orders for this customer
    orders = CustomerOrder.query.filter(
        CustomerOrder.customer_id == current_user.id
    ).filter(
        CustomerOrder.status == None
    ).order_by(CustomerOrder.id.desc()).all()
    
    # Calculate totals from session cart
    subtotals = 0
    discounttotal = 0
    if 'Shoppingcart' in session:
        for key, product in session['Shoppingcart'].items():
            discounttotal += float(product['discount'] / 100) * float(product['price']) * int(product['quantity'])
            subtotals += float(product['price']) * int(product['quantity'])
        subtotals -= discounttotal
    
    return render_template('customers/order.html', 
                         invoices=[order.invoice for order in orders], 
                         subtotals=subtotals, 
                         customer=customer,
                         orders=orders, 
                         brands=brands(), 
                         categories=categories(), 
                         get_order_data=get_order_data)


@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    address = request.form.get('CustomerAddress')
    invoice_customer = request.form.get('invoice_customer')
    if request.method == "POST":
        for invoice in invoice_customer.split(','):
            customer_order = CustomerOrder.query.filter_by(invoice=invoice).first()
            detail_order = CustomerOrder.query.get_or_404(customer_order.id)
            detail_order.status = "Pending"
            detail_order.address = address
            db.session.commit()
        clearcart()
    return redirect(url_for('payment_history'))


@app.route('/payment_history')
@login_required
def payment_history():
    orders = CustomerOrder.query.filter(CustomerOrder.customer_id == current_user.id).filter(
        CustomerOrder.status != None).order_by(CustomerOrder.id.desc()).all()
    return render_template('customers/myaccount.html', orders=orders, brands=brands(), categories=categories(), get_order_data=get_order_data)

def get_order_data(order):
    """Helper function to parse order data from JSON"""
    if order.orders:
        try:
            return json.loads(order.orders)
        except:
            return {}
    return {}
