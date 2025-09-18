from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, RadioField, IntegerField, DecimalField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from shop.models import Product, Customer

class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),
                                        validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35),
                                        validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])

class AdminOrderForm(FlaskForm):
    """Form for admin to create orders at counter"""

    # Customer Information
    customer_phone = StringField('Số điện thoại khách hàng',
                                validators=[DataRequired(message='Vui lòng nhập số điện thoại'),
                                          Length(min=10, max=15, message='Số điện thoại phải từ 10-15 ký tự')])

    customer_name = StringField('Họ tên khách hàng',
                               validators=[DataRequired(message='Vui lòng nhập họ tên khách hàng'),
                                         Length(min=2, max=100, message='Họ tên phải từ 2-100 ký tự')])

    customer_email = StringField('Email khách hàng',
                                validators=[Optional(), Email(message='Email không hợp lệ')])

    # Payment Method
    payment_method = RadioField('Phương thức thanh toán',
                               choices=[('cash', 'Tiền mặt'),
                                       ('qr_code', 'QR Code chuyển khoản')],
                               default='cash',
                               validators=[DataRequired(message='Vui lòng chọn phương thức thanh toán')])

    # Order Notes
    notes = TextAreaField('Ghi chú đơn hàng',
                         validators=[Optional(), Length(max=500, message='Ghi chú không quá 500 ký tự')])

class AdminOrderItemForm(FlaskForm):
    """Form for adding items to admin order"""

    product_id = IntegerField('Mã sản phẩm',
                             validators=[DataRequired(message='Vui lòng chọn sản phẩm')])

    quantity = IntegerField('Số lượng',
                           validators=[DataRequired(message='Vui lòng nhập số lượng'),
                                     NumberRange(min=1, message='Số lượng phải lớn hơn 0')])

    discount = IntegerField('Giảm giá (%)',
                           validators=[Optional(), NumberRange(min=0, max=100, message='Giảm giá phải từ 0-100%')],
                           default=0)