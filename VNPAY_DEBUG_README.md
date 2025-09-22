# VNPay Debug Guide

## Tổng quan
Hướng dẫn này giúp debug các vấn đề thường gặp với tích hợp VNPay trong hệ thống MobileStore.

## Các cải tiến đã thực hiện

### 1. Logging chi tiết
- Tất cả các request VNPay (return, IPN) đều được log chi tiết
- Signature validation được log với thông tin đầy đủ
- Order status changes được track
- Lỗi được phân loại theo mức độ nghiêm trọng

### 2. Error handling cải thiện
- Thông báo lỗi cụ thể hơn thay vì generic message
- Hiển thị mã lỗi VNPay và mô tả
- Log chi tiết để debug

### 3. Debug tool
- Route `/vnpay_debug` cho admin để kiểm tra cấu hình
- Test payment URL generation
- Test signature validation
- Hướng dẫn khắc phục các vấn đề thường gặp

## Cách sử dụng Debug Tool

### Truy cập Debug Page
1. Đăng nhập với tài khoản admin
2. Truy cập: `http://your-domain/vnpay_debug`

### Kiểm tra Configuration
- Xác nhận tất cả VNPay config được cấu hình đúng
- Kiểm tra hash secret có được set không
- Verify URLs (return, IPN) đúng format

### Test Validation
- Tool sẽ test tạo payment URL
- Test signature validation với mock data
- Hiển thị kết quả thành công/thất bại

## Các vấn đề thường gặp và khắc phục

### 1. "Invalid Signature" Error
**Nguyên nhân:**
- Hash secret không khớp giữa config và VNPay dashboard
- Thứ tự parameters sai khi hash
- URL encoding/decoding issues
- Network corruption của response data

**Giải pháp:**
```bash
# Kiểm tra logs
grep "VNPAY signature validation failed" logs/app.log
grep "Expected hash:" logs/app.log
grep "CRITICAL.*signature validation failed.*response_code='00'" logs/app.log
```

**Kiểm tra:**
- Hash secret trong `config.py` khớp với VNPay dashboard
- Không có ký tự đặc biệt trong secret
- Secret không có khoảng trắng thừa
- Nếu thấy "CRITICAL" log: Có thể bị tấn công man-in-the-middle!

**Lưu ý quan trọng:**
Khi signature fails nhưng response_code='00', đây có thể là vấn đề bảo mật nghiêm trọng. KHÔNG tin tưởng response_code khi signature validation fails.

### 2. "Order Not Found" Error
**Nguyên nhân:**
- Invoice format không tương thích (quá dài, chứa ký tự đặc biệt)
- Order không được lưu trước khi redirect
- Database connection issues

**Giải pháp:**
```bash
# Kiểm tra invoice format
grep "invoice.*=" logs/app.log
```

**Kiểm tra:**
- Invoice chỉ chứa alphanumeric characters
- Invoice length < 34 ký tự
- Order được commit thành công trước redirect

### 3. Payment Amount Issues
**Nguyên nhân:**
- Lỗi tính toán số tiền
- Format VND * 100 sai
- Discount calculation errors

**Giải pháp:**
```bash
# Kiểm tra amount logs
grep "final_amount.*=" logs/app.log
grep "VNPAY.*amount.*=" logs/app.log
```

## Log Analysis

### Log Levels
```
CRITICAL: Security issues, potential attacks (signature fails but response_code='00')
ERROR: Critical errors, signature failures
WARNING: Failed payments, non-critical issues
INFO: Successful operations
DEBUG: Detailed validation info (enable for troubleshooting)
```

### Key Log Messages
```bash
# Payment creation
"VNPAY payment URL created for invoice {invoice}"
"VNPAY order created successfully, cart cleared immediately for order {invoice}"

# Return processing
"VNPAY return received. Method: {method}, Response keys: {keys}"
"VNPAY validation result: valid={valid}, response_code={code}"
"VNPAY payment successful for order {order_id}, cart existed: {existed}, cart cleared: {cleared}, user authenticated: {auth}"
"Clearing cart for user {user_id} due to recent successful VNPay orders: {invoices}"

# IPN processing
"VNPAY IPN received. Response keys: {keys}"
"VNPAY IPN validation result: valid={valid}"

# Errors
"VNPAY signature validation failed for order {order_id}"
"Expected hash: {expected}, Received hash: {received}"
"CRITICAL: VNPAY signature validation failed but response_code='00' (success) for order {order_id}. Potential security issue!"
```

## Enable Debug Logging

Trong `config.py`, set:
```python
LOG_LEVEL = 'DEBUG'
```

Hoặc trong production, enable debug cho VNPay specific:
```python
import logging
vnpay_logger = logging.getLogger('shop.vnpay_utils')
vnpay_logger.setLevel(logging.DEBUG)
```

## Testing VNPay Integration

### Manual Testing
1. Tạo đơn hàng test với số tiền nhỏ
2. Chọn thanh toán VNPay
3. Redirect đến VNPay sandbox
4. Test các response codes khác nhau
5. Kiểm tra giỏ hàng đã được xóa sau khi VNPay return thành công

### Cart Clearing Logic
- **COD:** Cart được xóa ngay sau khi tạo order thành công
- **VNPay:**
  1. Cart được xóa ngay khi VNPay return với response_code='00' (thành công)
  2. Nếu cart vẫn còn (do session issues), cart sẽ được xóa tự động khi user xem cart nếu họ có order VNPay thành công trong vòng 1 giờ
- **Lý do:** Xử lý trường hợp session không persistent hoặc user logout/login lại sau thanh toán

### VNPay Test Cards
- Sử dụng test cards từ VNPay documentation
- Test success và failure scenarios
- Verify IPN callback

## Configuration Checklist

- [ ] VNPAY_URL: Correct sandbox/production URL
- [ ] VNPAY_TMN_CODE: Merchant code from VNPay
- [ ] VNPAY_HASH_SECRET: Secret key (no spaces/extra chars)
- [ ] VNPAY_RETURN_URL: Your return endpoint
- [ ] VNPAY_IPN_URL: Your IPN endpoint
- [ ] Database: Orders table exists with correct schema
- [ ] Routes: /vnpay_return, /vnpay_ipn, /vnpay_payment accessible

## Emergency Recovery

Nếu khách hàng bị trừ tiền nhưng hệ thống báo lỗi:

1. **Kiểm tra logs ngay lập tức:**
```bash
grep "VNPAY.*{order_id}" logs/app.log
```

2. **Manual order verification:**
```sql
SELECT * FROM orders WHERE invoice = '{order_id}';
```

3. **Manual payment status update if needed:**
```sql
UPDATE orders SET payment_status = 'paid' WHERE invoice = '{order_id}';
```

4. **Contact VNPay support với transaction details**

## Support

Khi báo lỗi cho support:
1. Include order ID/invoice
2. VNPay transaction reference (vnp_TxnRef)
3. Response code từ VNPay
4. Relevant log entries
5. Debug page screenshots
