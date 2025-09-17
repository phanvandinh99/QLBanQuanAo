import secrets
import json
import hmac
import hashlib
from datetime import datetime
from flask import render_template, session, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from shop import app, db
from shop.models import CustomerOrder, Category, Brand, Addproduct, Register
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
        discounttotal += (product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
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

        # Create order immediately with "Chờ thanh toán" status
        print("=" * 60)
        print("VNPAY PAYMENT - CREATING ORDER")
        print("=" * 60)
        print(f"Invoice: {invoice}")
        print(f"Customer ID: {customer_id}")
        print(f"Final amount: {final_amount}")
        print(f"Cart items: {len(session.get('Shoppingcart', {}))}")

        try:
            print("Creating CustomerOrder object...")
            new_order = CustomerOrder(
                invoice=invoice,
                customer_id=customer_id,
                orders=json.dumps(session['Shoppingcart']),
                status="Đang xác nhận",  # Order status: pending confirmation
                payment_status="Đã thanh toán",  # Payment status: already paid online
                address=customer_address,
                amount=final_amount,
                payment_method='vnpay'
            )
            print("Adding to session...")
            db.session.add(new_order)
            print("Committing to database...")
            db.session.commit()
            print(f"✅ Order created successfully with ID: {new_order.id}, Invoice: {invoice}")
            print("=" * 60)

            # Gửi email xác nhận đơn hàng
            customer = Register.query.get(customer_id)
            if customer and customer.email:
                email_sent = send_order_confirmation_email(customer, new_order)
                if email_sent:
                    print(f"Email xác nhận đã gửi đến {customer.email}")
                else:
                    print(f"Không thể gửi email xác nhận đến {customer.email}")
        except Exception as e:
            print(f"❌ ERROR creating order: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print("Full traceback:")
            traceback.print_exc()
            print("=" * 60)
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

    print("=" * 60)
    print("VNPAY RETURN - START PROCESSING")
    print("=" * 60)
    print(f"Request method: {request.method}")
    print(f"Request args: {dict(request.args)}")
    print(f"Request form: {dict(request.form)}")

    try:
        vnp_response = request.args.to_dict()
        print(f"VNP response from args: {vnp_response}")

        if not vnp_response:
            vnp_response = request.form.to_dict()
            print(f"VNP response from form: {vnp_response}")

        if not vnp_response and request.method == 'HEAD':
            print("No VNP response data and HEAD method")
            flash('Không nhận được phản hồi từ VNPAY. Vui lòng kiểm tra lại sau.', 'warning')
            return redirect(url_for('payment_history'))

        print("Creating VNPAY instance...")
        from shop.vnpay_utils import create_vnpay_instance
        vnpay = create_vnpay_instance()

        print("Validating VNPAY response...")
        is_valid, response_code, order_id = vnpay.validate_response(vnp_response)
        print(f"Validation result: is_valid={is_valid}, response_code={response_code}, order_id={order_id}")
        print(f"VNP response keys: {list(vnp_response.keys())}")
        print(f"VNP Response Code: {vnp_response.get('vnp_ResponseCode')}")
        print(f"VNP TxnRef: {vnp_response.get('vnp_TxnRef')}")

        if not is_valid:
            print(f"❌ Invalid signature - VNP response: {vnp_response}")
            flash('Chữ ký không hợp lệ!', 'danger')
            return redirect(url_for('payment_history'))

        # Find the order by invoice
        print(f"Searching for order with invoice: {order_id}")
        try:
            order = CustomerOrder.query.filter_by(invoice=order_id).first()
            if order:
                print(f"✅ Found order: ID={order.id}, Status={order.status}, Customer={order.customer_id}, Payment={order.payment_method}")
            else:
                print(f"❌ No order found for invoice: {order_id}")
                # List all orders for debugging
                all_orders = CustomerOrder.query.limit(10).all()
                print(f"Recent orders in database:")
                for o in all_orders:
                    print(f"  ID: {o.id}, Invoice: {o.invoice}, Status: {o.status}")
                flash('Không tìm thấy đơn hàng để xử lý!', 'danger')
                return redirect(url_for('payment_history'))
        except Exception as e:
            print(f"❌ Database error when finding order: {e}")
            flash('Lỗi database khi tìm đơn hàng!', 'danger')
            return redirect(url_for('payment_history'))

        # Check order ownership (allow processing even if user is not logged in, for VNPAY return)
        if current_user.is_authenticated and order and order.customer_id != current_user.id:
            print(f"ERROR: Order {order_id} belongs to customer {order.customer_id}, but current user is {current_user.id}")
            flash('Bạn không có quyền truy cập đơn hàng này!', 'danger')
            return redirect(url_for('payment_history'))

        # Process payment result
        print(f"Processing payment result with response_code: {response_code}")

        if response_code == '00':
            print("PAYMENT SUCCESSFUL - Order already created with 'Đã thanh toán' status")

            flash('Thanh toán thành công! Đơn hàng của bạn đã được xác nhận.', 'success')
            print("Redirecting to order detail page")

        else:
            print(f"PAYMENT FAILED - Response code: {response_code}")

            # Update order status to "Thanh toán thất bại"
            try:
                order.status = 'Thanh toán thất bại'
                db.session.commit()
                print(f"Order {order_id} status updated to 'Thanh toán thất bại'")
            except Exception as e:
                print(f"❌ ERROR updating failed payment status: {e}")
                db.session.rollback()

            # DON'T clear cart on payment failure - keep it for user to retry
            print("Keeping shopping cart for user to retry payment")

            response_desc = vnpay.get_response_description(response_code)
            print(f"Response description: {response_desc}")
            flash(f'Thanh toán thất bại: {response_desc}. Đơn hàng đã được lưu với trạng thái thất bại.', 'danger')

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


@app.route('/test_vnpay_return/<invoice>', methods=['GET'])
def test_vnpay_return(invoice):
    """Test VNPAY return directly with invoice"""
    print(f"=" * 60)
    print(f"TESTING VNPAY RETURN FOR INVOICE: {invoice}")
    print("=" * 60)

    # Simulate VNPAY return parameters
    mock_params = {
        'vnp_ResponseCode': '00',
        'vnp_TxnRef': invoice,
        'vnp_Amount': '9500000',
        'vnp_OrderInfo': f'Thanh toan don hang {invoice}',
        'vnp_BankCode': 'NCB',
        'vnp_PayDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        'vnp_TransactionNo': f'140000{secrets.token_hex(2)}'
    }

    # Redirect to actual vnpay_return with mock parameters
    query_string = '&'.join([f'{k}={v}' for k, v in mock_params.items()])
    redirect_url = f"{url_for('vnpay_return')}?{query_string}"

    print(f"Redirecting to: {redirect_url}")
    return redirect(redirect_url)


@app.route('/test_vnpay_success', methods=['GET'])
def test_vnpay_success():
    """Test route to simulate successful VNPAY payment"""
    print("=" * 60)
    print("TEST VNPAY SUCCESS - START")
    print("=" * 60)

    if not current_user.is_authenticated:
        print("❌ User not authenticated")
        flash('Vui lòng đăng nhập trước!', 'danger')
        return redirect(url_for('customer_login'))

    print(f"✅ User authenticated: ID={current_user.id}")

    # Create test shopping cart if not exists
    if 'Shoppingcart' not in session:
        session['Shoppingcart'] = {
            '1': {
                'name': 'Test Product',
                'price': 100000.0,
                'discount': 10,
                'color': 'Black',
                'quantity': 1,
                'image': 'test.jpg',
                'colors': 'Black,White',
                'brand': 'Test Brand'
            }
        }
        session.modified = True
        print("✅ Created test shopping cart")

    print(f"Shopping cart: {session['Shoppingcart']}")

    # Create test order immediately
    test_invoice = f'TEST_SUCCESS_{secrets.token_hex(4)}'
    print(f"Test invoice: {test_invoice}")

    try:
        test_order = CustomerOrder(
            invoice=test_invoice,
            customer_id=current_user.id,
            orders=json.dumps(session['Shoppingcart']),
            status="Đang xác nhận",  # Order status
            payment_status="Đã thanh toán",  # Payment status for VNPAY test
            address='123 Test Address, Hanoi',
            amount=90000,  # 100000 - 10% discount
            payment_method='vnpay_test'
        )
        db.session.add(test_order)
        db.session.commit()

        print("=" * 60)
        print("TESTING VNPAY SUCCESS SIMULATION")
        print("=" * 60)
        print(f"✅ Test order created: ID={test_order.id}, Invoice={test_invoice}")
        print(f"User: {current_user.id}")

        # Clear cart after successful test order creation
        if 'Shoppingcart' in session:
            print("🗑️ Clearing shopping cart after test order creation")
            session.pop('Shoppingcart', None)
            session.modified = True
            print("✅ Shopping cart cleared from session")

        flash('Đơn hàng test đã được tạo thành công! Giỏ hàng đã được xóa.', 'success')

        # Simulate successful VNPAY return
        return redirect(url_for('vnpay_return', vnp_ResponseCode='00', vnp_TxnRef=test_invoice, vnp_Amount='9000000'))

    except Exception as e:
        print(f"❌ ERROR creating test order: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash('Lỗi tạo đơn hàng test!', 'danger')
        return redirect(url_for('getCart'))


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
