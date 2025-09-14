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
        print("ERROR: Shopping cart is empty")
        flash('Giỏ hàng trống!', 'danger')
        return redirect(url_for('getCart'))

    try:
        # Get form data
        customer_address = request.form.get('CustomerAddress', '')
        print(f"Customer Address: {customer_address}")
        print(f"User ID: {current_user.id}")
        print(f"Cart contents: {session['Shoppingcart']}")

        # Calculate total amount from cart
        subtotals = 0
        discounttotal = 0
        for key, product in session['Shoppingcart'].items():
            product_discount = (product['discount'] / 100) * float(product['price']) * int(product['quantity'])
            discounttotal += product_discount
            product_subtotal = float(product['price']) * int(product['quantity'])
            subtotals += product_subtotal
            print(f"Product {key}: price={product['price']}, quantity={product['quantity']}, discount={product['discount']}%, product_subtotal={product_subtotal}, product_discount={product_discount}")

        # Final amount to pay
        final_amount = int(subtotals - discounttotal)
        print(f"Calculated totals - Subtotals: {subtotals}, Discount: {discounttotal}, Final Amount: {final_amount}")

        # Create order first with pending status
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        print(f"Generated invoice: {invoice}")

        # Validate invoice format (should be alphanumeric, max 34 chars for VNPAY)
        if len(invoice) > 34:
            invoice = invoice[:34]
            print(f"Invoice truncated to 34 chars: {invoice}")

        if not invoice.replace('_', '').replace('-', '').isalnum():
            invoice = ''.join(c for c in invoice if c.isalnum())
            print(f"Invoice cleaned to alphanumeric: {invoice}")

        order = CustomerOrder(
            invoice=invoice,
            customer_id=customer_id,
            orders=json.dumps(session['Shoppingcart']),
            status="Chờ thanh toán",
            address=customer_address
        )
        db.session.add(order)
        db.session.commit()
        print(f"Order created successfully with ID: {order.id}")

        # Import VNPAY utility
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()
        print("VNPAY instance created")

        # Create payment URL
        order_info = f'Thanh toan don hang {invoice}'
        print(f"Order info: {order_info}")
        print(f"Payment amount: {final_amount}")

        # Validate order_info length (VNPAY limit is typically 255 chars)
        if len(order_info) > 255:
            order_info = order_info[:255]
            print(f"Order info truncated to 255 chars: {order_info}")

        # Validate amount before creating URL
        if final_amount <= 0:
            print("ERROR: Payment amount is 0 or negative!")
            flash('Số tiền thanh toán không hợp lệ!', 'danger')
            return redirect(url_for('getCart'))

        if final_amount > 100000000:  # 1 billion VND limit
            print(f"ERROR: Payment amount too large: {final_amount}")
            flash('Số tiền thanh toán quá lớn!', 'danger')
            return redirect(url_for('getCart'))

        print(f"Amount validation passed: {final_amount}")

        # Test if return and IPN URLs are accessible
        try:
            import requests
            return_url_response = requests.head(vnpay.return_url, timeout=5)
            ipn_url_response = requests.head(vnpay.ipn_url, timeout=5)
            print(f"Return URL accessibility: {return_url_response.status_code}")
            print(f"IPN URL accessibility: {ipn_url_response.status_code}")
        except Exception as e:
            print(f"WARNING: Could not test URL accessibility: {e}")
            print("This might cause VNPAY error code 99")

        payment_url = vnpay.create_payment_url(
            order_info=order_info,
            order_id=invoice,
            amount=final_amount
        )

        print(f"VNPAY Payment URL generated: {payment_url}")

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


