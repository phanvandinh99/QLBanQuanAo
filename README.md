
# Lập trình web bán hàng điện thoại sử dụng Flask!
Link website: 
- Giao diện người dùng: [https://thuctapcongnhan2020.herokuapp.com/](https://thuctapcongnhan2020.herokuapp.com/)
- Giao diện admin: [https://thuctapcongnhan2020.herokuapp.com/admin](https://thuctapcongnhan2020.herokuapp.com/admin)

- Tên đề tài : **Website bán hàng điện thoại.**
- Ngôn ngữ backend: [Flask-Python](https://flask.palletsprojects.com/en/1.1.x/)
- Cơ sở dữ liệu: MySQL.

## Mục lục:
1.[Hướng dẫn cài đặt](#p1)

2.[Các chức năng chính của chương trình](#p2)

3.[Cấu trúc thư mục chương trình](#p3)

4.[Tài liệu tham khảo](#p4)

<a id="p1"></a> 
# Hướng dẫn cài đặt:
1. Tải source code:

2. Cài đặt python : [Python 3.8](https://www.python.org/downloads/release/python-380/)

3. Download database: [here](database/myshop.sql)

3.1
```shell
python -m venv venv
```

```shell
venv\Scripts\activate
    => cmd "Set-ExecutionPolicy RemoteSigned"
```

4. Cài đặt môi trường thư viện tự động sử dụng tệp requirements.txt

```shell
pip install -r requirements.txt
```

5. Khởi chạy chương trình:
```shell
python run.py
```
7. Truy cập trang admin: thêm **/admin** sau tên miền.
6. Tài khoản đăng nhập trang admin:  Tai khoan admin: [viethoang@gmail.com](viethoang123@gmail.com) ,password: viethoang123

<a id="p2"></a> 
# Các chức năng chính của chương trình.
Được đặc tả qua tài liệu Usecase tổng quát:
<div align='center'>
  <img src='images/use_case.png'>
</div>

- Giao diện chính:

![alt tag](images/GUIUser.png)

![alt tag](images/GUIAdmin.png)

<a id="p3"></a> 
# Cấu trúc thư mục chương trình
```
$ Cấu trúc thư mục
.
├── shop
│   ├── admin
│   └── carts
│   └── customers
│   └── products
│   └── static
│   └── template
│   └── __init__.py
├── images
│   ├── use_case.png
│   ├── GUIAdmin.png
│   ├── GUIUser.png
├── database
│   ├── myshop.sql
└── requirements.txt
└── README.md
└── run.py

```

<a id="p4"></a> 
# VNPAY Payment Integration

## Overview
This project now includes VNPAY payment gateway integration for secure online payments.

## Configuration
The VNPAY integration is configured in `shop/__init__.py`:

```python
# VNPAY Configuration
app.config['VNPAY_URL'] = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
app.config['VNPAY_TMN_CODE'] = 'QV4AJ3NO'
app.config['VNPAY_HASH_SECRET'] = '3CP0V5HCDJ6VFE1YPVYL85YUHK1SGLLP'
app.config['VNPAY_RETURN_URL'] = 'http://localhost:5000/vnpay_return'
app.config['VNPAY_IPN_URL'] = 'http://localhost:5000/vnpay_ipn'
```

## How It Works

### 1. Payment Initiation
- User selects VNPAY payment method in the cart
- System creates an order with "Chờ thanh toán" status
- VNPAY payment URL is generated and user is redirected

### 2. Payment Processing
- User completes payment on VNPAY's secure platform
- VNPAY redirects user back to `/vnpay_return` endpoint
- System validates payment and updates order status

### 3. Payment Confirmation
- IPN (Instant Payment Notification) is sent to `/vnpay_ipn` for server-side confirmation
- Order status is updated to "Đã thanh toán" upon successful payment

## Usage

1. Add products to cart
2. Go to checkout page
3. Select "Thanh toán VNPAY" payment method
4. Enter shipping address
5. Click "Đặt hàng" to proceed to VNPAY payment
6. Complete payment on VNPAY platform
7. System will redirect back and confirm payment

## API Endpoints

- `POST /vnpay_payment` - Initiates VNPAY payment
- `GET /vnpay_return` - Handles payment completion redirect
- `POST /vnpay_ipn` - Handles payment status notifications

## Order Status Flow

1. **Chờ thanh toán** - Order created, waiting for payment
2. **Đã thanh toán** - Payment successful
3. **Thanh toán thất bại** - Payment failed or cancelled

## Security Features

- HMAC-SHA512 signature validation
- Secure hash verification for all transactions
- Server-side payment confirmation via IPN
- Order status validation

## Testing

Use VNPAY sandbox environment for testing:
- URL: https://sandbox.vnpayment.vn
- Test cards and instructions available in VNPAY documentation

## VNPAY Debug Tools

## Debug Endpoint
Access the debug endpoint to test VNPAY integration: `http://localhost:5000/debug_vnpay`

This endpoint will:
- Test URL generation
- Test hash validation
- Show current configuration
- Help identify configuration issues

## Logging
The application now includes comprehensive logging for all VNPAY operations:

### Payment Initiation Logs:
```
VNPAY PAYMENT INITIATION - START
- Customer info, cart contents, calculated totals
- Order creation details
- Generated payment URL
```

### Return Processing Logs:
```
VNPAY RETURN PROCESSING - START
- All VNPAY response parameters
- Validation results
- Order lookup and status updates
```

### IPN Processing Logs:
```
VNPAY IPN PROCESSING - START
- IPN request parameters
- Validation and processing results
```

### Utility Function Logs:
```
VNPAY URL CREATION - START
- Parameter details and hash generation
VNPAY RESPONSE VALIDATION - START
- Hash validation process and results
```

## Common Issues & Solutions

### 1. "Invalid VNPAY signature" Error
**Possible causes:**
- Wrong `VNPAY_HASH_SECRET` in configuration
- Network transmission errors
- Response data tampering

**Solution:**
1. Check `VNPAY_HASH_SECRET` matches your VNPAY dashboard
2. Verify no extra spaces or characters in the secret
3. Check debug endpoint for validation results

### 2. "Order not found" Error
**Possible causes:**
- Order ID mismatch between creation and return
- Database connection issues
- Order was not created successfully

**Solution:**
1. Check console logs for order creation
2. Verify database connectivity
3. Check if order exists in database

### 3. Generic VNPAY Error
**Solution:**
1. Check all console logs for detailed error information
2. Use debug endpoint to test basic functionality
3. Verify VNPAY credentials and configuration

## Testing Steps

### **Phase 1: Local Testing (Debug Mode)**

1. **Start the application:**
```bash
python app.py
```

2. **Test debug endpoint:**
```
http://localhost:5000/debug_vnpay
```

3. **Test VNPAY setup:**
```bash
# Run the test script
python test_vnpay_setup.py

# Or use the batch file (Windows)
test_vnpay.bat
```

### **Phase 2: Full Payment Testing (Requires ngrok)**

#### **Step 1: Install ngrok**
```bash
# Download from: https://ngrok.com/download
# Install and add to PATH
```

#### **Step 2: Expose localhost to internet**
```bash
# In a new terminal/command prompt
ngrok http 5000
```

#### **Step 3: Update VNPAY URLs**
After running ngrok, you'll get a URL like: `https://abcd1234.ngrok.io`

Update `shop/__init__.py`:
```python
app.config['VNPAY_RETURN_URL'] = 'https://abcd1234.ngrok.io/vnpay_return'
app.config['VNPAY_IPN_URL'] = 'https://abcd1234.ngrok.io/vnpay_ipn'
```

#### **Step 4: Restart Flask app**
```bash
# Stop Flask app (Ctrl+C)
python app.py
```

#### **Step 5: Test full payment flow**
- Add items to cart
- Select VNPAY payment
- Complete payment on VNPAY sandbox
- Check console logs for detailed processing info

### **Phase 3: Monitor and Debug**

4. **Monitor logs:**
   - All VNPAY operations are logged with detailed information
   - Look for `VNPAY` prefixed log messages
   - Check for validation failures or order issues

**⚠️ IMPORTANT:** Without ngrok, VNPAY cannot access your localhost URLs, causing error code 99!

## Production Usage Guide

### 1. **Basic Payment Flow:**
```python
# User adds items to cart
# User selects VNPAY payment method
# User fills shipping address
# User clicks "Đặt hàng"

# System automatically:
# 1. Calculates total amount
# 2. Creates order with status "Chờ thanh toán"
# 3. Generates VNPAY payment URL
# 4. Redirects user to VNPAY

# User completes payment on VNPAY
# VNPAY redirects back to your site
# System validates payment and updates order status
```

### 2. **Integration Points:**

**Frontend (carts.html):**
- Payment method selection radio buttons (already implemented)
- Address input form (already implemented)
- JavaScript for form submission (already implemented)

**Backend Routes:**
- `/vnpay_payment` - Initiates payment (POST)
- `/vnpay_return` - Handles payment return (GET)
- `/vnpay_ipn` - Handles payment notifications (POST)

### 3. **Order Status Flow:**
```
1. User clicks "Đặt hàng" → Order status: "Chờ thanh toán"
2. Redirect to VNPAY → User completes payment
3. VNPAY returns → System validates → Order status: "Đã thanh toán"
4. Alternative: Payment failed → Order status: "Thanh toán thất bại"
```

### 4. **Error Handling:**
- All errors are logged with detailed information
- User-friendly error messages are displayed
- System gracefully handles payment failures
- Cart is cleared only on successful payment

### 5. **Security Features:**
- HMAC-SHA512 signature validation
- Secure hash verification for all transactions
- Order ownership validation
- Input sanitization and validation

# Production Deployment

For production, update the configuration:
1. Change VNPAY_URL to production endpoint
2. Update TMN_CODE and HASH_SECRET with production credentials
3. Update RETURN_URL and IPN_URL to your production domain
4. Ensure HTTPS is enabled for all payment endpoints

# Tài liệu tham khảo

 1. Template : [https://easetemplate.com/downloads/online-mobile-store-shopping-website-template/](https://easetemplate.com/downloads/online-mobile-store-shopping-website-template/)
2. Youtube: [https://www.youtube.com/watch?v=o9TwipumGoU&list=PLYPlvTh05MsxJja9bzQCSTDu4hnEv5N](https://www.youtube.com/watch?v=o9TwipumGoU&list=PLYPlvTh05MsxJja9bzQCSTDu4hnEv5N_u&index=1)
