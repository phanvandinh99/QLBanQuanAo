"""
Custom exceptions and error handlers
"""

from flask import jsonify, render_template, current_app, flash, redirect, url_for, request
from werkzeug.exceptions import HTTPException

class MobileStoreError(Exception):
    """Base exception for MobileStore application"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

class ValidationError(MobileStoreError):
    """Validation error"""
    pass

class AuthenticationError(MobileStoreError):
    """Authentication error"""
    def __init__(self, message="Authentication required", status_code=401):
        super().__init__(message, status_code)

class AuthorizationError(MobileStoreError):
    """Authorization error"""
    def __init__(self, message="Access denied", status_code=403):
        super().__init__(message, status_code)

class NotFoundError(MobileStoreError):
    """Resource not found error"""
    def __init__(self, message="Resource not found", status_code=404):
        super().__init__(message, status_code)

class DatabaseError(MobileStoreError):
    """Database operation error"""
    def __init__(self, message="Database error", status_code=500):
        super().__init__(message, status_code)

class PaymentError(MobileStoreError):
    """Payment processing error"""
    def __init__(self, message="Payment processing failed", status_code=400):
        super().__init__(message, status_code)

def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(MobileStoreError)
    def handle_mobile_store_error(error):
        """Handle custom MobileStore errors"""
        if current_app.config['DEBUG']:
            response = {
                'error': error.message,
                'status_code': error.status_code,
                'payload': error.payload
            }
        else:
            response = {
                'error': 'An error occurred',
                'status_code': error.status_code
            }

        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found', 'status_code': 404}), 404
        else:
            return render_template('404.html'), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        current_app.logger.error(f"Internal server error: {error}")

        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'status_code': 500}), 500
        else:
            flash('Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.', 'danger')
            return render_template('500.html'), 500

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Access denied', 'status_code': 403}), 403
        else:
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('home'))

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Authentication required', 'status_code': 401}), 401
        else:
            flash('Vui lòng đăng nhập để tiếp tục.', 'danger')
            return redirect(url_for('customer_login'))

def safe_db_operation(operation_func):
    """Decorator for safe database operations"""
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
    return wrapper

def validate_required_fields(data, required_fields):
    """Validate required fields in data dictionary"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)

    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_numeric_field(value, field_name, min_value=None, max_value=None):
    """Validate numeric field"""
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")

    if min_value is not None and num_value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")

    if max_value is not None and num_value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")

    return num_value

def validate_email_format(email):
    """Validate email format"""
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValidationError("Invalid email format")

def validate_phone_format(phone):
    """Validate phone format"""
    import re
    # Vietnamese phone number regex
    phone_regex = r'^(0|\+84)[3|5|7|8|9][0-9]{8}$'
    if not re.match(phone_regex, phone):
        raise ValidationError("Invalid phone number format")

def log_error(message, level='error'):
    """Log error message"""
    if current_app:
        logger = current_app.logger
        if level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'info':
            logger.info(message)
        else:
            logger.debug(message)