@app.route('/vnpay_return', methods=['GET'])
def vnpay_return():
    """
    Handle VNPAY return after payment completion
    """
    print("=" * 50)
    print("VNPAY RETURN PROCESSING - START")
    print("=" * 50)

    try:
        # Get all VNPAY response parameters
        vnp_response = request.args.to_dict()
        print(f"Full VNPAY response parameters: {vnp_response}")

        # Log individual important parameters
        print(f"vnp_ResponseCode: {vnp_response.get('vnp_ResponseCode', 'NOT_FOUND')}")
        print(f"vnp_TxnRef: {vnp_response.get('vnp_TxnRef', 'NOT_FOUND')}")
        print(f"vnp_Amount: {vnp_response.get('vnp_Amount', 'NOT_FOUND')}")
        print(f"vnp_OrderInfo: {vnp_response.get('vnp_OrderInfo', 'NOT_FOUND')}")
        print(f"vnp_BankCode: {vnp_response.get('vnp_BankCode', 'NOT_FOUND')}")
        print(f"vnp_SecureHash: {vnp_response.get('vnp_SecureHash', 'NOT_FOUND')}")

        # Import VNPAY utility and validate response
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()
        print("VNPAY instance created for validation")

        # Validate response
        print("Starting response validation...")
        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)
        print(f"Validation result: is_valid={is_valid}, response_code={response_code}, order_id={order_id}")

        if not is_valid:
            print("ERROR: Invalid VNPAY signature")
            print("This could be due to:")
            print("1. Wrong VNPAY_HASH_SECRET in configuration")
            print("2. Response tampered with")
            print("3. Network issues during transmission")
            flash('Chữ ký không hợp lệ!', 'danger')
            return redirect(url_for('payment_history'))

        # Get order information
        print(f"Looking for order with invoice: {order_id}")
        order = CustomerOrder.query.filter_by(invoice=order_id).first()
        if not order:
            print(f"ERROR: Order not found with invoice: {order_id}")
            print("Available orders in database:")
            all_orders = CustomerOrder.query.limit(10).all()
            for o in all_orders:
                print(f"  Order ID: {o.id}, Invoice: {o.invoice}, Status: {o.status}")
            flash('Không tìm thấy đơn hàng!', 'danger')
            return redirect(url_for('payment_history'))

        print(f"Order found: ID={order.id}, Status={order.status}, Customer={order.customer_id}")

        # Check if order belongs to current user (if logged in)
        if current_user.is_authenticated:
            if order.customer_id != current_user.id:
                print(f"ERROR: Order {order_id} belongs to customer {order.customer_id}, but current user is {current_user.id}")
                flash('Bạn không có quyền truy cập đơn hàng này!', 'danger')
                return redirect(url_for('payment_history'))

        # Process payment result
        print(f"Processing payment result with response_code: {response_code}")
        if response_code == '00':
            print("PAYMENT SUCCESSFUL - Updating order status")
            # Payment successful
            order.status = 'Đã thanh toán'
            db.session.commit()
            print(f"Order {order_id} status updated to 'Đã thanh toán'")

            # Clear cart if payment was successful
            if 'Shoppingcart' in session:
                print("Clearing shopping cart from session")
                session.pop('Shoppingcart', None)

            # Clear pending order session
            if 'pending_order' in session:
                print("Clearing pending order from session")
                session.pop('pending_order', None)

            flash('Thanh toán thành công! Đơn hàng của bạn đã được xác nhận.', 'success')
            print("Redirecting to order detail page")
        else:
            print(f"PAYMENT FAILED - Response code: {response_code}")
            # Payment failed
            order.status = 'Thanh toán thất bại'
            db.session.commit()
            print(f"Order {order_id} status updated to 'Thanh toán thất bại'")

            # Clear pending order session
            if 'pending_order' in session:
                print("Clearing pending order from session")
                session.pop('pending_order', None)

            response_desc = vnpay.get_response_description(response_code)
            print(f"Response description: {response_desc}")
            flash(f'Thanh toán thất bại: {response_desc}', 'danger')

        print("=" * 50)
        print("VNPAY RETURN PROCESSING - SUCCESS")
        print("=" * 50)
        return redirect(url_for('order_detail', invoice=order_id))

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


