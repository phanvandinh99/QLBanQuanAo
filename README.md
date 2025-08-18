
# Lập trình web bán hàng điện thoại sử dụng Flask!
Link website: 
- Giao diện người dùng: [https://thuctapcongnhan2020.herokuapp.com/](https://thuctapcongnhan2020.herokuapp.com/)
- Giao diện admin: [https://thuctapcongnhan2020.herokuapp.com/admin](https://thuctapcongnhan2020.herokuapp.com/admin)

- Tên đề tài : **Website bán hàng điện thoại.**
- Ngôn ngữ backend: [Flask-Python](https://flask.palletsprojects.com/en/1.1.x/)
- Cơ sở dữ liệu: MySQL.

## Mục lục:
1.[Hướng dẫn cài đặt](#p1)

2.[Các chức năng chính của chương trình](#p2)

3.[Cấu trúc thư mục chương trình](#p3)

4.[Tài liệu tham khảo](#p4)

<a id="p1"></a> 
# Hướng dẫn cài đặt:
1. Tải source code:

2. Cài đặt python : [Python 3.8](https://www.python.org/downloads/release/python-380/)

3. Download database: [here](database/myshop.sql)

4. Cài đặt môi trường thư viện tự động sử dụng tệp requirements.txt

```shell
pip install -r requirements.txt
```

5. Khởi chạy chương trình:
```shell
python run.py
```
7. Truy cập trang admin: thêm **/admin** sau tên miền.
6. Tài khoản đăng nhập trang admin:  Tai khoan admin: [viethoang@gmail.com](viethoang123@gmail.com) ,password: viethoang123

<a id="p2"></a> 
# Các chức năng chính của chương trình.
Được đặc tả qua tài liệu Usecase tổng quát:
<div align='center'>
  <img src='images/use_case.png'>
</div>

- Giao diện chính:

![alt tag](images/GUIUser.png)

![alt tag](images/GUIAdmin.png)

<a id="p3"></a> 
# Cấu trúc thư mục chương trình
```
$ Cấu trúc thư mục
.
├── shop
│   ├── admin
│   └── carts
│   └── customers
│   └── products
│   └── static
│   └── template
│   └── __init__.py
├── images
│   ├── use_case.png
│   ├── GUIAdmin.png
│   ├── GUIUser.png
├── database
│   ├── myshop.sql
└── requirements.txt
└── README.md
└── run.py

```

<a id="p4"></a> 
# Tài liệu tham khảo

 1. Template : [https://easetemplate.com/downloads/online-mobile-store-shopping-website-template/](https://easetemplate.com/downloads/online-mobile-store-shopping-website-template/)
2. Youtube: [https://www.youtube.com/watch?v=o9TwipumGoU&list=PLYPlvTh05MsxJja9bzQCSTDu4hnEv5N](https://www.youtube.com/watch?v=o9TwipumGoU&list=PLYPlvTh05MsxJja9bzQCSTDu4hnEv5N_u&index=1)
