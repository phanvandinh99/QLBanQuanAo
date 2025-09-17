from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
try:
    from flask_uploads import UploadSet, IMAGES, configure_uploads
    FLASK_UPLOADS_AVAILABLE = True
except ImportError:
    FLASK_UPLOADS_AVAILABLE = False
    print("⚠️ Flask-Uploads not available, using fallback")

import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Database configuration - set BEFORE initializing SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/myshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SQLAlchemy after app creation
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

app.config['VNPAY_URL'] = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
app.config['VNPAY_TMN_CODE'] = 'WSGZMU68'
app.config['VNPAY_HASH_SECRET'] = 'HM60DQ1QI6AKYMZUXT7Z2M9SHZWL4P0I'
app.config['VNPAY_RETURN_URL'] = 'http://localhost:5000/vnpay_return'
app.config['VNPAY_IPN_URL'] = 'http://localhost:5000/vnpay_ipn'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'vonhanh271@gmail.com'  # Thay bằng email của bạn
app.config['MAIL_PASSWORD'] = 'aonkmuvovinnkabz'    # Thay bằng app password
app.config['MAIL_DEFAULT_SENDER'] = 'vonhanh271@gmail.com'  # Thay bằng email của bạn

# Upload configuration
app.config['UPLOADED_PHOTOS_DEST'] = 'shop/static/images'

# Initialize extensions (SQLAlchemy already initialized above)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customer_login'
mail = Mail(app)

# Custom image extensions including webp, bmp, svg, ico
ALLOWED_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'ico',
    'JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'SVG', 'ICO'
)

if FLASK_UPLOADS_AVAILABLE:
    photos = UploadSet('photos', ALLOWED_EXTENSIONS)
    configure_uploads(app, photos)
else:
    photos = None

# Custom filter for VND currency format
@app.template_filter('vnd')
def vnd_format(value):
    """Format number as VND currency"""
    try:
        return f"{int(value):,} ₫"
    except (ValueError, TypeError):
        return f"{value} ₫"

# Import models and setup login manager
from shop.models import Register

@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

# Import routes
from shop.admin import routes
from shop.products import routes 
from shop.carts import routes
from shop.customers import routes