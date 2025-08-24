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


