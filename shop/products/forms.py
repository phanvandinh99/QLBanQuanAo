from wtforms import Form, SubmitField, IntegerField, FloatField, StringField, TextAreaField, validators, DecimalField, BooleanField, SelectField, FieldList, FormField, HiddenField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional, NumberRange
from shop.models import Size, Color, Brand, Category


class ProductVariantRowForm(FlaskForm):
    """Form for individual variant row"""
    size_id = SelectField('Kích thước', coerce=int, validators=[Optional()])
    color_id = SelectField('Màu sắc', coerce=int, validators=[Optional()])
    price = DecimalField('Giá', validators=[
        DataRequired(message='Vui lòng nhập giá'),
        NumberRange(min=0.01, message='Giá phải lớn hơn 0')
    ])
    stock = IntegerField('Số lượng', validators=[
        DataRequired(message='Vui lòng nhập số lượng'),
        NumberRange(min=0, message='Số lượng phải lớn hơn hoặc bằng 0')
    ])
    sku = StringField('SKU', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(ProductVariantRowForm, self).__init__(*args, **kwargs)
        
        # Populate size choices
        self.size_id.choices = [(0, 'Chọn kích thước')] + [
            (size.id, size.display_name) for size in Size.query.order_by(Size.sort_order).all()
        ]
        
        # Populate color choices
        self.color_id.choices = [(0, 'Chọn màu sắc')] + [
            (color.id, color.name) for color in Color.query.order_by(Color.name).all()
        ]


class AddProductsForm(FlaskForm):
    """Form for adding products - tất cả sản phẩm đều có variants"""
    # Basic product info
    name = StringField('Tên sản phẩm', validators=[DataRequired(message='Vui lòng nhập tên sản phẩm')])
    description = TextAreaField('Mô tả', validators=[DataRequired(message='Vui lòng nhập mô tả')])
    discount = IntegerField('Giảm giá (%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Giảm giá phải từ 0-100%')
    ], default=0)
    
    # Category and Brand
    category_id = SelectField('Danh mục', coerce=int, validators=[DataRequired(message='Vui lòng chọn danh mục')])
    brand_id = SelectField('Thương hiệu', coerce=int, validators=[DataRequired(message='Vui lòng chọn thương hiệu')])
    
    # Tất cả sản phẩm đều có variants - bỏ các trường cũ
    # has_variants = BooleanField('Sản phẩm có nhiều biến thể (size, màu sắc, giá khác nhau)')
    # simple_price = DecimalField('Giá (cho sản phẩm đơn giản)', validators=[Optional()])
    # simple_stock = IntegerField('Số lượng (cho sản phẩm đơn giản)', validators=[Optional()])
    # simple_colors = StringField('Màu sắc (cho sản phẩm đơn giản)', validators=[Optional()])
    
    # Images
    image_1 = FileField('Hình ảnh 1', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh')
    ])
    image_2 = FileField('Hình ảnh 2', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh')
    ])
    image_3 = FileField('Hình ảnh 3', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'], 'Chỉ chấp nhận file ảnh')
    ])

    def __init__(self, *args, **kwargs):
        super(AddProductsForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        self.category_id.choices = [(0, 'Chọn danh mục')] + [
            (cat.id, cat.name) for cat in Category.query.order_by(Category.name).all()
        ]
        
        # Populate brand choices - will be filtered by category via AJAX
        self.brand_id.choices = [(0, 'Chọn thương hiệu')] + [
            (brand.id, brand.name) for brand in Brand.query.order_by(Brand.name).all()
        ]

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators)
        if not rv:
            return False

        # Tất cả sản phẩm đều có variants - không cần validation đặc biệt
        return rv


# Keep the old form for backward compatibility
class Addproducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    # Bỏ price và stock vì tất cả sản phẩm đều có variants
    # price = DecimalField('Price', [validators.Optional(), validators.NumberRange(min=0)])
    discount = IntegerField('Discount', [validators.Optional(), validators.NumberRange(min=0, max=100)], default=0)
    # stock = IntegerField('Stock', [validators.Optional(), validators.NumberRange(min=0)], default=0)
    colors = StringField('Colors', [validators.Optional()])  # Không còn cần thiết
    has_variants = BooleanField('Has Variants', default=True)  # Luôn True
    description = TextAreaField('Description', [validators.DataRequired()])

    image_1 = FileField('Image 1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'])])
    image_2 = FileField('Image 2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'])])
    image_3 = FileField('Image 3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'webp', 'bmp', 'svg', 'ico'])])
    
    def validate(self, extra_validators=None):
        """Custom validation - tất cả sản phẩm đều có variants"""
        rv = super().validate(extra_validators)
        if not rv:
            return False
            
        # Tất cả sản phẩm đều có variants - không cần validation đặc biệt
        return True


class ProductVariantForm(FlaskForm):
    """Form for managing product variants"""
    size_id = SelectField('Kích thước', coerce=int, validators=[Optional()])
    color_id = SelectField('Màu sắc', coerce=int, validators=[Optional()])
    price = DecimalField('Giá', validators=[
        DataRequired(message='Vui lòng nhập giá'),
        NumberRange(min=0.01, message='Giá phải lớn hơn 0')
    ])
    stock = IntegerField('Số lượng', validators=[
        DataRequired(message='Vui lòng nhập số lượng'),
        NumberRange(min=0, message='Số lượng phải lớn hơn hoặc bằng 0')
    ])
    sku = StringField('SKU', validators=[Optional()])
    is_active = BooleanField('Kích hoạt', default=True)

    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        
        # Populate size choices
        self.size_id.choices = [(0, 'Chọn kích thước')] + [
            (size.id, size.display_name) for size in Size.query.order_by(Size.sort_order).all()
        ]
        
        # Populate color choices
        self.color_id.choices = [(0, 'Chọn màu sắc')] + [
            (color.id, color.name) for color in Color.query.order_by(Color.name).all()
        ]


class SizeForm(FlaskForm):
    """Form for managing sizes"""
    name = StringField('Tên size', validators=[
        DataRequired(message='Vui lòng nhập tên size'),
        validators.Length(min=1, max=10, message='Tên size phải từ 1-10 ký tự')
    ])
    display_name = StringField('Tên hiển thị', validators=[
        DataRequired(message='Vui lòng nhập tên hiển thị'),
        validators.Length(min=1, max=20, message='Tên hiển thị phải từ 1-20 ký tự')
    ])
    sort_order = IntegerField('Thứ tự sắp xếp', validators=[
        Optional(),
        NumberRange(min=0, message='Thứ tự phải lớn hơn hoặc bằng 0')
    ], default=0)


class ColorForm(FlaskForm):
    """Form for managing colors"""
    name = StringField('Tên màu', validators=[
        DataRequired(message='Vui lòng nhập tên màu'),
        validators.Length(min=1, max=50, message='Tên màu phải từ 1-50 ký tự')
    ])
    hex_code = StringField('Mã màu (hex)', validators=[
        Optional(),
        validators.Regexp(r'^#[0-9A-Fa-f]{6}$', message='Mã màu phải có định dạng #RRGGBB')
    ])


class Rates(Form):
    register_id = IntegerField('Register_id', [validators.DataRequired()])
    product_id = IntegerField('Product_id', [validators.DataRequired()])
    desc = TextAreaField('Desc', [validators.DataRequired()])
