/**
 * Toast Notification System
 * Hệ thống thông báo toast hiện đại thay thế flash messages
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Tạo container cho toast notifications
        this.createContainer();
        
        // Thêm CSS styles
        this.addStyles();
        
        // Xử lý flash messages hiện có (nếu có)
        this.handleExistingFlashMessages();
    }

    createContainer() {
        // Sử dụng container có sẵn trong layout hoặc tạo mới
        this.container = document.getElementById('global-toast-container');
        
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'global-toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
        
        // Đảm bảo container có class và style đúng
        this.container.className = 'toast-container';
        
        // Áp dụng responsive positioning
        this.updateContainerPosition();
        
        // Listen for window resize để cập nhật position
        window.addEventListener('resize', () => this.updateContainerPosition());
    }

    updateContainerPosition() {
        if (!this.container) return;
        
        const isMobile = window.innerWidth <= 768;
        const isSmallMobile = window.innerWidth <= 480;
        
        if (isSmallMobile) {
            this.container.style.cssText = `
                position: fixed !important;
                top: 10px !important;
                right: 10px !important;
                left: 10px !important;
                z-index: 999999 !important;
                max-width: none !important;
                pointer-events: none !important;
            `;
        } else if (isMobile) {
            this.container.style.cssText = `
                position: fixed !important;
                top: 15px !important;
                right: 15px !important;
                left: 15px !important;
                z-index: 999999 !important;
                max-width: none !important;
                pointer-events: none !important;
            `;
        } else {
            this.container.style.cssText = `
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                z-index: 999999 !important;
                max-width: 420px !important;
                pointer-events: none !important;
            `;
        }
    }

    addStyles() {
        if (document.getElementById('toast-styles')) return;

        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                pointer-events: none;
            }

            .toast-notification {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                margin-bottom: 10px;
                padding: 16px 20px;
                border-left: 4px solid #28a745;
                position: relative;
                pointer-events: auto;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s ease-out;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.4;
                max-width: 100%;
                word-wrap: break-word;
            }

            .toast-notification.show {
                transform: translateX(0);
                opacity: 1;
            }

            .toast-notification.hide {
                transform: translateX(100%);
                opacity: 0;
            }

            .toast-notification.success {
                border-left-color: #28a745;
                background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
            }

            .toast-notification.danger,
            .toast-notification.error {
                border-left-color: #dc3545;
                background: linear-gradient(135deg, #fff8f8 0%, #ffffff 100%);
            }

            .toast-notification.warning {
                border-left-color: #ffc107;
                background: linear-gradient(135deg, #fffdf8 0%, #ffffff 100%);
            }

            .toast-notification.info {
                border-left-color: #17a2b8;
                background: linear-gradient(135deg, #f8fcff 0%, #ffffff 100%);
            }

            .toast-header {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .toast-icon {
                margin-right: 10px;
                font-size: 18px;
                width: 20px;
                text-align: center;
            }

            .toast-notification.success .toast-icon {
                color: #28a745;
            }

            .toast-notification.danger .toast-icon,
            .toast-notification.error .toast-icon {
                color: #dc3545;
            }

            .toast-notification.warning .toast-icon {
                color: #ffc107;
            }

            .toast-notification.info .toast-icon {
                color: #17a2b8;
            }

            .toast-close {
                position: absolute;
                top: 8px;
                right: 12px;
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #999;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
            }

            .toast-close:hover {
                background: rgba(0, 0, 0, 0.1);
                color: #666;
            }

            .toast-message {
                margin: 0;
                color: #333;
            }

            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 0 0 8px 8px;
                overflow: hidden;
            }

            .toast-progress-bar {
                height: 100%;
                background: currentColor;
                width: 100%;
                transform: translateX(-100%);
                transition: transform linear;
            }

            .toast-notification.success .toast-progress-bar {
                background: #28a745;
            }

            .toast-notification.danger .toast-progress-bar,
            .toast-notification.error .toast-progress-bar {
                background: #dc3545;
            }

            .toast-notification.warning .toast-progress-bar {
                background: #ffc107;
            }

            .toast-notification.info .toast-progress-bar {
                background: #17a2b8;
            }

            /* Responsive */
            @media (max-width: 480px) {
                .toast-container {
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
                
                .toast-notification {
                    margin-bottom: 8px;
                    padding: 12px 16px;
                    font-size: 13px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show(message, type = 'success', options = {}) {
        const {
            title = null,
            duration = 5000,
            showProgress = true,
            closable = true,
            onClick = null
        } = options;

        // Tạo toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;

        // Icon mapping
        const icons = {
            success: 'fa-check-circle',
            danger: 'fa-exclamation-triangle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        const icon = icons[type] || icons.info;

        // Tạo nội dung toast
        let content = '';
        
        if (title) {
            content += `
                <div class="toast-header">
                    <i class="fa ${icon} toast-icon"></i>
                    <span>${title}</span>
                </div>
            `;
        } else {
            content += `<i class="fa ${icon} toast-icon" style="float: left; margin-top: 2px;"></i>`;
        }

        content += `<div class="toast-message">${message}</div>`;

        if (closable) {
            content += `<button class="toast-close" type="button">&times;</button>`;
        }

        if (showProgress && duration > 0) {
            content += `
                <div class="toast-progress">
                    <div class="toast-progress-bar"></div>
                </div>
            `;
        }

        toast.innerHTML = content;

        // Thêm event listeners
        if (closable) {
            const closeBtn = toast.querySelector('.toast-close');
            closeBtn.addEventListener('click', () => this.hide(toast));
        }

        if (onClick) {
            toast.style.cursor = 'pointer';
            toast.addEventListener('click', onClick);
        }

        // Thêm vào container
        this.container.appendChild(toast);

        // Hiển thị với animation
        setTimeout(() => {
            toast.classList.add('show');
            
            // Bắt đầu progress bar
            if (showProgress && duration > 0) {
                const progressBar = toast.querySelector('.toast-progress-bar');
                if (progressBar) {
                    progressBar.style.transitionDuration = `${duration}ms`;
                    progressBar.style.transform = 'translateX(0)';
                }
            }
        }, 10);

        // Auto hide
        if (duration > 0) {
            setTimeout(() => {
                this.hide(toast);
            }, duration);
        }

        return toast;
    }

    hide(toast) {
        if (!toast || !toast.parentNode) return;

        toast.classList.remove('show');
        toast.classList.add('hide');

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    // Xử lý flash messages hiện có
    handleExistingFlashMessages() {
        // Đợi một chút để đảm bảo DOM đã load hoàn toàn
        setTimeout(() => {
            const flashContainer = document.querySelector('.flashes');
            if (!flashContainer) return;

            const alerts = flashContainer.querySelectorAll('.alert');
            alerts.forEach(alert => {
                const type = this.getTypeFromClasses(alert.className);
                const message = alert.textContent.replace('×', '').trim();
                
                if (message && message.length > 0) {
                    console.log('Converting flash message to toast:', message, type);
                    this.show(message, type, { duration: 5000 });
                }
            });

            // Ẩn flash container gốc
            if (alerts.length > 0) {
                flashContainer.style.display = 'none';
            }
        }, 100);
    }

    getTypeFromClasses(className) {
        if (className.includes('alert-success')) return 'success';
        if (className.includes('alert-danger')) return 'error';
        if (className.includes('alert-warning')) return 'warning';
        if (className.includes('alert-info')) return 'info';
        return 'info';
    }

    // Clear tất cả toasts
    clearAll() {
        const toasts = this.container.querySelectorAll('.toast-notification');
        toasts.forEach(toast => this.hide(toast));
    }
}

// Khởi tạo hệ thống toast
let toastSystem = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initializing Toast System...');
    
    try {
        toastSystem = new ToastNotification();
        
        // Export to global scope
        window.toast = toastSystem;
        window.showToast = (message, type, options) => toastSystem.show(message, type, options);
        
        console.log('✅ Toast System initialized successfully');
        console.log('   - window.toast:', typeof window.toast);
        console.log('   - Container:', document.getElementById('global-toast-container'));
        
        // Test toast để đảm bảo hoạt động
        setTimeout(() => {
            console.log('🧪 Testing toast system...');
            if (window.toast && typeof window.toast.success === 'function') {
                // Chỉ hiển thị toast test nếu không có flash messages và đang ở test page
                const flashContainer = document.querySelector('.flashes');
                const hasFlashMessages = flashContainer && flashContainer.querySelectorAll('.alert').length > 0;
                const isTestPage = window.location.pathname.includes('test');
                
                if (!hasFlashMessages && isTestPage) {
                    window.toast.success('🎉 Toast system đã sẵn sàng!', { duration: 3000 });
                }
            }
        }, 500);
        
    } catch (error) {
        console.error('❌ Error initializing Toast System:', error);
    }
});

// Form submission handler với toast
class AjaxFormHandler {
    constructor() {
        this.init();
    }

    init() {
        console.log('ℹ️ AjaxFormHandler.init is disabled - using simple-cart-updater instead');
        return; // Exit early to prevent any form binding
        
        document.addEventListener('DOMContentLoaded', () => {
            this.bindForms();
        });
    }

    bindForms() {
        // Tự động bind các form có class 'ajax-form'
        const ajaxForms = document.querySelectorAll('form.ajax-form');
        ajaxForms.forEach(form => {
            this.bindForm(form);
        });
    }

    bindForm(form) {
        console.log('ℹ️ AjaxFormHandler.bindForm is disabled - using simple-cart-updater instead');
        return; // Exit early to prevent duplicate event listeners
        
        form.addEventListener('submit', (e) => {
            // Nếu form có onsubmit validation, gọi nó trước
            if (form.onsubmit) {
                const validationResult = form.onsubmit(e);
                if (validationResult === false) {
                    // Validation failed, don't proceed with AJAX
                    return;
                }
            }
            
            e.preventDefault();
            this.handleSubmit(form);
        });
    }

    async handleSubmit(form) {
        console.log('ℹ️ AjaxFormHandler.handleSubmit is disabled - using simple-cart-updater instead');
        return; // Exit early to prevent duplicate handling
        
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalText = submitBtn ? submitBtn.innerHTML : '';
        
        try {
            // Show loading state
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Đang xử lý...';
            }

            const formData = new FormData(form);
            
            // Check if form has file inputs
            const hasFiles = Array.from(form.querySelectorAll('input[type="file"]')).some(input => input.files.length > 0);
            
            const fetchOptions = {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };

            const response = await fetch(form.action || window.location.href, fetchOptions);

            // Handle both JSON and HTML responses
            let data;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                // If HTML response, it might be a redirect or error page
                const text = await response.text();
                if (response.ok) {
                    // DISABLED: Prevent duplicate toasts
                    console.log('ℹ️ toast-notifications.js HTML success handler disabled - using simple-cart-updater instead');
                    // if (toastSystem) {
                    //     toastSystem.success('Thao tác thành công!');
                    // }
                    // Try to extract redirect URL from response or use current URL
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                    return;
                } else {
                    throw new Error('Server returned an error');
                }
            }

            if (data.success) {
                console.log('ℹ️ toast-notifications.js success handler disabled - using simple-cart-updater instead');
                // DISABLED: Prevent duplicate toasts
                // if (toastSystem) {
                //     toastSystem.success(data.message || 'Thao tác thành công!');
                // }
                
                // Update cart count with multiple fallback options
                if (data.data && data.data.cart_count !== undefined) {
                    console.log('🛒 Updating cart count to:', data.data.cart_count);
                    
                    // Try multiple methods in order of preference
                    let updated = false;
                    
                    // Method 1: CartUpdater (most reliable)
                    if (window.CartUpdater && window.CartUpdater.setCartCount) {
                        updated = window.CartUpdater.setCartCount(data.data.cart_count);
                        console.log('✅ Used CartUpdater.setCartCount');
                    }
                    
                    // Method 2: Global setCartCount function
                    if (!updated && window.setCartCount) {
                        updated = window.setCartCount(data.data.cart_count);
                        console.log('✅ Used window.setCartCount');
                    }
                    
                    // Method 3: setCartCountInDOM from messages.js
                    if (!updated && window.setCartCountInDOM) {
                        updated = window.setCartCountInDOM(data.data.cart_count);
                        console.log('✅ Used setCartCountInDOM');
                    }
                    
                    // Method 4: Direct DOM manipulation
                    if (!updated) {
                        console.log('🔧 Using direct DOM manipulation');
                        const cartElement = document.getElementById('header-cart-count') || 
                                          document.querySelector('.cart-quantity');
                        if (cartElement) {
                            cartElement.textContent = data.data.cart_count;
                            
                            // Simple animation
                            cartElement.style.transition = 'all 0.3s ease';
                            cartElement.style.transform = 'scale(1.2)';
                            cartElement.style.background = '#28a745';
                            cartElement.style.color = 'white';
                            cartElement.style.borderRadius = '50%';
                            cartElement.style.padding = '2px 6px';
                            
                            setTimeout(() => {
                                cartElement.style.transform = 'scale(1)';
                                cartElement.style.background = '';
                                cartElement.style.color = '';
                            }, 500);
                            
                            updated = true;
                            console.log('✅ Used direct DOM manipulation');
                        }
                    }
                    
                    // Method 5: Last resort - fetch from API
                    if (!updated) {
                        console.log('🔄 Fallback to API update');
                        setTimeout(() => {
                            if (window.updateCartCountFromAPI) {
                                window.updateCartCountFromAPI();
                            }
                        }, 100);
                    }
                }
                
                // Redirect if specified
                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                }
                
                // Reset form if specified
                if (data.reset_form) {
                    form.reset();
                }
                
                // Reload page if specified
                if (data.reload) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            } else {
                console.log('ℹ️ toast-notifications.js error handler disabled - using simple-cart-updater instead');
                // DISABLED: Prevent duplicate toasts
                // if (toastSystem) {
                //     toastSystem.error(data.message || 'Có lỗi xảy ra!');
                // }
            }

        } catch (error) {
            console.error('Ajax form error:', error);
            console.log('ℹ️ toast-notifications.js catch error handler disabled - using simple-cart-updater instead');
            // DISABLED: Prevent duplicate toasts
            // if (toastSystem) {
            //     toastSystem.error('Có lỗi xảy ra khi xử lý yêu cầu!');
            // }
        } finally {
            // Restore button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }
    }
}

// DISABLED: Ajax form handler to prevent conflicts with simple-cart-updater
// new AjaxFormHandler();
console.log('ℹ️ AjaxFormHandler disabled - using simple-cart-updater instead');
