/**
 * Cart Count Updater - Simple and reliable cart count management
 */

// Global cart updater object
window.CartUpdater = {
    
    /**
     * Update cart count by fetching from server
     */
    updateCartCount: function() {
        console.log('🛒 Updating cart count...');
        
        fetch('/api/cart-count')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.setCartCount(data.cart_count);
                    console.log('✅ Cart count updated to:', data.cart_count);
                } else {
                    console.error('❌ Failed to get cart count:', data.error);
                }
            })
            .catch(error => {
                console.error('❌ Error fetching cart count:', error);
            });
    },
    
    /**
     * Set cart count in the UI
     */
    setCartCount: function(count) {
        // Find cart count element by ID first
        let cartElement = document.getElementById('header-cart-count');
        
        // Fallback to class selector
        if (!cartElement) {
            cartElement = document.querySelector('.cart-quantity');
        }
        
        // Fallback to any sup element in cart link
        if (!cartElement) {
            const cartLink = document.querySelector('a[href*="cart"]');
            if (cartLink) {
                cartElement = cartLink.querySelector('sup');
            }
        }
        
        if (cartElement) {
            const oldValue = cartElement.textContent.trim();
            cartElement.textContent = count;
            
            // Add visual feedback if count changed
            if (oldValue !== count.toString()) {
                this.animateCartUpdate(cartElement);
            }
            
            console.log('🎯 Cart count set from "' + oldValue + '" to "' + count + '"');
            return true;
        } else {
            console.error('❌ Cart count element not found!');
            return false;
        }
    },
    
    /**
     * Add visual animation to cart count update
     */
    animateCartUpdate: function(element) {
        // Save original styles
        const originalTransform = element.style.transform;
        const originalBackground = element.style.background;
        const originalColor = element.style.color;
        const originalBorderRadius = element.style.borderRadius;
        const originalPadding = element.style.padding;
        
        // Apply animation styles
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.2)';
        element.style.background = '#28a745';
        element.style.color = 'white';
        element.style.borderRadius = '50%';
        element.style.padding = '2px 6px';
        
        // Reset after animation
        setTimeout(() => {
            element.style.transform = originalTransform;
            element.style.background = originalBackground;
            element.style.color = originalColor;
            element.style.borderRadius = originalBorderRadius;
            element.style.padding = originalPadding;
        }, 600);
    },
    
    /**
     * Initialize cart updater
     */
    init: function() {
        console.log('🚀 Cart Updater initialized');
        
        // Update cart count on page load
        this.updateCartCount();
        
        // Make functions globally available
        window.updateCartCount = () => this.updateCartCount();
        window.setCartCount = (count) => this.setCartCount(count);
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    CartUpdater.init();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading
} else {
    // DOM is already loaded
    CartUpdater.init();
}
