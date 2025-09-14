import hashlib
import hmac
import urllib.parse
from datetime import datetime

class VNPay:
    def __init__(self, vnpay_url, tmn_code, hash_secret, return_url, ipn_url):
        self.vnpay_url = vnpay_url
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.return_url = return_url
        self.ipn_url = ipn_url

    def create_payment_url(self, order_info, order_id, amount, order_type='billpayment',
                          language='vn', bank_code='', expire_date=None, ip_addr=''):
        vnp_params = {
            'vnp_Version': '2.0.0',  # Thay đổi từ 2.1.0 thành 2.0.0 như C#
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.tmn_code,
            'vnp_Amount': str(amount * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_id,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': order_type,
            'vnp_Locale': language,
            'vnp_ReturnUrl': self.return_url,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S')
        }

        # Thêm IP address nếu có
        if ip_addr:
            vnp_params['vnp_IpAddr'] = ip_addr

        if bank_code:
            vnp_params['vnp_BankCode'] = bank_code

        if expire_date:
            vnp_params['vnp_ExpireDate'] = expire_date

        # Sắp xếp theo key như trong code C#
        sorted_params = sorted(vnp_params.items(), key=lambda x: x[0])
        hash_data = '&'.join([f"{key}={str(value)}" for key, value in sorted_params])

        secure_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        vnp_params['vnp_SecureHash'] = secure_hash

        query_parts = [f'{key}={urllib.parse.quote_plus(str(value))}' for key, value in vnp_params.items()]
        query_string = '&'.join(query_parts)

        return f"{self.vnpay_url}?{query_string}"

    def validate_response(self, response_data):
        vnp_secure_hash = response_data.get('vnp_SecureHash', '')
        vnp_response_code = response_data.get('vnp_ResponseCode', '')
        vnp_txn_ref = response_data.get('vnp_TxnRef', '')

        params_for_hash = {k: v for k, v in response_data.items() if k != 'vnp_SecureHash'}
        sorted_params = sorted(params_for_hash.items())
        hash_data = '&'.join([f"{key}={str(value)}" for key, value in sorted_params])

        calculated_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        is_valid = hmac.compare_digest(calculated_hash, vnp_secure_hash)
        return is_valid, vnp_response_code, vnp_txn_ref

    def get_response_description(self, response_code):
        codes = {
            '00': 'Thành công', '01': 'Giao dịch tồn tại', '02': 'Merchant không hợp lệ',
            '03': 'Dữ liệu sai định dạng', '04': 'Website bị khóa', '05': 'Website chưa đăng ký',
            '06': 'Website chưa cấu hình', '07': 'Server bị firewall', '08': 'Website chưa cấp phép',
            '09': 'Chưa đăng ký Internet Banking', '10': 'Sai thông tin xác thực',
            '11': 'Hết hạn thanh toán', '12': 'Thẻ/tài khoản bị khóa', '13': 'Sai OTP',
            '24': 'Khách hàng hủy', '51': 'Không đủ số dư', '65': 'Vượt hạn mức',
            '75': 'Ngân hàng bảo trì', '79': 'Sai mật khẩu quá lần quy định', '99': 'Lỗi khác'
        }
        return codes.get(response_code, f'Lỗi: {response_code}')

def create_vnpay_instance():
    from flask import current_app
    return VNPay(
        current_app.config['VNPAY_URL'],
        current_app.config['VNPAY_TMN_CODE'],
        current_app.config['VNPAY_HASH_SECRET'],
        current_app.config['VNPAY_RETURN_URL'],
        current_app.config['VNPAY_IPN_URL']
    )
