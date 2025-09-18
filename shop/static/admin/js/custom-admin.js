/**
 * Custom Admin JavaScript - Belluni Mobile Store
 * Modern admin interface enhancements
 */

// Global variables
let currentTheme = localStorage.getItem('admin-theme') || 'light';
let notificationCount = 0;

// Initialize when document is ready
$(document).ready(function() {
    initializeTheme();
    initializeTooltips();
    initializePopovers();
    initializeSearch();
    initializeNotifications();
    initializeDataTables();
    initializeAnimations();
});

// ===== THEME MANAGEMENT =====
function initializeTheme() {
    if (currentTheme === 'dark') {
        enableDarkMode();
    }

    $('#theme-toggle').on('click', function(e) {
        e.preventDefault();
        toggleTheme();
    });
}

function toggleTheme() {
    if (currentTheme === 'light') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    $('body').addClass('dark-mode');
    $('#theme-toggle i').removeClass('fa-moon').addClass('fa-sun');
    currentTheme = 'dark';
    localStorage.setItem('admin-theme', 'dark');

    // Update charts if they exist
    updateChartThemes('dark');
}

function disableDarkMode() {
    $('body').removeClass('dark-mode');
    $('#theme-toggle i').removeClass('fa-sun').addClass('fa-moon');
    currentTheme = 'light';
    localStorage.setItem('admin-theme', 'light');

    // Update charts if they exist
    updateChartThemes('light');
}

function updateChartThemes(theme) {
    // Update Chart.js themes if charts exist
    if (typeof Chart !== 'undefined') {
        Chart.helpers.each(Chart.instances, function(instance) {
            if (theme === 'dark') {
                instance.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
                instance.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
            } else {
                instance.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
                instance.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';
            }
            instance.update();
        });
    }
}

// ===== TOOLTIPS AND POPOVERS =====
function initializeTooltips() {
    $('[data-toggle="tooltip"]').tooltip({
        placement: 'top',
        delay: { show: 300, hide: 100 }
    });
}

function initializePopovers() {
    $('[data-toggle="popover"]').popover({
        trigger: 'hover',
        placement: 'top'
    });
}

// ===== GLOBAL SEARCH =====
function initializeSearch() {
    const searchInput = $('#global-search-input');
    const searchResults = $('#global-search-results');

    let searchTimeout;

    searchInput.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();

        if (query.length < 2) {
            hideSearchResults();
            return;
        }

        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });

    // Hide search results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#global-search').length) {
            hideSearchResults();
        }
    });
}

function performSearch(query) {
    // Mock search results - replace with actual API call
    const mockResults = [
        { type: 'product', title: 'iPhone 15 Pro', url: '/admin/products/1' },
        { type: 'order', title: 'Đơn hàng #12345', url: '/admin/orders/12345' },
        { type: 'customer', title: 'Nguyễn Văn A', url: '/admin/customers/1' }
    ];

    displaySearchResults(mockResults);
}

function displaySearchResults(results) {
    let html = '<div class="search-results">';

    results.forEach(result => {
        const iconClass = getIconForType(result.type);
        html += `
            <div class="search-result-item" onclick="navigateTo('${result.url}')">
                <i class="${iconClass} mr-2"></i>
                <span>${result.title}</span>
                <small class="text-muted ml-2">${result.type}</small>
            </div>
        `;
    });

    html += '</div>';

    $('#global-search').append(html);
}

function hideSearchResults() {
    $('.search-results').remove();
}

function getIconForType(type) {
    const icons = {
        'product': 'fas fa-box',
        'order': 'fas fa-shopping-cart',
        'customer': 'fas fa-user',
        'category': 'fas fa-tag',
        'brand': 'fas fa-building'
    };
    return icons[type] || 'fas fa-search';
}

function navigateTo(url) {
    window.location.href = url;
}

// ===== NOTIFICATIONS =====
function initializeNotifications() {
    // Mock notifications - replace with actual API call
    loadNotifications();

    // Auto refresh notifications every 30 seconds
    setInterval(loadNotifications, 30000);
}

function loadNotifications() {
    // Mock notification data
    const notifications = [
        {
            id: 1,
            title: 'Đơn hàng mới',
            message: 'Đơn hàng #12345 vừa được đặt',
            time: '5 phút trước',
            unread: true
        },
        {
            id: 2,
            title: 'Sản phẩm hết hàng',
            message: 'iPhone 15 Pro chỉ còn 2 sản phẩm',
            time: '10 phút trước',
            unread: true
        }
    ];

    updateNotificationBadge(notifications.length);
    renderNotificationMenu(notifications);
}

function updateNotificationBadge(count) {
    const badge = $('#notification-count');
    if (count > 0) {
        badge.text(count).show();
    } else {
        badge.hide();
    }
}

