// Messages handling JavaScript
(function() {
    'use strict';

    // Function to show toast notification
    function showToast(message, type = 'success') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast-notification');
        existingToasts.forEach(toast => toast.remove());

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification alert alert-${type} alert-dismissible fade show`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-radius: 8px;
            border: none;
            animation: slideInRight 0.5s ease-out;
        `;

        // Add icon based on type
        let icon = 'fa-check-circle';
        if (type === 'danger') icon = 'fa-exclamation-triangle';
        else if (type === 'warning') icon = 'fa-exclamation-circle';
        else if (type === 'info') icon = 'fa-info-circle';

        toast.innerHTML = `
            <i class="fa ${icon}"></i>
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;

        // Add to page
        document.body.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('fade');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 500);
            }
        }, 4000);

        // Handle close button
        const closeBtn = toast.querySelector('.close');
        closeBtn.addEventListener('click', () => {
            toast.classList.add('fade');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 500);
        });
    }

    // Function to update cart count
    function updateCartCount(count) {
        const cartElements = document.querySelectorAll('.cart-quantity');
        cartElements.forEach(element => {
            element.textContent = count;
        });
    }

    // Function to handle add to cart form submission
    function handleAddToCart(form) {
        const formData = new FormData(form);
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Đang thêm...';
        submitBtn.disabled = true;

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                if (data.cart_count !== undefined) {
                    updateCartCount(data.cart_count);
                }
            } else {
                showToast(data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Có lỗi xảy ra khi thêm sản phẩm vào giỏ hàng', 'danger');
        })
        .finally(() => {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Handle all add to cart forms
        const addToCartForms = document.querySelectorAll('form[action*="AddCart"]');
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                handleAddToCart(this);
            });
        });

        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .toast-notification {
                font-weight: 500;
                padding: 15px 20px;
            }
            
            .toast-notification i {
                margin-right: 10px;
                font-size: 16px;
            }
            
            .toast-notification .close {
                opacity: 0.7;
                font-size: 18px;
                font-weight: bold;
                line-height: 1;
                color: inherit;
                text-shadow: none;
                padding: 0;
                margin: -5px -10px -5px 10px;
            }
            
            .toast-notification .close:hover {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    });

    // Export functions for global use
    window.showToast = showToast;
    window.updateCartCount = updateCartCount;

})();
