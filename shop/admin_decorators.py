"""
Admin decorators for role-based access control
"""

from functools import wraps
from flask import session, flash, redirect, url_for, request
from shop.models import Admin

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Yêu cầu đăng nhập', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_permission=None):
    """Decorator to require specific role or permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session:
                flash('Yêu cầu đăng nhập', 'danger')
                return redirect(url_for('login'))
            
            user = Admin.query.filter_by(email=session['email']).first()
            if not user:
                flash('Tài khoản không tồn tại', 'danger')
                return redirect(url_for('login'))
            
            # If no specific permission required, just check if user has a role
            if required_permission is None:
                return f(*args, **kwargs)
            
            # Check if user has the required permission
            if not user.has_permission(required_permission):
                flash('Bạn không có quyền truy cập chức năng này', 'danger')
                return redirect(url_for('admin'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_only(f):
    """Decorator to require admin role only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Yêu cầu đăng nhập', 'danger')
            return redirect(url_for('login'))
        
        user = Admin.query.filter_by(email=session['email']).first()
        if not user or not user.is_admin:
            flash('Chỉ quản trị viên mới có quyền truy cập', 'danger')
            return redirect(url_for('admin'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_admin():
    """Get current logged in admin"""
    if 'email' in session:
        return Admin.query.filter_by(email=session['email']).first()
    return None

def check_menu_permission(permission):
    """Check if current user has permission to see menu item"""
    user = get_current_admin()
    if not user:
        return False
    return user.has_permission(permission)