function renderNotificationMenu(notifications) {
    const menu = $('#notification-menu');

    if (notifications.length === 0) {
        menu.html('<span class="dropdown-item dropdown-header">Không có thông báo</span>');
        return;
    }

    let html = '<span class="dropdown-item dropdown-header">Thông báo</span>';
    html += '<div class="dropdown-divider"></div>';

    notifications.forEach(notification => {
        const unreadClass = notification.unread ? 'font-weight-bold' : '';
        html += `
            <a href="#" class="dropdown-item ${unreadClass}" onclick="markAsRead(${notification.id})">
                <i class="fas fa-bell mr-2"></i>
                <div>
                    <div class="text-truncate">${notification.title}</div>
                    <small class="text-muted">${notification.message}</small>
                    <div class="text-muted text-sm">${notification.time}</div>
                </div>
            </a>
            <div class="dropdown-divider"></div>
        `;
    });

    html += '<a href="#" class="dropdown-item dropdown-footer">Xem tất cả thông báo</a>';
    menu.html(html);
}

function markAsRead(notificationId) {
    // Mark notification as read - replace with actual API call
    console.log('Marked notification', notificationId, 'as read');
}

// ===== DATA TABLES =====
function initializeDataTables() {
    // Enhanced DataTables configuration
    $('.data-table').each(function() {
        const table = $(this).DataTable({
            responsive: true,
            autoWidth: false,
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.25/i18n/Vietnamese.json"
            },
            initComplete: function() {
                // Add search input styling
                $('.dataTables_filter input').addClass('form-control form-control-sm');
                $('.dataTables_length select').addClass('form-control form-control-sm');
            }
        });
    });
}

// ===== ANIMATIONS =====
function initializeAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });

    // Add loading animations
    $('.loading-trigger').on('click', function() {
        const target = $(this).data('loading-target') || $(this);
        target.addClass('loading');

        // Remove loading after 2 seconds (replace with actual loading logic)
        setTimeout(() => {
            target.removeClass('loading');
        }, 2000);
    });
}

// ===== UTILITY FUNCTIONS =====

// Show success message
function showSuccessMessage(message, title = 'Thành công!') {
    Swal.fire({
        icon: 'success',
        title: title,
        text: message,
        timer: 3000,
        showConfirmButton: false,
        toast: true,
        position: 'top-end'
    });
}

// Show error message
function showErrorMessage(message, title = 'Lỗi!') {
    Swal.fire({
        icon: 'error',
        title: title,
        text: message,
        timer: 5000,
        showConfirmButton: true
    });
}

// Show confirmation dialog
function showConfirmDialog(message, callback, title = 'Xác nhận') {
    Swal.fire({
        title: title,
        text: message,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#007bff',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Đồng ý',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed && callback) {
            callback();
        }
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccessMessage('Đã sao chép vào clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccessMessage('Đã sao chép vào clipboard!');
    });
}

// ===== FORM ENHANCEMENTS =====

// Auto-submit forms with loading state
$('.auto-submit').on('submit', function(e) {
    const form = $(this);
    const submitBtn = form.find('[type="submit"]');

    submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i>Đang xử lý...');

    // Re-enable after 5 seconds if no response
    setTimeout(() => {
        submitBtn.prop('disabled', false).html(submitBtn.data('original-text') || 'Submit');
    }, 5000);
});

// Auto-resize textareas
$('textarea').each(function() {
    this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
}).on('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// ===== KEYBOARD SHORTCUTS =====
$(document).on('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.keyCode === 75) {
        e.preventDefault();
        $('#global-search-input').focus();
    }

    // Escape: Close modals and dropdowns
    if (e.keyCode === 27) {
        $('.modal').modal('hide');
        $('.dropdown-menu').removeClass('show');
        hideSearchResults();
    }
});

// ===== RESPONSIVE HANDLING =====
function handleResponsive() {
    const width = $(window).width();

    if (width < 768) {
        // Mobile optimizations
        $('.main-sidebar').addClass('mobile-sidebar');
        $('.navbar-nav .nav-link span').hide();
    } else {
        // Desktop optimizations
        $('.main-sidebar').removeClass('mobile-sidebar');
        $('.navbar-nav .nav-link span').show();
    }
}

$(window).on('resize', handleResponsive);
handleResponsive(); // Initial call

// ===== PERFORMANCE MONITORING =====
function initializePerformanceMonitoring() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log('Page load time:', loadTime.toFixed(2), 'ms');

        // Send to analytics if available
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_load_time', {
                value: Math.round(loadTime)
            });
        }
    });

    // Monitor AJAX requests
    $(document).ajaxStart(function() {
        $('#global-loading').show();
    });

    $(document).ajaxStop(function() {
        $('#global-loading').hide();
    });
}

// ===== CHART INITIALIZATION =====
function initializeCharts() {
    // Sales chart
    if ($('#sales-chart').length) {
        const ctx = document.getElementById('sales-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Doanh thu',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // Orders chart
    if ($('#orders-chart').length) {
        const ctx = document.getElementById('orders-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
                datasets: [{
                    label: 'Đơn hàng',
                    data: [12, 19, 15, 25, 22, 30, 18],
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// ===== INITIALIZE EVERYTHING =====
$(document).ready(function() {
    initializeTheme();
    initializeTooltips();
    initializePopovers();
    initializeSearch();
    initializeNotifications();
    initializeDataTables();
    initializeAnimations();
    initializePerformanceMonitoring();
    initializeCharts();
});

// Export functions for global use
window.AdminUtils = {
    showSuccessMessage,
    showErrorMessage,
    showConfirmDialog,
    formatCurrency,
    formatDate,
    copyToClipboard
};
