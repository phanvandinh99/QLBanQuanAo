import secrets
import json
import hmac
import hashlib
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
    print("=" * 50)
    print("VNPAY PAYMENT INITIATION - START")
    print("=" * 50)

    if not current_user.is_authenticated:
        print("ERROR: User not authenticated")
        flash('Vui lòng đăng nhập để thanh toán', 'danger')
        return redirect(url_for('customer_login'))

    # Check if cart is empty
    if 'Shoppingcart' not in session or not session['Shoppingcart']:
        flash('Giỏ hàng trống!', 'danger')
        return redirect(url_for('getCart'))

    try:
        customer_address = request.form.get('CustomerAddress', '')

        # Calculate total amount from cart
        subtotals = 0
        discounttotal = 0
        for key, product in session['Shoppingcart'].items():
            product_discount = (product['discount'] / 100) * float(product['price']) * int(product['quantity'])
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

        # Store order info in session for creation after successful payment
        session['pending_order_data'] = {
            'invoice': invoice,
            'customer_id': customer_id,
            'orders': json.dumps(session['Shoppingcart']),
            'address': customer_address,
            'amount': final_amount,
            'subtotals': subtotals,
            'discounttotal': discounttotal
        }

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
        print(f"Session pending_order stored: {session['pending_order']}")

        flash('Đang chuyển hướng đến trang thanh toán VNPAY...', 'info')
        print("=" * 50)
        print("VNPAY PAYMENT INITIATION - SUCCESS")
        print("=" * 50)
        return redirect(payment_url)

    except Exception as e:
        print("=" * 50)
        print("VNPAY PAYMENT INITIATION - ERROR")
        print("=" * 50)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 50)

        db.session.rollback()
        flash('Có lỗi xảy ra khi xử lý thanh toán VNPAY', 'danger')
        return redirect(url_for('getCart'))


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
            flash('Chữ ký không hợp lệ!', 'danger')
            return redirect(url_for('payment_history'))

        # Check if we have pending order data in session (for successful payments)
        # or try to find existing order (for failed payments that might have been created)
        order = None
        pending_order_data = None

        if 'pending_order_data' in session and session['pending_order_data']['invoice'] == order_id:
            pending_order_data = session['pending_order_data']
            print(f"Found pending order data in session for invoice: {order_id}")
        else:
            # Try to find existing order (for backward compatibility or failed payments)
            order = CustomerOrder.query.filter_by(invoice=order_id).first()
            if order:
                print(f"Found existing order: ID={order.id}, Status={order.status}, Customer={order.customer_id}")
            else:
                print(f"No order found for invoice: {order_id}")

        # Check if order belongs to current user (if logged in and order exists)
        if order and current_user.is_authenticated:
            if order.customer_id != current_user.id:
                print(f"ERROR: Order {order_id} belongs to customer {order.customer_id}, but current user is {current_user.id}")
                flash('Bạn không có quyền truy cập đơn hàng này!', 'danger')
                return redirect(url_for('payment_history'))

        # Process payment result
        print(f"Processing payment result with response_code: {response_code}")
        if response_code == '00':
            print("PAYMENT SUCCESSFUL - Creating order and updating status")

            # Payment successful - create order from pending data
            if pending_order_data:
                # Create new order from pending data
                new_order = CustomerOrder(
                    invoice=pending_order_data['invoice'],
                    customer_id=pending_order_data['customer_id'],
                    orders=pending_order_data['orders'],
                    status="Đã thanh toán",
                    address=pending_order_data['address']
                )
                db.session.add(new_order)
                db.session.commit()
                order = new_order
                print(f"New order created successfully with ID: {new_order.id}, Invoice: {new_order.invoice}")
            elif order:
                # Update existing order status
                order.status = 'Đã thanh toán'
                db.session.commit()
                print(f"Existing order {order_id} status updated to 'Đã thanh toán'")
            else:
                print("ERROR: No order data found for successful payment!")
                flash('Có lỗi xảy ra khi xử lý đơn hàng!', 'danger')
                return redirect(url_for('payment_history'))

            # Clear cart if payment was successful
            if 'Shoppingcart' in session:
                print("Clearing shopping cart from session")
                session.pop('Shoppingcart', None)

            # Clear pending order data
            if 'pending_order_data' in session:
                print("Clearing pending order data from session")
                session.pop('pending_order_data', None)

            flash('Thanh toán thành công! Đơn hàng của bạn đã được xác nhận.', 'success')
            print("Redirecting to order detail page")

        else:
            print(f"PAYMENT FAILED - Response code: {response_code}")
            # Payment failed - DO NOT create order, keep cart for retry

            # DON'T clear cart on payment failure - keep it for user to retry
            print("Keeping shopping cart for user to retry payment")

            # Clear pending order data (don't create the order)
            if 'pending_order_data' in session:
                print("Removing pending order data - order not created due to payment failure")
                session.pop('pending_order_data', None)

            response_desc = vnpay.get_response_description(response_code)
            print(f"Response description: {response_desc}")
            flash(f'Thanh toán thất bại: {response_desc}. Bạn có thể thử thanh toán lại.', 'danger')

        print("=" * 50)
        print("VNPAY RETURN PROCESSING - SUCCESS")
        print("=" * 50)

        # Redirect based on payment result
        if response_code == '00':
            # Payment successful - redirect to order detail
            return redirect(url_for('order_detail', invoice=order_id))
        else:
            # Payment failed - redirect to cart or home
            return redirect(url_for('getCart'))

    except Exception as e:
        print("=" * 50)
        print("VNPAY RETURN PROCESSING - ERROR")
        print("=" * 50)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 50)

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

        order = CustomerOrder.query.filter_by(invoice=order_id).first()
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
            # Payment successful
            if order.status != 'Đã thanh toán':
                order.status = 'Đã thanh toán'
                db.session.commit()

            return jsonify({'RspCode': '00', 'Message': 'Confirm Success'})
        else:
            if order.status == 'Chờ thanh toán':
                order.status = 'Thanh toán thất bại'
                db.session.commit()

            response_desc = vnpay.get_response_description(response_code)
            # Return success response to VNPAY (to acknowledge receipt)
            return jsonify({
                'RspCode': '00',
                'Message': 'Confirm Success'
            })

    except Exception as e:
        print("=" * 50)
        print("VNPAY IPN PROCESSING - ERROR")
        print("=" * 50)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 50)
        return 'INTERNAL_ERROR', 500


