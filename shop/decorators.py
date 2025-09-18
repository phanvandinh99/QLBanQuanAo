"""
Decorators for authentication and authorization
"""

from functools import wraps
from flask import session, flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """Decorator to require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để tiếp tục', 'danger')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_active_required(f):
    """Decorator to require active customer account"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để tiếp tục', 'danger')
            return redirect(url_for('customer_login'))

        if current_user.is_locked():
            flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
            return redirect(url_for('customer_login'))

        return f(*args, **kwargs)
    return decorated_function

def admin_or_customer_required(f):
    """Decorator to require either admin or customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session and not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để tiếp tục', 'danger')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated_function

def no_cache(f):
    """Decorator to prevent caching"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

def require_https(f):
    """Decorator to redirect HTTP to HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.url.startswith('http://') and not request.url.startswith('http://localhost'):
            return redirect(request.url.replace('http://', 'https://', 1), code=301)
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=100, window_seconds=60):
    """Decorator for basic rate limiting"""
    requests = {}

    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        from flask import request

        # Simple IP-based rate limiting
        client_ip = request.remote_addr
        current_time = time.time()

        # Clean old requests
        if client_ip in requests:
            requests[client_ip] = [t for t in requests[client_ip] if current_time - t < window_seconds]

        # Check rate limit
        if client_ip in requests and len(requests[client_ip]) >= max_requests:
            flash('Quá nhiều yêu cầu. Vui lòng thử lại sau.', 'danger')
            return redirect(request.referrer or url_for('home'))

        # Add current request
        if client_ip not in requests:
            requests[client_ip] = []
        requests[client_ip].append(current_time)

        return f(*args, **kwargs)
    return decorated_function
