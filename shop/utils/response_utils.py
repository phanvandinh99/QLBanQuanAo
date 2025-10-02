"""
Response utilities for handling AJAX requests and toast notifications
"""

from flask import jsonify, request, redirect, url_for, flash
from functools import wraps


def ajax_response(success=True, message="", data=None, redirect_url=None, reload=False, reset_form=False):
    """
    Tạo JSON response cho AJAX requests
    
    Args:
        success (bool): Trạng thái thành công
        message (str): Thông báo hiển thị
        data (dict): Dữ liệu bổ sung
        redirect_url (str): URL để redirect
        reload (bool): Có reload trang không
        reset_form (bool): Có reset form không
    
    Returns:
        JSON response
    """
    response_data = {
        'success': success,
        'message': message
    }
    
    if data:
        response_data.update(data)
    
    if redirect_url:
        response_data['redirect'] = redirect_url
    
    if reload:
        response_data['reload'] = True
        
    if reset_form:
        response_data['reset_form'] = True
    
    return jsonify(response_data)


def handle_request_type(success_message="", error_message="", redirect_url=None, **kwargs):
    """
    Decorator để xử lý cả AJAX và form submission thông thường
    
    Usage:
        @handle_request_type(
            success_message="Cập nhật thành công!",
            redirect_url="admin.products"
        )
        def update_product():
            # Logic xử lý
            if success:
                return True  # Trả về True nếu thành công
            else:
                return False, "Lỗi cụ thể"  # Trả về False và message nếu lỗi
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **func_kwargs):
            try:
                result = f(*args, **func_kwargs)
                
                # Xử lý kết quả từ function
                if isinstance(result, tuple):
                    success, message = result
                elif isinstance(result, bool):
                    success = result
                    message = success_message if success else error_message
                else:
                    # Nếu function trả về response object, return luôn
                    return result
                
                # Kiểm tra nếu là AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    if success:
                        return ajax_response(
                            success=True,
                            message=message or success_message,
                            redirect_url=url_for(redirect_url) if redirect_url else None,
                            **kwargs
                        )
                    else:
                        return ajax_response(
                            success=False,
                            message=message or error_message
                        )
                else:
                    # Traditional form submission
                    if success:
                        flash(message or success_message, 'success')
                        if redirect_url:
                            return redirect(url_for(redirect_url))
                    else:
                        flash(message or error_message, 'danger')
                        
                    # Return None để function gốc xử lý redirect
                    return None
                    
            except Exception as e:
                error_msg = f"Có lỗi xảy ra: {str(e)}"
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return ajax_response(success=False, message=error_msg)
                else:
                    flash(error_msg, 'danger')
                    return None
                    
        return decorated_function
    return decorator


def is_ajax_request():
    """Kiểm tra xem có phải AJAX request không"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def success_response(message, **kwargs):
    """Shortcut cho success response"""
    return ajax_response(success=True, message=message, **kwargs)


def error_response(message, **kwargs):
    """Shortcut cho error response"""
    return ajax_response(success=False, message=message, **kwargs)


def redirect_response(url, message="", **kwargs):
    """Response với redirect"""
    return ajax_response(
        success=True,
        message=message,
        redirect_url=url,
        **kwargs
    )


def reload_response(message="", **kwargs):
    """Response với reload page"""
    return ajax_response(
        success=True,
        message=message,
        reload=True,
        **kwargs
    )