@app.route('/debug_vnpay', methods=['GET'])
def debug_vnpay():
    """
    Debug endpoint for VNPAY integration
    """
    print("=" * 50)
    print("VNPAY DEBUG ENDPOINT CALLED")
    print("=" * 50)

    try:
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        # Test URL creation
        test_order_id = "DEBUG_" + secrets.token_hex(4)
        test_amount = 100000  # 100,000 VND
        test_order_info = "Test order for debugging"

        print(f"Creating test payment URL with order_id={test_order_id}, amount={test_amount}")

        payment_url = vnpay.create_payment_url(
            order_info=test_order_info,
            order_id=test_order_id,
            amount=test_amount
        )

        # Test hash validation with a mock response
        mock_response = {
            'vnp_ResponseCode': '00',
            'vnp_TxnRef': test_order_id,
            'vnp_Amount': str(test_amount * 100),
            'vnp_OrderInfo': test_order_info,
            'vnp_BankCode': 'NCB',
            'vnp_PayDate': '20241209112433',
            'vnp_TransactionNo': '14000001'
        }

        # Create hash for mock response
        mock_params = sorted(mock_response.items())
        mock_hash_data = '&'.join([f"{key}={str(value)}" for key, value in mock_params])
        mock_secure_hash = hmac.new(
            vnpay.hash_secret.encode('utf-8'),
            mock_hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        mock_response['vnp_SecureHash'] = mock_secure_hash

        print("Testing hash validation with mock response...")
        is_valid, response_code, order_id = vnpay.validate_response(mock_response)

        # Get current configuration
        config_info = {
            'VNPAY_URL': vnpay.vnpay_url,
            'VNPAY_TMN_CODE': vnpay.tmn_code,
            'VNPAY_RETURN_URL': vnpay.return_url,
            'VNPAY_IPN_URL': vnpay.ipn_url,
            'HASH_SECRET_LENGTH': len(vnpay.hash_secret)
        }

        debug_info = {
            'config': config_info,
            'test_payment_url': payment_url,
            'test_order_id': test_order_id,
            'test_amount': test_amount,
            'mock_validation_result': {
                'is_valid': is_valid,
                'response_code': response_code,
                'order_id': order_id
            },
            'mock_response': mock_response,
            'current_user': {
                'is_authenticated': current_user.is_authenticated,
                'id': current_user.id if current_user.is_authenticated else None
            }
        }

        print("=" * 50)
        print("DEBUG INFO GENERATED SUCCESSFULLY")
        print("=" * 50)

        return jsonify(debug_info)

    except Exception as e:
        print("=" * 50)
        print("DEBUG ENDPOINT ERROR")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 50)

        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
