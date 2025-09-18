import secrets
import json
import hmac
import hashlib
from datetime import datetime
from flask import render_template, session, request, redirect, url_for, flash, jsonify, current_app
from flask_login import current_user
from shop import app, db
from shop.models import Order, OrderItem, Category, Brand, Product, Customer
from shop.email_utils import send_order_confirmation_email


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
        product = Product.query.filter_by(id=product_id).first()
        
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

    except Exception:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi thêm sản phẩm'})
        flash('Có lỗi xảy ra khi thêm sản phẩm', 'danger')
        return redirect(request.referrer)


@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return render_template('products/carts.html', empty=True, brands=brands(),
                               categories=categories())

    subtotals = 0
    discounttotal = 0
    for key, product in session['Shoppingcart'].items():
        discounttotal += (product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
        subtotals += float(product['price']) * int(product['quantity'])

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
        except Exception:
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
    except Exception:
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('getCart'))
    except Exception:
        pass


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

    pending_invoice = session.get('vnpay_pending_order')
    if pending_invoice:
        order = Order.query.filter_by(invoice=pending_invoice, customer_id=current_user.id).first()
        if not order:
            flash('Không tìm thấy đơn hàng!', 'danger')
            return redirect(url_for('payment_history'))

        session.pop('vnpay_pending_order', None)

        customer_address = order.shipping_address or ''
        final_amount = int(order.total_amount)
        invoice = pending_invoice

    else:
        # Legacy method - calculate from cart (for backward compatibility)
        if 'Shoppingcart' not in session or not session['Shoppingcart']:
            flash('Giỏ hàng trống!', 'danger')
            return redirect(url_for('getCart'))

        customer_address = request.form.get('CustomerAddress', '')

        # Calculate total amount from cart
        subtotals = 0
        discounttotal = 0
        for key, product in session['Shoppingcart'].items():
            product_discount = (product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
            discounttotal += product_discount
            product_subtotal = float(product['price']) * int(product['quantity'])
            subtotals += product_subtotal

        # Final amount to pay
        final_amount = int(subtotals - discounttotal)

        # Generate invoice for future order creation (don't create order yet)
        customer_id = current_user.id
        invoice = secrets.token_hex(5)

        # Validate invoice format (should be alphanumeric, max 34 chars for VNPAY)
        if len(invoice) > 34:
            invoice = invoice[:34]

        if not invoice.replace('_', '').replace('-', '').isalnum():
            invoice = ''.join(c for c in invoice if c.isalnum())

        # Create order immediately with "pending" status
        try:
            new_order = Order(
                invoice=invoice,
                customer_id=customer_id,
                status="pending",
                payment_status="paid",  # VNPAY payment is processed
                shipping_address=customer_address,
                total_amount=final_amount,
                payment_method='vnpay'
            )
            db.session.add(new_order)
            db.session.flush()  # Get order ID

            # Create OrderItem objects for VNPAY order
            for product_id, item in session['Shoppingcart'].items():
                product = Product.query.get(int(product_id))
                if product:
                    quantity = int(item.get('quantity', 0))
                    discount = float(item.get('discount', 0))

                    order_item = OrderItem(
                        order_id=new_order.id,
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
                send_order_confirmation_email(customer, new_order)
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra khi tạo đơn hàng: {str(e)}', 'danger')
            return redirect(url_for('getCart'))

        # Store order info for potential manual cart clearing if VNPAY callback fails
        session['last_vnpay_order'] = {
            'invoice': invoice,
            'order_id': new_order.id,
            'timestamp': datetime.now().isoformat()
        }
        session.modified = True

    # Create VNPAY payment for both pending order and legacy cart
    from shop.vnpay_utils import create_vnpay_instance
    vnpay = create_vnpay_instance()

    order_info = f'Thanh toan don hang {invoice}'
    if len(order_info) > 255:
        order_info = order_info[:255]

    if final_amount <= 0 or final_amount > 100000000:
        flash('Số tiền thanh toán không hợp lệ!', 'danger')
        return redirect(url_for('getCart'))

    # Lấy IP address của client
    client_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()

    payment_url = vnpay.create_payment_url(
        order_info=order_info,
        order_id=invoice,
        amount=final_amount,
        ip_addr=client_ip
    )

    # Store order info in session for return processing
    session['pending_order'] = {
        'invoice': invoice,
        'amount': final_amount
    }

    flash('Đang chuyển hướng đến trang thanh toán VNPAY...', 'info')
    return redirect(payment_url)



@app.route('/vnpay_return', methods=['GET', 'POST', 'HEAD'])
def vnpay_return():
    """
    Handle VNPAY return after payment completion
    """
    # Handle empty request for HEAD method
    if request.method == 'HEAD' and not request.args and not request.form:
        flash('Không nhận được phản hồi từ VNPAY. Vui lòng kiểm tra lại sau.', 'warning')
        return redirect(url_for('payment_history'))

    try:
        vnp_response = request.args.to_dict()

        if not vnp_response:
            vnp_response = request.form.to_dict()

        if not vnp_response and request.method == 'HEAD':
            flash('Không nhận được phản hồi từ VNPAY. Vui lòng kiểm tra lại sau.', 'warning')
            return redirect(url_for('payment_history'))

        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)

        if not is_valid:
            current_app.logger.error(f"VNPAY signature validation failed for order {order_id}")
            flash('Có lỗi xảy ra trong quá trình xử lý thanh toán. Vui lòng liên hệ hỗ trợ nếu tiền đã bị trừ.', 'danger')
            return redirect(url_for('payment_history'))

        # Find the order by invoice
        try:
            order = Order.query.filter_by(invoice=order_id).first()
            if not order:
                flash('Không tìm thấy đơn hàng để xử lý!', 'danger')
                return redirect(url_for('payment_history'))
        except Exception:
            flash('Lỗi database khi tìm đơn hàng!', 'danger')
            return redirect(url_for('payment_history'))

        # Check order ownership (allow processing even if user is not logged in, for VNPAY return)
        if current_user.is_authenticated and order and order.customer_id != current_user.id:
            flash('Bạn không có quyền truy cập đơn hàng này!', 'danger')
            return redirect(url_for('payment_history'))

        # Process payment result
        if response_code == '00':
            # Clear shopping cart after successful payment
            session.pop('Shoppingcart', None)
            flash('Thanh toán thành công! Đơn hàng của bạn đã được xác nhận.', 'success')
        else:
            # Update order status to "Thanh toán thất bại"
            try:
                order.status = 'Thanh toán thất bại'
                db.session.commit()
            except Exception:
                db.session.rollback()

            response_desc = vnpay.get_response_description(response_code)
            flash(f'Thanh toán thất bại: {response_desc}. Đơn hàng đã được lưu với trạng thái thất bại.', 'danger')

        # Redirect based on payment result
        if response_code == '00':
            # Payment successful - redirect to order detail
            return redirect(url_for('order_detail', invoice=order_id))
        else:
            # Payment failed - redirect to cart or home
            return redirect(url_for('getCart'))

    except Exception:
        flash('Có lỗi xảy ra khi xử lý kết quả thanh toán', 'danger')
        return redirect(url_for('payment_history'))


@app.route('/vnpay_ipn', methods=['POST', 'HEAD'])
def vnpay_ipn():
    """
    Handle VNPAY Instant Payment Notification (IPN)
    This endpoint is called by VNPAY server to notify payment status
    """
    if request.method == 'HEAD':
        return '', 200

    try:
        vnp_response = request.form.to_dict()

        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)

        if not is_valid:
            return 'INVALID_SIGNATURE', 400

        order = Order.query.filter_by(invoice=order_id).first()
        if not order:
            if response_code == '00':
                return 'ORDER_NOT_FOUND', 404
            else:
                return jsonify({'RspCode': '00', 'Message': 'Confirm Success - No order created for failed payment'})

        vnp_amount = int(vnp_response.get('vnp_Amount', 0)) / 100
        vnp_txn_ref = vnp_response.get('vnp_TxnRef', '')
        vnp_transaction_no = vnp_response.get('vnp_TransactionNo', '')
        vnp_bank_code = vnp_response.get('vnp_BankCode', '')
        vnp_pay_date = vnp_response.get('vnp_PayDate', '')

        if response_code == '00':
            # Payment was already marked as successful when order was created
            return jsonify({'RspCode': '00', 'Message': 'Confirm Success'})
        else:
            # Payment failed - update payment status
            if order.payment_status == 'Đã thanh toán':
                order.payment_status = 'Thanh toán thất bại'
                db.session.commit()

            response_desc = vnpay.get_response_description(response_code)
            # Return success response to VNPAY (to acknowledge receipt)
            return jsonify({
                'RspCode': '00',
                'Message': 'Confirm Success'
            })

    except Exception:
        return 'INTERNAL_ERROR', 500






