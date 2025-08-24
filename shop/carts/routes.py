import secrets
import json
from flask import render_template, session, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from shop import app, db
from shop.models import CustomerOrder, Category, Brand, Addproduct, Register


def brands():
    brands = Brand.query.all()
    return brands


def categories():
    categories = Category.query.order_by(Category.name.desc()).all()
    return categories


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))


@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        color = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        
        if not product:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
            flash('Sản phẩm không tồn tại', 'danger')
            return redirect(request.referrer)
        
        brand = Brand.query.filter_by(id=product.brand_id).first().name
        if request.method == "POST":
            # if product_id in orders
            DictItems = {product_id: {'name': product.name, 'price': float(product.price), 'discount': product.discount,
                                      'color': color, 'quantity': quantity, 'image': product.image_1,
                                      'colors': product.colors, 'brand': brand}}
            if 'Shoppingcart' in session:
                # print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += quantity;
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
            else:
                session['Shoppingcart'] = DictItems
            
            # Calculate cart count
            cart_count = sum(item['quantity'] for item in session['Shoppingcart'].values())
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': f'Sản phẩm {product.name} đã được thêm vào giỏ hàng!',
                    'cart_count': cart_count
                })
            
            flash(f'Sản phẩm {product.name} đã được thêm vào giỏ hàng!', 'success')
            return redirect(request.referrer)

    except Exception as e:
        print("Loi", e)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi thêm sản phẩm'})
        flash('Có lỗi xảy ra khi thêm sản phẩm', 'danger')
        return redirect(request.referrer)


@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return render_template('products/carts.html', empty=True, brands=brands(),
                               categories=categories())
    
    # Calculate totals from session cart
    subtotals = 0
    discounttotal = 0
    for key, product in session['Shoppingcart'].items():
        discounttotal += (product['discount'] / 100) * float(product['price']) * int(product['quantity'])
        subtotals += float(product['price']) * int(product['quantity'])
    
    # Get customer info if authenticated
    customer = None
    if current_user.is_authenticated:
        customer = current_user
    
    return render_template('products/carts.html', 
                         discounttotal=discounttotal, 
                         subtotals=subtotals, 
                         customer=customer,
                         brands=brands(),
                         categories=categories())


@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('getCart'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('getCart'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('getCart'))
    except Exception as e:
        print(e)


@app.route('/cart')
def cart():
    if 'Shoppingcart' not in session:
        return redirect(request.referrer)
    return render_template('cart.html')


@app.route('/vnpay_payment', methods=['POST'])
def vnpay_payment():
    if not current_user.is_authenticated:
        flash('Vui lòng đăng nhập để thanh toán', 'danger')
        return redirect(url_for('customer_login'))
    
    try:
        amount = request.form.get('amount')
        customer_name = request.form.get('CustomerName')
        customer_email = request.form.get('CustomerEmail')
        customer_phone = request.form.get('CustomerPhone')
        customer_address = request.form.get('CustomerAddress')
        
        # Here you would integrate with VNPAY API
        # For now, we'll just create the order and redirect to a success page
        
        # Create order
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        order = CustomerOrder(invoice=invoice, customer_id=customer_id,
                              orders=json.dumps(session['Shoppingcart']),
                              status="Đang xác nhận", address=customer_address)
        db.session.add(order)
        db.session.commit()
        
        # Clear cart
        session.pop('Shoppingcart', None)
        
        flash('Đơn hàng đã được tạo thành công! Vui lòng thanh toán qua VNPAY.', 'success')
        return redirect(url_for('payment_history'))
        
    except Exception as e:
        print("VNPAY Payment Error:", e)
        flash('Có lỗi xảy ra khi xử lý thanh toán VNPAY', 'danger')
        return redirect(url_for('getCart'))
