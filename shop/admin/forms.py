from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, RadioField, IntegerField, DecimalField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from shop.models import Product, Customer, Role

class RegistrationForm(FlaskForm):
    name = StringField('Tên', [validators.Length(min=4, max=25)])
    username = StringField('Tên đăng nhập', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35),
                                        validators.Email()])
    password = PasswordField('Mật khẩu', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Mật khẩu không khớp')
    ])
    confirm = PasswordField('Xác nhận mật khẩu')
    role_id = SelectField('Quyền', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Populate role choices with Vietnamese labels
        role_labels = {
            'admin': 'Quản trị viên - có toàn quyền truy cập',
            'nhanvien': 'Nhân viên - quyền hạn chế: Nhập hàng, Sản phẩm, Bài viết, Đơn hàng'
        }
        self.role_id.choices = [(role.id, role_labels.get(role.name, role.description)) for role in Role.query.all()]

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

    customer_last_name = StringField('Họ khách hàng',
                                    validators=[DataRequired(message='Vui lòng nhập họ khách hàng'),
                                              Length(min=1, max=50, message='Họ phải từ 1-50 ký tự')])

    customer_name = StringField('Tên khách hàng',
                               validators=[DataRequired(message='Vui lòng nhập tên khách hàng'),
                                         Length(min=1, max=50, message='Tên phải từ 1-50 ký tự')])

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


# ================= INVENTORY (PURCHASE) FORMS =================
class PurchaseForm(FlaskForm):
    supplier_name = StringField('Nhà cung cấp', validators=[Optional(), Length(max=120)])
    notes = TextAreaField('Ghi chú', validators=[Optional(), Length(max=1000)])


class PurchaseItemForm(FlaskForm):
    product_id = IntegerField('Mã sản phẩm', validators=[DataRequired(message='Vui lòng chọn sản phẩm')])
    quantity = IntegerField('Số lượng nhập', validators=[DataRequired(message='Vui lòng nhập số lượng'), NumberRange(min=1)])
    unit_cost = DecimalField('Giá nhập', validators=[Optional(), NumberRange(min=0)], default=0)


class SupplierForm(FlaskForm):
    name = StringField('Tên nhà cung cấp', validators=[DataRequired(), Length(max=120)])
    contact_name = StringField('Người liên hệ', validators=[Optional(), Length(max=120)])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    address = StringField('Địa chỉ', validators=[Optional(), Length(max=255)])