@app.route('/vnpay_ipn', methods=['POST'])
def vnpay_ipn():
    """
    Handle VNPAY Instant Payment Notification (IPN)
    This endpoint is called by VNPAY server to notify payment status
    """
    print("=" * 50)
    print("VNPAY IPN PROCESSING - START")
    print("=" * 50)

    try:
        # Get all VNPAY IPN parameters
        vnp_response = request.form.to_dict()
        print(f"VNPAY IPN received: {vnp_response}")

        # Log individual important parameters
        print(f"vnp_ResponseCode: {vnp_response.get('vnp_ResponseCode', 'NOT_FOUND')}")
        print(f"vnp_TxnRef: {vnp_response.get('vnp_TxnRef', 'NOT_FOUND')}")
        print(f"vnp_Amount: {vnp_response.get('vnp_Amount', 'NOT_FOUND')}")
        print(f"vnp_OrderInfo: {vnp_response.get('vnp_OrderInfo', 'NOT_FOUND')}")
        print(f"vnp_TransactionNo: {vnp_response.get('vnp_TransactionNo', 'NOT_FOUND')}")
        print(f"vnp_BankCode: {vnp_response.get('vnp_BankCode', 'NOT_FOUND')}")
        print(f"vnp_PayDate: {vnp_response.get('vnp_PayDate', 'NOT_FOUND')}")
        print(f"vnp_SecureHash: {vnp_response.get('vnp_SecureHash', 'NOT_FOUND')}")

        # Import VNPAY utility and validate response
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()
        print("VNPAY instance created for IPN validation")

        # Validate response
        print("Starting IPN response validation...")
        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)
        print(f"IPN Validation result: is_valid={is_valid}, response_code={response_code}, order_id={order_id}")

        if not is_valid:
            print("ERROR: Invalid VNPAY IPN signature")
            print("This could be due to:")
            print("1. Wrong VNPAY_HASH_SECRET in configuration")
            print("2. IPN request tampered with")
            print("3. Network issues during IPN transmission")
            print("=" * 50)
            print("VNPAY IPN PROCESSING - INVALID SIGNATURE")
            print("=" * 50)
            return 'INVALID_SIGNATURE', 400

        # Get order information
        print(f"Looking for order with invoice: {order_id}")
        order = CustomerOrder.query.filter_by(invoice=order_id).first()
        if not order:
            print(f"ERROR: Order not found: {order_id}")
            print("Available orders in database:")
            all_orders = CustomerOrder.query.limit(10).all()
            for o in all_orders:
                print(f"  Order ID: {o.id}, Invoice: {o.invoice}, Status: {o.status}")
            print("=" * 50)
            print("VNPAY IPN PROCESSING - ORDER NOT FOUND")
            print("=" * 50)
            return 'ORDER_NOT_FOUND', 404

        print(f"Order found: ID={order.id}, Status={order.status}, Customer={order.customer_id}")

        # Get transaction information
        vnp_amount = int(vnp_response.get('vnp_Amount', 0)) / 100  # Convert back from VNPAY format
        vnp_txn_ref = vnp_response.get('vnp_TxnRef', '')
        vnp_transaction_no = vnp_response.get('vnp_TransactionNo', '')
        vnp_bank_code = vnp_response.get('vnp_BankCode', '')
        vnp_pay_date = vnp_response.get('vnp_PayDate', '')

        print(f"Transaction details: amount={vnp_amount}, txn_ref={vnp_txn_ref}, transaction_no={vnp_transaction_no}, bank_code={vnp_bank_code}, pay_date={vnp_pay_date}")

        # Process payment result
        print(f"Processing IPN payment result with response_code: {response_code}")
        if response_code == '00':
            print("IPN PAYMENT SUCCESSFUL - Updating order status")
            # Payment successful
            if order.status != 'Đã thanh toán':
                order.status = 'Đã thanh toán'
                db.session.commit()
                print(f"Order {order_id} payment confirmed via IPN")
            else:
                print(f"Order {order_id} already marked as paid")

            print("=" * 50)
            print("VNPAY IPN PROCESSING - SUCCESS")
            print("=" * 50)
            # Return success response to VNPAY
            return jsonify({
                'RspCode': '00',
                'Message': 'Confirm Success'
            })
        else:
            print(f"IPN PAYMENT FAILED - Response code: {response_code}")
            # Payment failed or other status
            if order.status == 'Chờ thanh toán':
                order.status = 'Thanh toán thất bại'
                db.session.commit()
                print(f"Order {order_id} payment failed via IPN: {response_code}")

            response_desc = vnpay.get_response_description(response_code)
            print(f"IPN Response description: {response_desc}")

            print("=" * 50)
            print("VNPAY IPN PROCESSING - PAYMENT FAILED")
            print("=" * 50)
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
