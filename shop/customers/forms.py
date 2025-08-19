from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf import FlaskForm
from shop.models import Register  # Changed from .models to shop.models
from flask_wtf.file import FileRequired, FileAllowed, FileField


class CustomerRegisterForm(FlaskForm):
    username = StringField('Username: ', [validators.DataRequired()])
    first_name = StringField('First Name: ', [validators.DataRequired()])
    last_name = StringField('Last Name: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number: ', [validators.DataRequired()])
    gender = StringField('Gender: ', [validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired(),
                                            validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if Register.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if Register.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_phone_number(self, field):
        if Register.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone Number already registered.')


class CustomerLoginFrom(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])


