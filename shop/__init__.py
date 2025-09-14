from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/myshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# VNPAY Configuration
app.config['VNPAY_URL'] = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
app.config['VNPAY_TMN_CODE'] = 'QV4AJ3NO'
app.config['VNPAY_HASH_SECRET'] = '3CP0V5HCDJ6VFE1YPVYL85YUHK1SGLLP'

# IMPORTANT: For development, use ngrok to expose localhost to internet
# Install ngrok: https://ngrok.com/download
# Run: ngrok http 5000
# Then update these URLs with your ngrok URL, e.g.:
# app.config['VNPAY_RETURN_URL'] = 'https://abcd1234.ngrok.io/vnpay_return'
# app.config['VNPAY_IPN_URL'] = 'https://abcd1234.ngrok.io/vnpay_ipn'

app.config['VNPAY_RETURN_URL'] = 'http://localhost:5000/vnpay_return'
app.config['VNPAY_IPN_URL'] = 'http://localhost:5000/vnpay_ipn'

# Upload configuration
app.config['UPLOADED_PHOTOS_DEST'] = 'shop/static/images'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customer_login'

# Custom image extensions including webp, bmp, svg, ico
ALLOWED_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'ico',
    'JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'SVG', 'ICO'
)

photos = UploadSet('photos', ALLOWED_EXTENSIONS)
configure_uploads(app, photos)

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