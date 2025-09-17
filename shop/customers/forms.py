from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError, RadioField
from flask_wtf import FlaskForm
from shop.models import Register  # Changed from .models to shop.models
from flask_wtf.file import FileRequired, FileAllowed, FileField


class CustomerRegisterForm(FlaskForm):
    username = StringField('Username: ', [validators.DataRequired(), validators.Length(min=4, max=20)])
    first_name = StringField('First Name: ', [validators.DataRequired(), validators.Length(min=2, max=50)])
    last_name = StringField('Last Name: ', [validators.DataRequired(), validators.Length(min=2, max=50)])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number: ', [validators.DataRequired(), validators.Length(min=10, max=15)])
    gender = RadioField('Gender: ', [validators.DataRequired()], choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], default='Nam')
    password = PasswordField('Password: ', [validators.DataRequired(), validators.Length(min=6),
                                            validators.EqualTo('confirm', message='Mật khẩu xác nhận không khớp!')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    submit = SubmitField('Register')


class CustomerLoginFrom(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])


class CheckoutForm(FlaskForm):
    delivery_method = RadioField('Phương thức nhận hàng: ',
                                [validators.DataRequired(message='Vui lòng chọn phương thức nhận hàng')],
                                choices=[('home_delivery', 'Giao tận nhà'),
                                        ('instore_pickup', 'Nhận tại cửa hàng')],
                                default='home_delivery')

    customer_address = TextAreaField('Địa chỉ giao hàng: ',
                                   render_kw={"placeholder": "Nhập địa chỉ giao hàng chi tiết"})

    pickup_store = RadioField('Chọn cửa hàng nhận hàng: ',
                             choices=[('belluni_cau_dien', 'Belluni Cầu Diễn - Số 298 Đ. Cầu Diễn, Minh Khai, Bắc Từ Liêm, Hà Nội'),
                                     ('belluni_other', 'Cửa hàng khác (sẽ có trong tương lai)')],
                             default='belluni_cau_dien')

    payment_method = RadioField('Phương thức thanh toán: ',
                               [validators.DataRequired(message='Vui lòng chọn phương thức thanh toán')],
                               choices=[('cod', 'Thanh toán khi nhận hàng (COD)'),
                                       ('vnpay', 'Thanh toán online (VNPAY)')],
                               default='cod')
    submit = SubmitField('Đặt hàng')

    def validate(self):
        """Custom validation to ensure proper fields are filled based on delivery and payment method"""
        if not super().validate():
            return False

        delivery_method = self.delivery_method.data

        if delivery_method == 'home_delivery':
            # For home delivery, address is optional but if provided should be valid length
            if self.customer_address.data and len(self.customer_address.data.strip()) < 10:
                self.customer_address.errors.append('Địa chỉ giao hàng phải có ít nhất 10 ký tự')
                return False
        elif delivery_method == 'instore_pickup':
            # For instore pickup, pickup_store should be selected
            if not self.pickup_store.data:
                self.pickup_store.errors.append('Vui lòng chọn cửa hàng nhận hàng')
                return False

        # Additional validation for payment method
        payment_method = self.payment_method.data
        if payment_method not in ['cod', 'vnpay']:
            self.payment_method.errors.append('Phương thức thanh toán không hợp lệ')
            return False

        return True


