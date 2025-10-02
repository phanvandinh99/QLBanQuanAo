# Hệ Thống Toast Notification

Hệ thống thông báo toast hiện đại thay thế flash messages truyền thống, cho phép hiển thị thông báo tức thì mà không cần reload trang.

## 🚀 Tính Năng

- ✅ **Thông báo tức thì**: Hiển thị ngay lập tức mà không cần reload trang
- 🎨 **Giao diện đẹp**: Toast notifications với animations mượt mà
- 📱 **Responsive**: Tương thích với mọi kích thước màn hình
- 🔄 **AJAX Support**: Tự động xử lý form submissions với AJAX
- 🎯 **Vị trí linh hoạt**: Hiển thị ở góc phải màn hình
- ⏱️ **Auto dismiss**: Tự động ẩn sau thời gian nhất định
- 🌙 **Dark mode**: Hỗ trợ chế độ tối
- ♿ **Accessibility**: Tuân thủ các tiêu chuẩn accessibility

## 📦 Cài Đặt

Hệ thống đã được tích hợp sẵn vào ứng dụng. Các file liên quan:

```
shop/static/js/toast-notifications.js    # JavaScript core
shop/static/css/toast-animations.css     # CSS styling & animations
shop/utils/response_utils.py             # Python utilities
shop/templates/_messages.html            # Template integration
```

## 🎯 Sử Dụng

### 1. JavaScript API

```javascript
// Hiển thị toast thành công
toast.success('Thao tác thành công!');

// Hiển thị toast lỗi
toast.error('Có lỗi xảy ra!');

// Hiển thị toast cảnh báo
toast.warning('Cảnh báo!');

// Hiển thị toast thông tin
toast.info('Thông tin quan trọng');

// Tùy chỉnh options
toast.show('Custom message', 'success', {
    title: 'Tiêu đề',
    duration: 3000,
    showProgress: true,
    closable: true,
    onClick: () => console.log('Clicked!')
});

// Xóa tất cả toasts
toast.clearAll();
```

### 2. AJAX Forms

Thêm class `ajax-form` vào form để tự động sử dụng AJAX:

```html
<form class="ajax-form" method="POST" action="/your-endpoint">
    <input type="text" name="data" required>
    <button type="submit">
        <i class="fa fa-save"></i> Lưu
    </button>
</form>
```

### 3. Python Backend

```python
from shop.utils.response_utils import success_response, error_response, is_ajax_request

@app.route('/your-endpoint', methods=['POST'])
def your_function():
    try:
        # Xử lý logic
        
        if is_ajax_request():
            return success_response('Thành công!', reset_form=True)
        else:
            flash('Thành công!', 'success')
            return redirect(url_for('some_page'))
            
    except Exception as e:
        if is_ajax_request():
            return error_response(f'Lỗi: {str(e)}')
        else:
            flash(f'Lỗi: {str(e)}', 'danger')
            return redirect(url_for('some_page'))
```

### 4. Response Options

```python
# Success với redirect
success_response('Thành công!', redirect_url=url_for('home'))

# Success với reload page
success_response('Thành công!', reload=True)

# Success với reset form
success_response('Thành công!', reset_form=True)

# Error response
error_response('Có lỗi xảy ra!')

# Custom response
ajax_response(
    success=True,
    message='Custom message',
    data={'extra': 'data'},
    redirect_url='/custom-redirect'
)
```

## 🎨 Customization

### CSS Variables

Bạn có thể tùy chỉnh màu sắc và styling bằng cách override CSS:

```css
.toast-notification.success {
    border-left-color: #your-color;
    background: linear-gradient(135deg, #your-bg1 0%, #your-bg2 100%);
}
```

### Animation Timing

```css
.toast-notification {
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

### Position

```css
.toast-container {
    top: 20px;
    right: 20px;
    /* Hoặc thay đổi vị trí khác */
}
```

## 📱 Responsive Design

Hệ thống tự động điều chỉnh cho các màn hình khác nhau:

- **Desktop**: Toast ở góc phải, width tối đa 420px
- **Tablet**: Điều chỉnh padding và font size
- **Mobile**: Full width với margins nhỏ hơn

## ♿ Accessibility

- Hỗ trợ keyboard navigation
- Screen reader friendly
- High contrast mode support
- Reduced motion support cho người dùng nhạy cảm với animation

## 🧪 Testing

Truy cập `/test-toast` để test hệ thống:

```
http://localhost:5000/test-toast
```

Trang test bao gồm:
- Manual toast buttons
- AJAX form test
- Traditional flash message comparison

## 🔧 Troubleshooting

### Toast không hiển thị

1. Kiểm tra JavaScript console có lỗi không
2. Đảm bảo `toast-notifications.js` được load
3. Kiểm tra CSS `toast-animations.css` được load

### AJAX form không hoạt động

1. Đảm bảo form có class `ajax-form`
2. Kiểm tra backend trả về JSON response đúng format
3. Kiểm tra `X-Requested-With` header

### Styling không đúng

1. Kiểm tra CSS conflicts
2. Đảm bảo `toast-animations.css` được load sau các CSS khác
3. Kiểm tra z-index conflicts

## 📈 Performance

- **Lightweight**: ~15KB JavaScript + CSS
- **Efficient**: Sử dụng CSS transforms cho animations
- **Memory safe**: Tự động cleanup DOM elements
- **Throttled**: Giới hạn số lượng toast hiển thị cùng lúc

## 🔄 Migration từ Flash Messages

### Trước (Flash Messages)
```python
flash('Message', 'success')
return redirect(url_for('page'))
```

### Sau (Toast System)
```python
if is_ajax_request():
    return success_response('Message')
else:
    flash('Message', 'success')
    return redirect(url_for('page'))
```

## 🎯 Best Practices

1. **Consistent messaging**: Sử dụng tone nhất quán cho messages
2. **Appropriate duration**: 3-5s cho thông tin, 7-10s cho lỗi quan trọng
3. **Clear actions**: Cung cấp hướng dẫn rõ ràng trong error messages
4. **Progressive enhancement**: Luôn có fallback cho non-JS users
5. **User feedback**: Hiển thị loading states trong forms

## 🚀 Future Enhancements

- [ ] Sound notifications
- [ ] Custom toast templates
- [ ] Batch notifications
- [ ] Notification history
- [ ] Push notifications integration
- [ ] Multi-language support
- [ ] Custom positioning options

## 📞 Support

Nếu gặp vấn đề, hãy kiểm tra:
1. Browser console logs
2. Network tab trong DevTools
3. Server logs cho AJAX requests

---

**Tác giả**: Mobile Store Development Team  
**Phiên bản**: 1.0.0  
**Cập nhật**: October 2024
