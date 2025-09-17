
# 🛒 Website Bán Hàng Điện Thoại

Dự án website bán hàng điện thoại sử dụng **Flask** và **MySQL** với tích hợp thanh toán **VNPAY**.

## 📋 Chức năng chính

### 👤 Khách hàng
- ✅ Đăng ký/Đăng nhập tài khoản
- ✅ Duyệt sản phẩm theo danh mục
- ✅ Thêm sản phẩm vào giỏ hàng
- ✅ Thanh toán online với VNPAY
- ✅ Theo dõi đơn hàng

### 🛍️ Sản phẩm
- ✅ Hiển thị danh sách sản phẩm
- ✅ Tìm kiếm và lọc sản phẩm
- ✅ Chi tiết sản phẩm với ảnh
- ✅ Quản lý kho hàng

### 🛠️ Quản trị viên
- ✅ Quản lý sản phẩm (thêm/sửa/xóa)
- ✅ Quản lý danh mục sản phẩm
- ✅ Quản lý đơn hàng
- ✅ Quản lý khách hàng
- ✅ Thống kê báo cáo

### 💳 Thanh toán
- ✅ Tích hợp VNPAY Payment Gateway
- ✅ Thanh toán an toàn và bảo mật
- ✅ Xử lý callback và IPN tự động

## 📁 Cấu trúc thư mục

```
MobileStore/
├── shop/                    # Thư mục chính ứng dụng
│   ├── __init__.py         # File khởi tạo Flask app
│   ├── models.py           # Models database
│   ├── vnpay_utils.py      # Utilities cho VNPAY
│   ├── admin/              # Quản lý admin
│   │   ├── routes.py
│   │   └── forms.py
│   ├── carts/              # Giỏ hàng
│   │   └── routes.py
│   ├── customers/          # Khách hàng
│   │   ├── routes.py
│   │   └── forms.py
│   ├── products/           # Sản phẩm
│   │   ├── routes.py
│   │   └── forms.py
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
├── databse/                # Database files
│   └── myshop.sql
├── images/                 # Hình ảnh demo
├── venv/                   # Virtual environment (không commit)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Dependencies
├── run.py                 # File chạy ứng dụng
└── README.md              # Tài liệu này
```

## 🚀 Hướng dẫn chạy dự án

### 1. 📥 Clone dự án
```bash
Giải nén dự án
```

### 2. 🐍 Cài đặt Python
Đảm bảo **Python 3.8+** được cài đặt.

### 3. 📦 Tạo môi trường ảo
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. 📚 Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 5. 🗄️ Thiết lập database
- Import file `databse/myshop.sql` vào MySQL
- Cập nhật thông tin database trong `shop/__init__.py`

### 6. ▶️ Chạy ứng dụng
```bash
python run.py
```

### 7. 🌐 Truy cập
- **Website khách hàng:** http://localhost:5000
- **Trang admin:** http://localhost:5000/admin
- **Tài khoản admin:** viethoang@gmail.com / Abc123

## 📝 Lưu ý

- Đảm bảo MySQL đang chạy
- Cập nhật cấu hình VNPAY trong `shop/__init__.py` (VNPAY_TMN_CODE, VNPAY_HASH_SECRET...)
- Sử dụng virtual environment để tránh xung đột dependencies

## 🎯 Công nghệ sử dụng

- **Backend:** Flask (Python)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Payment:** VNPAY Gateway
- **Template Engine:** Jinja2

---