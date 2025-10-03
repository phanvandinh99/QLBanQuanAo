import secrets
import json
import hmac
import hashlib
from datetime import datetime
from flask import render_template, session, request, redirect, url_for, flash, jsonify, current_app
from flask_login import current_user, login_required
from shop import app, db
from shop.models import Order, OrderItem, Category, Brand, Product, Customer
from shop.utils.response_utils import ajax_response, is_ajax_request, success_response, error_response
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
            error_msg = 'Sản phẩm không tồn tại'
            if is_ajax_request():
                return error_response(error_msg)
            flash(error_msg, 'danger')
            return redirect(request.referrer)
        
        # Check current quantity in cart
        current_cart_quantity = 0
        if 'Shoppingcart' in session and product_id in session['Shoppingcart']:
            current_cart_quantity = session['Shoppingcart'][product_id]['quantity']
        
        # Check if total quantity (cart + new) exceeds stock
        total_requested_quantity = current_cart_quantity + quantity
        if total_requested_quantity > product.total_stock:
            error_msg = f'Số lượng sản phẩm trong kho không đáp ứng (còn lại: {product.total_stock})'
            if is_ajax_request():
                return error_response(error_msg)
            flash(error_msg, 'danger')
            return redirect(request.referrer)
        
        brand = Brand.query.filter_by(id=product.brand_id).first().name
        if request.method == "POST":
            # if product_id in orders
            DictItems = {product_id: {'name': product.name, 'price': float(product.current_price), 'discount': product.discount,
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
            
            success_msg = f'🛒 Sản phẩm {product.name} đã được thêm vào giỏ hàng!'
            if is_ajax_request():
                return success_response(success_msg, data={'cart_count': cart_count})
            
            flash(success_msg, 'success')
            return redirect(request.referrer)

    except Exception as e:
        error_msg = 'Có lỗi xảy ra khi thêm sản phẩm'
        if is_ajax_request():
            return error_response(error_msg)
        flash(error_msg, 'danger')
        return redirect(request.referrer)


@app.route('/carts')
def getCart():
    # Check if user has successful VNPay orders and clear cart if needed
    if current_user.is_authenticated:
        from shop.models import Order
        from datetime import datetime, timedelta

        # Check for successful VNPay orders in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_vnpay_orders = Order.query.filter(
            Order.customer_id == current_user.id,
            Order.payment_method == 'vnpay',
            Order.status.in_(['Đang xác nhận', 'Đang xử lý', 'Đang giao hàng', 'Đã giao']),
            Order.created_at >= one_hour_ago
        ).all()

        if recent_vnpay_orders and 'Shoppingcart' in session:
            current_app.logger.info(f"Clearing cart for user {current_user.id} due to recent successful VNPay orders: {[o.invoice for o in recent_vnpay_orders]}")
            session.pop('Shoppingcart', None)
            session.modified = True

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
        quantity = int(request.form.get('quantity'))
        color = request.form.get('color')
        
        # Check stock availability
        product = Product.query.get(code)
        if product and quantity > product.total_stock:
            flash('Số lượng sản phẩm trong kho không đáp ứng', 'danger')
            return redirect(url_for('getCart'))
        
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


@app.route('/api/cart-count')
def get_cart_count():
    """API endpoint to get current cart count"""
    try:
        if 'Shoppingcart' in session and session['Shoppingcart']:
            cart_count = sum(item['quantity'] for item in session['Shoppingcart'].values())
        else:
            cart_count = 0
        
        return jsonify({
            'success': True,
            'cart_count': cart_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'cart_count': 0,
            'error': str(e)
        })


@app.route('/cart')
def cart():
    # Check if user has successful VNPay orders and clear cart if needed
    if current_user.is_authenticated:
        from shop.models import Order
        from datetime import datetime, timedelta

        # Check for successful VNPay orders in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_vnpay_orders = Order.query.filter(
            Order.customer_id == current_user.id,
            Order.payment_method == 'vnpay',
            Order.status.in_(['Đang xác nhận', 'Đang xử lý', 'Đang giao hàng', 'Đã giao']),
            Order.created_at >= one_hour_ago
        ).all()

        if recent_vnpay_orders and 'Shoppingcart' in session:
            current_app.logger.info(f"Clearing cart for user {current_user.id} due to recent successful VNPay orders (cart route): {[o.invoice for o in recent_vnpay_orders]}")
            session.pop('Shoppingcart', None)
            session.modified = True

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
                        unit_price=product.current_price,
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
        current_app.logger.error(f"Invalid payment amount: {final_amount} for invoice {invoice}")
        flash('Số tiền thanh toán không hợp lệ!', 'danger')
        return redirect(url_for('getCart'))

    # Lấy IP address của client
    client_ip = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    current_app.logger.info(f"Creating VNPAY payment for invoice {invoice}, amount {final_amount}, client_ip {client_ip}")

    payment_url = vnpay.create_payment_url(
        order_info=order_info,
        order_id=invoice,
        amount=final_amount,
        ip_addr=client_ip
    )

    current_app.logger.info(f"VNPAY payment URL created for invoice {invoice}: {payment_url[:100]}...")

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
        current_app.logger.warning("VNPAY return: Empty HEAD request received")
        flash('Không nhận được phản hồi từ VNPAY. Vui lòng kiểm tra lại sau.', 'warning')
        return redirect(url_for('payment_history'))

    current_app.logger.info(f"VNPAY return: User authenticated: {current_user.is_authenticated}, Session keys: {list(session.keys())}, Cart in session: {'Shoppingcart' in session}")

    try:
        vnp_response = request.args.to_dict()

        if not vnp_response:
            vnp_response = request.form.to_dict()

        if not vnp_response and request.method == 'HEAD':
            current_app.logger.warning("VNPAY return: No response data in HEAD request")
            flash('Không nhận được phản hồi từ VNPAY. Vui lòng kiểm tra lại sau.', 'warning')
            return redirect(url_for('payment_history'))

        # Log all VNPAY response parameters for debugging
        current_app.logger.info(f"VNPAY return received. Method: {request.method}, Response keys: {list(vnp_response.keys())}")
        for key, value in vnp_response.items():
            current_app.logger.debug(f"VNPAY param {key}: {value}")

        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)

        current_app.logger.info(f"VNPAY validation result: valid={is_valid}, response_code={response_code}, order_id={order_id}")

        if not is_valid:
            current_app.logger.error(f"VNPAY signature validation failed for order {order_id}")
            current_app.logger.error(f"VNPAY response details: {vnp_response}")
            # Do not trust response_code when signature validation fails
            # It could be tampered with or corrupted during transmission

            # Special warning if response_code suggests success but signature fails
            if response_code == '00':
                current_app.logger.critical(f"CRITICAL: VNPAY signature validation failed but response_code='00' (success) for order {order_id}. Potential security issue!")
                flash('Có lỗi bảo mật nghiêm trọng trong quá trình xử lý thanh toán. Vui lòng liên hệ hỗ trợ ngay lập tức!', 'danger')
            else:
                current_app.logger.error(f"VNPAY signature validation failed - not trusting response_code: {response_code}")
                flash('Có lỗi xảy ra trong quá trình xử lý thanh toán (signature validation failed). Vui lòng liên hệ hỗ trợ nếu tiền đã bị trừ.', 'danger')

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
            current_app.logger.warning(f"VNPAY return: Order ownership check failed - user {current_user.id} vs order customer {order.customer_id}")
            flash('Bạn không có quyền truy cập đơn hàng này!', 'danger')
            return redirect(url_for('payment_history'))

        # Process payment result
        if response_code == '00':
            # Clear shopping cart after successful payment
            cart_existed = 'Shoppingcart' in session
            session.pop('Shoppingcart', None)
            cart_cleared = 'Shoppingcart' not in session

            current_app.logger.info(f"VNPAY payment successful for order {order_id}, cart existed: {cart_existed}, cart cleared: {cart_cleared}, user authenticated: {current_user.is_authenticated}")

            if cart_existed and not cart_cleared:
                current_app.logger.error(f"VNPAY payment successful but failed to clear cart for order {order_id}")

            flash('Thanh toán thành công! Đơn hàng của bạn đã được xác nhận.', 'success')
        else:
            # Update order status to "Thanh toán thất bại"
            try:
                old_status = order.status
                order.status = 'Thanh toán thất bại'
                db.session.commit()
                current_app.logger.info(f"VNPAY payment failed for order {order_id}. Changed status from '{old_status}' to 'Thanh toán thất bại'")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to update order status for failed VNPAY payment {order_id}: {str(e)}")

            response_desc = vnpay.get_response_description(response_code)
            current_app.logger.warning(f"VNPAY payment failed for order {order_id}: {response_code} - {response_desc}")
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

        # Log IPN request for debugging
        current_app.logger.info(f"VNPAY IPN received. Response keys: {list(vnp_response.keys())}")
        for key, value in vnp_response.items():
            current_app.logger.debug(f"VNPAY IPN param {key}: {value}")

        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)

        current_app.logger.info(f"VNPAY IPN validation result: valid={is_valid}, response_code={response_code}, order_id={order_id}")

        if not is_valid:
            current_app.logger.error(f"VNPAY IPN signature validation failed for order {order_id}")
            current_app.logger.error(f"VNPAY IPN response details: {vnp_response}")
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

        current_app.logger.info(f"VNPAY IPN processing order {order_id}: amount={vnp_amount}, txn_ref={vnp_txn_ref}, txn_no={vnp_transaction_no}, bank={vnp_bank_code}")

        if response_code == '00':
            # Payment was already marked as successful when order was created
            current_app.logger.info(f"VNPAY IPN: Payment confirmed successful for order {order_id}")
            return jsonify({'RspCode': '00', 'Message': 'Confirm Success'})
        else:
            # Payment failed - update payment status
            old_payment_status = order.payment_status
            if order.payment_status == 'paid':
                order.payment_status = 'failed'
                db.session.commit()
                current_app.logger.warning(f"VNPAY IPN: Updated payment status from '{old_payment_status}' to 'failed' for order {order_id}")

            response_desc = vnpay.get_response_description(response_code)
            current_app.logger.warning(f"VNPAY IPN: Payment failed for order {order_id} - {response_code}: {response_desc}")
            # Return success response to VNPAY (to acknowledge receipt)
            return jsonify({
                'RspCode': '00',
                'Message': 'Confirm Success'
            })

    except Exception as e:
        current_app.logger.error(f"VNPAY IPN processing error: {str(e)}")
        return 'INTERNAL_ERROR', 500


