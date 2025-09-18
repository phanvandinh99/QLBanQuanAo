from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
try:
    from flask_uploads import UploadSet, IMAGES, configure_uploads
    FLASK_UPLOADS_AVAILABLE = True
except ImportError:
    # Try the maintained fork
    try:
        from flask_reuploaded import UploadSet, IMAGES, configure_uploads
        FLASK_UPLOADS_AVAILABLE = True
    except ImportError:
        FLASK_UPLOADS_AVAILABLE = False
        print("⚠️ Flask-Uploads not available, using fallback")

import pymysql
pymysql.install_as_MySQLdb()

from config import get_config

app = Flask(__name__)
config_class = get_config()
app.config.from_object(config_class)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customer_login'
mail = Mail(app)

ALLOWED_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'ico',
    'JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'BMP', 'SVG', 'ICO'
)

if FLASK_UPLOADS_AVAILABLE:
    photos = UploadSet('photos', ALLOWED_EXTENSIONS)
    configure_uploads(app, photos)
else:
    photos = None

@app.template_filter('vnd')
def vnd_format(value):
    """Format number as VND currency"""
    try:
        # Handle different input types
        if isinstance(value, str):
            # Remove commas and spaces, then convert
            value = value.replace(',', '').replace(' ', '').strip()
            if '.' in value:
                return f"{float(value):,.0f} ₫"
            else:
                return f"{int(value):,} ₫"
        elif isinstance(value, (int, float)):
            return f"{int(value):,} ₫"
        else:
            num_value = float(value)
            return f"{int(num_value):,} ₫"
    except (ValueError, TypeError):
        return f"{value} ₫"

from shop.models import Customer

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

from shop.caching import init_cache
init_cache(app)

from shop.errors import register_error_handlers
register_error_handlers(app)

from shop.admin import routes
from shop.products import routes
from shop.carts import routes
from shop.customers import routes

@app.before_request
def before_request():
    from shop.optimization import PerformanceMonitor
    PerformanceMonitor.start_timer()

@app.after_request
def after_request(response):
    from shop.optimization import PerformanceMonitor
    PerformanceMonitor.end_timer()
    return response