"""
Input validation and sanitization utilities
"""

import re
from bleach import clean
from shop.errors import ValidationError

def sanitize_html(text, strip=True):
    """Sanitize HTML input to prevent XSS attacks"""
    if not text:
        return ""

    # Allow only safe tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    allowed_attributes = {}

    return clean(str(text), tags=allowed_tags, attributes=allowed_attributes, strip=strip)

def sanitize_sql_input(text):
    """Basic SQL injection prevention by escaping dangerous characters"""
    if not text:
        return ""

    # Remove or escape dangerous SQL characters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    sanitized = str(text)

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()

def validate_product_name(name):
    """Validate product name"""
    if not name or len(name.strip()) < 2:
        raise ValidationError("Tên sản phẩm phải có ít nhất 2 ký tự")

    if len(name) > 80:
        raise ValidationError("Tên sản phẩm không được vượt quá 80 ký tự")

    # Check for potentially dangerous content
    if re.search(r'[<>]', name):
        raise ValidationError("Tên sản phẩm chứa ký tự không hợp lệ")

    return name.strip()

def validate_price(price):
    """Validate product price"""
    try:
        price_float = float(price)
        if price_float <= 0:
            raise ValidationError("Giá sản phẩm phải lớn hơn 0")
        if price_float > 999999999:  # 1 billion VND max
            raise ValidationError("Giá sản phẩm quá cao")
        return price_float
    except (ValueError, TypeError):
        raise ValidationError("Giá sản phẩm phải là số hợp lệ")

def validate_discount(discount):
    """Validate discount percentage"""
    try:
        discount_int = int(discount)
        if discount_int < 0 or discount_int > 100:
            raise ValidationError("Giảm giá phải nằm trong khoảng 0-100%")
        return discount_int
    except (ValueError, TypeError):
        raise ValidationError("Giảm giá phải là số nguyên hợp lệ")

def validate_stock(stock):
    """Validate stock quantity"""
    try:
        stock_int = int(stock)
        if stock_int < 0:
            raise ValidationError("Số lượng tồn kho phải lớn hơn hoặc bằng 0")
        if stock_int > 999999:  # Reasonable max stock
            raise ValidationError("Số lượng tồn kho quá lớn")
        return stock_int
    except (ValueError, TypeError):
        raise ValidationError("Số lượng tồn kho phải là số nguyên hợp lệ")

def validate_description(description):
    """Validate product description"""
    if not description or len(description.strip()) < 10:
        raise ValidationError("Mô tả sản phẩm phải có ít nhất 10 ký tự")

    if len(description) > 5000:
        raise ValidationError("Mô tả sản phẩm không được vượt quá 5000 ký tự")

    # Sanitize HTML
    return sanitize_html(description)

def validate_username(username):
    """Validate username"""
    if not username or len(username.strip()) < 3:
        raise ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự")

    if len(username) > 50:
        raise ValidationError("Tên đăng nhập không được vượt quá 50 ký tự")

    # Allow only alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError("Tên đăng nhập chỉ được chứa chữ cái, số, gạch dưới và gạch ngang")

    return username.strip().lower()

def validate_email(email):
    """Validate email address"""
    if not email:
        raise ValidationError("Email là bắt buộc")

    email = email.strip().lower()

    # Basic email regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError("Địa chỉ email không hợp lệ")

    if len(email) > 120:
        raise ValidationError("Địa chỉ email quá dài")

    return email

def validate_password(password):
    """Validate password strength"""
    if not password:
        raise ValidationError("Mật khẩu là bắt buộc")

    if len(password) < 6:
        raise ValidationError("Mật khẩu phải có ít nhất 6 ký tự")

    if len(password) > 200:
        raise ValidationError("Mật khẩu quá dài")

    # Check for at least one letter and one number
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError("Mật khẩu phải chứa ít nhất một chữ cái")

    if not re.search(r'[0-9]', password):
        raise ValidationError("Mật khẩu phải chứa ít nhất một số")

    return password

def validate_phone_number(phone):
    """Validate Vietnamese phone number"""
    if not phone:
        raise ValidationError("Số điện thoại là bắt buộc")

    phone = phone.strip()

    # Vietnamese phone number patterns
    patterns = [
        r'^0[3|5|7|8|9][0-9]{8}$',  # 10 digits starting with 0
        r'^\+84[3|5|7|8|9][0-9]{8}$',  # International format +84
    ]

    if not any(re.match(pattern, phone) for pattern in patterns):
        raise ValidationError("Số điện thoại không hợp lệ. Ví dụ: 0987654321 hoặc +84987654321")

    return phone

def validate_address(address):
    """Validate shipping address"""
    if not address or len(address.strip()) < 10:
        raise ValidationError("Địa chỉ giao hàng phải có ít nhất 10 ký tự")

    if len(address) > 500:
        raise ValidationError("Địa chỉ giao hàng quá dài")

    # Remove potentially dangerous characters
    return sanitize_sql_input(address.strip())

def validate_image_filename(filename):
    """Validate image filename and extension"""
    if not filename:
        raise ValidationError("Tên file ảnh là bắt buộc")

    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg', 'ico'}
    if '.' not in filename:
        raise ValidationError("File ảnh phải có phần mở rộng")

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}")

    # Check filename length
    if len(filename) > 150:
        raise ValidationError("Tên file quá dài")

    return filename

def validate_rating(rating):
    """Validate product rating"""
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            raise ValidationError("Đánh giá phải nằm trong khoảng 1-5 sao")
        return rating_int
    except (ValueError, TypeError):
        raise ValidationError("Đánh giá phải là số nguyên hợp lệ")

def validate_comment(comment):
    """Validate product comment/review"""
    if not comment or len(comment.strip()) < 5:
        raise ValidationError("Bình luận phải có ít nhất 5 ký tự")

    if len(comment) > 1000:
        raise ValidationError("Bình luận không được vượt quá 1000 ký tự")

    # Sanitize HTML but allow some formatting
    return sanitize_html(comment, strip=False)