@app.route('/vnpay_debug', methods=['GET'])
@login_required
def vnpay_debug():
    """
    Debug endpoint to check VNPay configuration and test validation
    Only accessible to admin users
    """
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('customer_login'))

    try:
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        # Test VNPay configuration
        config_info = {
            'vnpay_url': current_app.config.get('VNPAY_URL', 'Not configured'),
            'tmn_code': current_app.config.get('VNPAY_TMN_CODE', 'Not configured'),
            'hash_secret_configured': bool(current_app.config.get('VNPAY_HASH_SECRET')),
            'return_url': current_app.config.get('VNPAY_RETURN_URL', 'Not configured'),
            'ipn_url': current_app.config.get('VNPAY_IPN_URL', 'Not configured')
        }

        # Test payment URL generation
        test_payment_url = None
        test_validation = None
        try:
            test_payment_url = vnpay.create_payment_url(
                order_info="Test payment",
                order_id="DEBUG123",
                amount=10000,
                ip_addr="127.0.0.1"
            )

            # Test validation with a mock response
            mock_response = {
                'vnp_TmnCode': vnpay.tmn_code,
                'vnp_Amount': '1000000',
                'vnp_BankCode': 'NCB',
                'vnp_BankTranNo': '20170829152730',
                'vnp_CardType': 'ATM',
                'vnp_OrderInfo': 'Test payment',
                'vnp_PayDate': '20170829153052',
                'vnp_ResponseCode': '00',
                'vnp_TxnRef': 'DEBUG123',
                'vnp_TransactionNo': '20170829153052',
                'vnp_TransactionStatus': '00'
            }

            # Calculate expected hash for mock response
            params_for_hash = {k: v for k, v in mock_response.items()}
            sorted_params = sorted(params_for_hash.items(), key=lambda x: x[0])
            hash_parts = [f"{key}={value}" for key, value in sorted_params]
            hash_data = '&'.join(hash_parts)

            expected_hash = hmac.new(
                vnpay.hash_secret.encode('utf-8'),
                hash_data.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()

            mock_response['vnp_SecureHash'] = expected_hash
            test_validation = vnpay.validate_response(mock_response)

        except Exception as e:
            test_validation = f"Error: {str(e)}"

        return render_template('admin/vnpay_debug.html',
                             config_info=config_info,
                             test_payment_url=test_payment_url,
                             test_validation=test_validation)

    except Exception as e:
        current_app.logger.error(f"VNPay debug error: {str(e)}")
        flash(f'Lỗi khi kiểm tra VNPay: {str(e)}', 'danger')
        return redirect(url_for('admin'))






