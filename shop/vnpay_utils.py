import hashlib
import hmac
import json
import urllib.parse
import urllib.request
from datetime import datetime
import requests

class VNPay:
    def __init__(self, vnpay_url, tmn_code, hash_secret, return_url, ipn_url):
        self.vnpay_url = vnpay_url
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.return_url = return_url
        self.ipn_url = ipn_url

    def create_payment_url(self, order_info, order_id, amount, order_type='billpayment',
                          language='vn', bank_code='', expire_date=None):
        """
        Create VNPAY payment URL

        Args:
            order_info (str): Order description
            order_id (str): Unique order ID
            amount (int): Amount in VND (multiply by 100 as per VNPAY requirement)
            order_type (str): Order type
            language (str): Language ('vn' or 'en')
            bank_code (str): Bank code for direct bank selection
            expire_date (str): Payment expiration date (format: YYYYMMDDHHmmss)

        Returns:
            str: VNPAY payment URL
        """
        print("=" * 50)
        print("VNPAY URL CREATION - START")
        print("=" * 50)
        print(f"Input parameters: order_info={order_info}, order_id={order_id}, amount={amount}")

        # VNPAY parameters
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.tmn_code,
            'vnp_Amount': str(amount * 100),  # VNPAY expects amount in smallest currency unit
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_id,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': order_type,
            'vnp_Locale': language,
            'vnp_ReturnUrl': self.return_url,
            'vnp_IpnUrl': self.ipn_url,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S')
        }

        print(f"VNPAY base parameters: {vnp_params}")

        # Add optional parameters
        if bank_code:
            vnp_params['vnp_BankCode'] = bank_code
            print(f"Added bank_code: {bank_code}")

        if expire_date:
            vnp_params['vnp_ExpireDate'] = expire_date
            print(f"Added expire_date: {expire_date}")

        # Sort parameters and create signature
        sorted_params = sorted(vnp_params.items())
        print(f"Sorted parameters: {sorted_params}")

        query_string = '&'.join([f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in sorted_params])
        print(f"Query string: {query_string}")

        # Create secure hash
        hash_data = '&'.join([f"{key}={str(value)}" for key, value in sorted_params])
        print(f"Hash data: {hash_data}")
        print(f"Hash secret: {self.hash_secret}")

        secure_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        print(f"Generated secure hash: {secure_hash}")

        # Add signature to parameters
        vnp_params['vnp_SecureHash'] = secure_hash

        # Create final URL
        payment_url = f"{self.vnpay_url}?{urllib.parse.urlencode(vnp_params)}"
        print(f"Final payment URL: {payment_url}")

        print("=" * 50)
        print("VNPAY URL CREATION - SUCCESS")
        print("=" * 50)
        return payment_url

    def validate_response(self, response_data):
        """
        Validate VNPAY response data

        Args:
            response_data (dict): Response data from VNPAY

        Returns:
            tuple: (is_valid, response_code, order_id)
        """
        print("=" * 50)
        print("VNPAY RESPONSE VALIDATION - START")
        print("=" * 50)

        print(f"Full response data: {response_data}")

        vnp_secure_hash = response_data.get('vnp_SecureHash', '')
        vnp_response_code = response_data.get('vnp_ResponseCode', '')
        vnp_txn_ref = response_data.get('vnp_TxnRef', '')

        print(f"Extracted values: secure_hash={vnp_secure_hash}, response_code={vnp_response_code}, txn_ref={vnp_txn_ref}")

        # Remove secure hash from parameters for validation
        params_for_hash = {k: v for k, v in response_data.items() if k != 'vnp_SecureHash'}
        print(f"Parameters for hash calculation: {params_for_hash}")

        # Sort parameters
        sorted_params = sorted(params_for_hash.items())
        print(f"Sorted parameters: {sorted_params}")

        # Create hash data
        hash_data = '&'.join([f"{key}={str(value)}" for key, value in sorted_params])
        print(f"Hash data string: {hash_data}")
        print(f"Hash secret: {self.hash_secret}")

        # Calculate secure hash
        calculated_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        print(f"VNPAY provided hash: {vnp_secure_hash}")
        print(f"Calculated hash: {calculated_hash}")

        # Validate signature
        is_valid = hmac.compare_digest(calculated_hash, vnp_secure_hash)
        print(f"Hash validation result: {is_valid}")

        if not is_valid:
            print("HASH VALIDATION FAILED!")
            print("This indicates:")
            print("- Wrong VNPAY_HASH_SECRET configuration")
            print("- Response data was tampered with")
            print("- Network transmission error")
            print("- Hash calculation error in our code")
        else:
            print("HASH VALIDATION SUCCESS!")

        print("=" * 50)
        print("VNPAY RESPONSE VALIDATION - END")
        print("=" * 50)

        return is_valid, vnp_response_code, vnp_txn_ref

    def get_response_description(self, response_code):
        """
        Get description for VNPAY response code

        Args:
            response_code (str): VNPAY response code

        Returns:
            str: Description of the response code
        """
        response_codes = {
            '00': 'Giao dịch thành công',
            '01': 'Giao dịch đã tồn tại',
            '02': 'Merchant không hợp lệ',
            '03': 'Dữ liệu gửi sang không đúng định dạng',
            '04': 'Khởi tạo GD không thành công do Website đang bị tạm khóa',
            '05': 'Khởi tạo GD không thành công do Mã Website chưa được đăng ký',
            '06': 'Khởi tạo GD không thành công do Mã Website chưa được cấu hình',
            '07': 'Giao dịch không thành công do Server bị firewall chặn',
            '08': 'Khởi tạo GD không thành công do Website chưa được cấp phép',
            '09': 'GD không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.',
            '10': 'GD không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần',
            '11': 'GD không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.',
            '12': 'GD không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.',
            '13': 'GD không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP). Xin quý khách vui lòng thực hiện lại.',
            '24': 'GD không thành công do: Khách hàng hủy giao dịch',
            '51': 'GD không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.',
            '65': 'GD không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.',
            '75': 'Ngân hàng thanh toán đang bảo trì.',
            '79': 'GD không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định. Xin quý khách vui lòng thực hiện lại',
            '99': 'Các lỗi khác (lỗi còn lại, không có trong danh sách mã lỗi đã liệt kê)'
        }

        return response_codes.get(response_code, f'Mã lỗi không xác định: {response_code}')

def create_vnpay_instance():
    """
    Create VNPAY instance with configuration from app config
    """
    from flask import current_app

    return VNPay(
        vnpay_url=current_app.config.get('VNPAY_URL'),
        tmn_code=current_app.config.get('VNPAY_TMN_CODE'),
        hash_secret=current_app.config.get('VNPAY_HASH_SECRET'),
        return_url=current_app.config.get('VNPAY_RETURN_URL'),
        ipn_url=current_app.config.get('VNPAY_IPN_URL')
    )
