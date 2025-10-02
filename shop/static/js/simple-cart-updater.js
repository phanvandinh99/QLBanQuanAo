/**
 * Simple Cart Updater - Đảm bảo cart count luôn cập nhật
 * ANTI-DUPLICATE SYSTEM: Ngăn chặn hoàn toàn duplicate notifications
 */

(function() {
    'use strict';

    // Global flag to prevent duplicate toasts
    window.CART_OPERATION_IN_PROGRESS = false;
    
    // Global toast queue to prevent duplicates
    window.TOAST_QUEUE = [];
    
    // Function to create toast directly (fallback)
    function createDirectToast(message, type) {
        console.log('🔧 Creating direct toast:', message, type);
        
        // Create toast container if not exists
        let container = document.getElementById('global-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'global-toast-container';
            container.style.cssText = `
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                z-index: 999999 !important;
                max-width: 420px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        const bgColor = type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#fff3cd';
        const borderColor = type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#ffc107';
        const textColor = type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#856404';
        const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️';
        
        toast.style.cssText = `
            background: ${bgColor};
            border: 1px solid ${borderColor};
            border-left: 4px solid ${borderColor};
            color: ${textColor};
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.4;
            max-width: 400px;
            word-wrap: break-word;
            pointer-events: auto;
            cursor: pointer;
            animation: slideInRight 0.3s ease-out;
        `;
        
        toast.innerHTML = `${icon} ${message}`;
        
        // Add click to dismiss
        toast.onclick = () => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        };
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
        
        container.appendChild(toast);
        
        // Add CSS animations if not already added
        if (!document.getElementById('direct-toast-animations')) {
            const style = document.createElement('style');
            style.id = 'direct-toast-animations';
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
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        console.log('✅ Direct toast created and shown');
    }

    // Function to show toast with duplicate prevention
    function showUniqueToast(message, type) {
        // For cart operations, allow duplicates but with shorter time window
        const messageKey = `${type}:${message}`;
        const now = Date.now();
        
        // Clean old messages from queue (older than 1 second for cart operations)
        const timeWindow = message.includes('giỏ hàng') ? 1000 : 3000;
        window.TOAST_QUEUE = window.TOAST_QUEUE.filter(item => now - item.timestamp < timeWindow);
        
        // Check if this message was recently shown
        const isDuplicate = window.TOAST_QUEUE.some(item => item.key === messageKey);
        
        if (isDuplicate) {
            console.log('🚫 Duplicate toast prevented:', message, '(within', timeWindow, 'ms)');
            return false;
        }
        
        // Add to queue
        window.TOAST_QUEUE.push({
            key: messageKey,
            timestamp: now
        });
        
        // Show toast with multiple fallbacks
        setTimeout(() => {
            console.log('🔍 Attempting to show toast:', message, 'type:', type);
            console.log('🔍 Available toast systems:');
            console.log('  - window.toast:', typeof window.toast);
            console.log('  - window.showToast:', typeof window.showToast);
            
            let toastShown = false;
            
            // Method 1: Try window.toast system
            if (window.toast && typeof window.toast[type] === 'function') {
                try {
                    window.toast[type](message);
                    console.log('✅ Toast shown via window.toast.' + type);
                    toastShown = true;
                } catch (error) {
                    console.error('❌ Error with window.toast.' + type + ':', error);
                }
            }
            
            // Method 2: Try window.showToast
            if (!toastShown && window.showToast && typeof window.showToast === 'function') {
                try {
                    window.showToast(message, type === 'error' ? 'danger' : type);
                    console.log('✅ Toast shown via window.showToast');
                    toastShown = true;
                } catch (error) {
                    console.error('❌ Error with window.showToast:', error);
                }
            }
            
            // Method 3: Direct toast creation as fallback
            if (!toastShown) {
                console.log('🔧 Creating toast directly as fallback');
                createDirectToast(message, type);
                toastShown = true;
            }
            
            // Method 4: Force create toast if all else fails
            if (!toastShown) {
                console.error('❌ All toast methods failed, forcing direct creation');
                try {
                    // Force create a simple toast
                    const forceToast = document.createElement('div');
                    forceToast.style.cssText = `
                        position: fixed !important;
                        top: 20px !important;
                        right: 20px !important;
                        z-index: 999999 !important;
                        background: ${type === 'success' ? '#d4edda' : '#f8d7da'} !important;
                        border: 2px solid ${type === 'success' ? '#28a745' : '#dc3545'} !important;
                        color: ${type === 'success' ? '#155724' : '#721c24'} !important;
                        padding: 15px 20px !important;
                        border-radius: 8px !important;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
                        font-size: 16px !important;
                        font-weight: bold !important;
                        max-width: 400px !important;
                        word-wrap: break-word !important;
                        animation: slideInRight 0.3s ease-out !important;
                    `;
                    forceToast.innerHTML = `${type === 'success' ? '✅' : '❌'} ${message}`;
                    
                    document.body.appendChild(forceToast);
                    
                    // Auto remove
                    setTimeout(() => {
                        if (forceToast.parentNode) {
                            forceToast.remove();
                        }
                    }, 5000);
                    
                    console.log('✅ Force toast created successfully');
                    toastShown = true;
                } catch (forceError) {
                    console.error('❌ Even force toast failed:', forceError);
                    // Absolutely last resort: alert
                    alert(message);
                }
            }
        }, 50);
        
        return true;
    }

    // Function to update cart count in header
    function updateCartCountInHeader(newCount) {
        console.log('🛒 Updating cart count to:', newCount);
        
        // Find cart element with multiple fallbacks
        let cartElement = document.getElementById('header-cart-count');
        if (!cartElement) {
            cartElement = document.querySelector('.cart-quantity');
        }
        if (!cartElement) {
            const cartLink = document.querySelector('a[href*="cart"]');
            if (cartLink) {
                cartElement = cartLink.querySelector('sup');
            }
        }

        if (cartElement) {
            const oldValue = cartElement.textContent.trim();
            cartElement.textContent = newCount;
            
            console.log('✅ Cart count updated from "' + oldValue + '" to "' + newCount + '"');
            
            // Add visual animation
            cartElement.style.transition = 'all 0.3s ease';
            cartElement.style.transform = 'scale(1.3)';
            cartElement.style.background = '#28a745';
            cartElement.style.color = 'white';
            cartElement.style.borderRadius = '50%';
            cartElement.style.padding = '2px 6px';
            
            setTimeout(() => {
                cartElement.style.transform = 'scale(1)';
                cartElement.style.background = '';
                cartElement.style.color = '';
            }, 600);
            
            return true;
        } else {
            console.error('❌ Cart element not found for update');
            return false;
        }
    }

    // Function to fetch cart count from API (only updates count, no toast)
    function fetchCartCountFromAPI() {
        console.log('📡 Fetching cart count from API...');
        
        return fetch('/api/cart-count')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('📡 API returned cart count:', data.cart_count);
                    updateCartCountInHeader(data.cart_count);
                    return data.cart_count;
                } else {
                    console.error('❌ API error:', data.error);
                    return null;
                }
            })
            .catch(error => {
                console.error('❌ Fetch error:', error);
                return null;
            });
    }

    // Function to handle add to cart form submission
    function handleAddToCartForm(form) {
        // Check if form already has our handler to prevent duplicates
        if (form.hasAttribute('data-cart-handler-attached')) {
            console.log('🔄 Form already has cart handler, skipping...');
            return;
        }
        
        console.log('🛒 Setting up add-to-cart form handler');
        
        // Mark form as handled
        form.setAttribute('data-cart-handler-attached', 'true');
        
        // Remove any existing event listeners by cloning the form
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        form = newForm; // Update reference
        
        // Mark the new form as handled
        form.setAttribute('data-cart-handler-attached', 'true');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevent multiple simultaneous operations
            if (window.CART_OPERATION_IN_PROGRESS) {
                console.log('🚫 Cart operation already in progress, ignoring...');
                return false;
            }
            
            // Check if this specific form is already being processed
            if (form.hasAttribute('data-processing')) {
                console.log('🚫 This form is already being processed, ignoring...');
                return false;
            }
            
            window.CART_OPERATION_IN_PROGRESS = true;
            form.setAttribute('data-processing', 'true');
            console.log('🛒 Add to cart form submitted (simple-cart-updater)');
            
            const formData = new FormData(form);
            const data = new URLSearchParams();
            for (let [key, value] of formData) {
                data.append(key, value);
            }
            
            console.log('📤 Sending cart data:', data.toString());
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.innerHTML = '⏳ Đang thêm...';
                submitBtn.disabled = true;
            }
            
            fetch('/addcart', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: data
            })
            .then(response => {
                console.log('📥 Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('📥 Response data:', data);
                
                // Reset button and flags
                if (submitBtn) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
                window.CART_OPERATION_IN_PROGRESS = false;
                form.removeAttribute('data-processing');
                
                if (data.success) {
                    // Show cart success toast (bypass duplicate check)
                    console.log('✅ Cart operation successful, showing toast:', data.message);
                    
                    // For cart operations, show toast directly without duplicate check
                    let toastShown = false;
                    
                    // Try original toast system first
                    if (window.toast && window.toast.success && typeof window.toast.success === 'function') {
                        try {
                            // Find and call original method if it exists
                            const originalToast = window.toast.success.originalMethod || window.toast.success;
                            if (typeof originalToast === 'function') {
                                originalToast.call(window.toast, data.message);
                                console.log('✅ Cart toast shown via original toast.success');
                                toastShown = true;
                            }
                        } catch (error) {
                            console.error('❌ Error with original toast.success:', error);
                        }
                    }
                    
                    // Fallback to direct toast creation
                    if (!toastShown) {
                        console.log('🔧 Using direct toast creation for cart operation');
                        createDirectToast(data.message, 'success');
                        toastShown = true;
                    }
                    
                    console.log('🔍 Cart toast display result:', toastShown);
                    
                    // Update cart count - check both data.cart_count and data.data.cart_count
                    console.log('🔍 Debug response structure:', JSON.stringify(data, null, 2));
                    
                    let cartCount = null;
                    if (data.cart_count !== undefined && data.cart_count !== null) {
                        cartCount = data.cart_count;
                        console.log('📊 Using data.cart_count:', cartCount);
                    } else if (data.data && data.data.cart_count !== undefined && data.data.cart_count !== null) {
                        cartCount = data.data.cart_count;
                        console.log('📊 Using data.data.cart_count:', cartCount);
                    } else {
                        console.log('🔍 Cart count not found in response:');
                        console.log('  - data.cart_count:', data.cart_count);
                        console.log('  - data.data:', data.data);
                    }
                    
                    if (cartCount !== null && cartCount !== undefined) {
                        updateCartCountInHeader(cartCount);
                    } else {
                        // Fallback: fetch from API
                        console.log('🔄 No cart_count in response, fetching from API...');
                        fetchCartCountFromAPI();
                    }
                } else {
                    // Show unique error toast
                    showUniqueToast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Add to cart error:', error);
                
                // Reset button and flags
                if (submitBtn) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
                window.CART_OPERATION_IN_PROGRESS = false;
                form.removeAttribute('data-processing');
                
                // Show unique error toast
                showUniqueToast('Có lỗi xảy ra khi thêm sản phẩm', 'error');
            });
        });
    }

    // Initialize when DOM is ready
    function init() {
        console.log('🚀 Simple Cart Updater initializing...');
        
        // Find all add-to-cart forms
        const cartForms = document.querySelectorAll('form[action*="addcart"], form.ajax-form');
        console.log('🔍 Found', cartForms.length, 'cart forms');
        
        cartForms.forEach((form, index) => {
            console.log('🔧 Setting up form', index + 1);
            handleAddToCartForm(form);
        });
        
        // Also look for forms that might be added dynamically
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const newForms = node.querySelectorAll ? 
                            node.querySelectorAll('form[action*="addcart"], form.ajax-form') : [];
                        newForms.forEach(form => {
                            console.log('🆕 Setting up dynamically added form');
                            handleAddToCartForm(form);
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Make functions globally available
        window.updateCartCountInHeader = updateCartCountInHeader;
        window.fetchCartCountFromAPI = fetchCartCountFromAPI;
        window.showUniqueToast = showUniqueToast;
        
        // Override other toast functions to prevent duplicates (only once)
        if (!window.TOAST_FUNCTIONS_OVERRIDDEN) {
            window.TOAST_FUNCTIONS_OVERRIDDEN = true;
            
            const originalShowToast = window.showToast;
            window.showToast = function(message, type) {
                console.log('🔄 Redirecting showToast to showUniqueToast');
                return showUniqueToast(message, type);
            };
            
            // Override window.toast methods if they exist
            setTimeout(() => {
                if (window.toast) {
                    const originalToast = window.toast;
                    ['success', 'error', 'warning', 'info'].forEach(method => {
                        if (originalToast[method]) {
                            const originalMethod = originalToast[method];
                            originalToast[method] = function(message, options) {
                                console.log(`🔄 Redirecting toast.${method} to showUniqueToast`);
                                // For cart operations, bypass duplicate check by calling original method
                                if (message && message.includes('giỏ hàng')) {
                                    console.log('🛒 Cart operation detected, calling original toast method');
                                    return originalMethod.call(this, message, options);
                                }
                                return showUniqueToast(message, method);
                            };
                            // Store reference to original method
                            originalToast[method].originalMethod = originalMethod;
                        }
                    });
                    console.log('✅ Toast function overrides applied');
                }
            }, 100); // Small delay to ensure toast system is loaded
        }
        
        console.log('✅ Simple Cart Updater initialized with anti-duplicate system');
        
        // Expose functions globally for debugging
        window.showUniqueToast = showUniqueToast;
        window.createDirectToast = createDirectToast;
        
        // Add test function for debugging
        window.testToast = function() {
            console.log('🧪 Testing toast manually...');
            showUniqueToast('🧪 Test toast - hệ thống hoạt động bình thường!', 'success');
        };
        
        // Add test function for cart toast specifically
        window.testCartToast = function() {
            console.log('🧪 Testing cart toast manually...');
            createDirectToast('🛒 Test: Sản phẩm đã được thêm vào giỏ hàng!', 'success');
        };
        
        console.log('🌐 Toast functions exposed globally');
        console.log('💡 Để test toast, gõ: testToast() hoặc testCartToast() trong console');
        
        // Test toast on initialization (disabled in production)
        // setTimeout(() => {
        //     console.log('🧪 Testing toast system...');
        //     showUniqueToast('🧪 Toast system đã sẵn sàng!', 'success');
        // }, 1000);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
