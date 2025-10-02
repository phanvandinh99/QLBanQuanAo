/**
 * Toast Debug Script
 * Kiểm tra và debug hệ thống toast
 */

console.log('🔍 Toast Debug Script Loaded');

// Kiểm tra khi DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM Ready - Starting Toast Debug');
    
    setTimeout(() => {
        debugToastSystem();
    }, 2000);
});

function debugToastSystem() {
    console.log('🔍 === TOAST SYSTEM DEBUG ===');
    
    // 1. Kiểm tra toast system
    console.log('1. Toast System:', typeof window.toast);
    console.log('   - toastSystem:', typeof window.toastSystem);
    console.log('   - showToast:', typeof window.showToast);
    
    // 2. Kiểm tra container
    const container = document.getElementById('global-toast-container');
    console.log('2. Container:', {
        exists: !!container,
        element: container,
        styles: container ? window.getComputedStyle(container) : null
    });
    
    // 3. Kiểm tra CSS
    const cssLink = document.querySelector('link[href*="toast-animations.css"]');
    console.log('3. CSS:', {
        linkExists: !!cssLink,
        href: cssLink ? cssLink.href : null
    });
    
    // 4. Kiểm tra JavaScript files
    const jsScript = document.querySelector('script[src*="toast-notifications.js"]');
    console.log('4. JavaScript:', {
        scriptExists: !!jsScript,
        src: jsScript ? jsScript.src : null
    });
    
    // 5. Test tạo toast thủ công (chỉ khi được gọi thủ công)
    console.log('5. Toast system ready for testing...');
    console.log('   - Use testToast() function to test manually');
    console.log('   - Use createManualToast() for fallback testing');
    
    // 6. Kiểm tra errors
    console.log('6. Checking for errors...');
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.error);
    });
    
    console.log('🔍 === DEBUG COMPLETE ===');
}

function createManualToast() {
    console.log('Creating manual toast for debug...');
    
    // Tạo container nếu chưa có
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
            pointer-events: none !important;
        `;
        document.body.appendChild(container);
        console.log('Created container:', container);
    }
    
    // Tạo toast element
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: white;
        border: 1px solid #28a745;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        pointer-events: auto;
        font-family: Arial, sans-serif;
        font-size: 14px;
        color: #333;
        position: relative;
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s ease;
    `;
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center;">
            <span style="color: #28a745; margin-right: 10px;">✅</span>
            <span>🧪 Manual Debug Toast - Hệ thống hoạt động!</span>
            <button onclick="this.parentNode.parentNode.remove()" 
                    style="position: absolute; top: 8px; right: 12px; background: none; border: none; font-size: 18px; cursor: pointer; color: #999;">×</button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }, 5000);
    
    console.log('Manual toast created:', toast);
}

// Export for global access
window.debugToastSystem = debugToastSystem;
window.createManualToast = createManualToast;
