from wtforms import Form, SubmitField, IntegerField, FloatField, StringField, TextAreaField, validators, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed


class Addproducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    price = DecimalField('Price', [
        validators.DataRequired(),
        validators.NumberRange(min=0.01, message='Price must be greater than 0')
    ])
    discount = IntegerField('Discount', [
        validators.NumberRange(min=0, max=100, message='Discount must be between 0 and 100'),
        validators.Optional()
    ], default=0)
    stock = IntegerField('Stock', [
        validators.DataRequired(),
        validators.NumberRange(min=0, message='Stock must be greater than or equal to 0')
    ])
    colors = StringField('Colors', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])

    image_1 = FileField('Image 1',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh (JPG, PNG, GIF, JPEG, WEBP, BMP, SVG, ICO)')])
    image_2 = FileField('Image 2',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh (JPG, PNG, GIF, JPEG, WEBP, BMP, SVG, ICO)')])
    image_3 = FileField('Image 3',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh (JPG, PNG, GIF, JPEG, WEBP, BMP, SVG, ICO)')])


class Rates(Form):
    register_id = IntegerField('Register_id', [validators.DataRequired()])
    product_id = IntegerField('Product_id', [validators.DataRequired()])
    desc = TextAreaField('Desc', [validators.DataRequired()])
