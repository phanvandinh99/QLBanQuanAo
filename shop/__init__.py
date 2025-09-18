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

# Import config
from config import get_config

# Create app with configuration
app = Flask(__name__)
config_class = get_config()
app.config.from_object(config_class)

# Initialize SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

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
from shop.models import Customer

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

# Initialize caching
from shop.caching import init_cache
init_cache(app)

# Register error handlers
from shop.errors import register_error_handlers
register_error_handlers(app)

# Import routes
from shop.admin import routes
from shop.products import routes
from shop.carts import routes
from shop.customers import routes

# Performance monitoring
@app.before_request
def before_request():
    from shop.optimization import PerformanceMonitor
    PerformanceMonitor.start_timer()

@app.after_request
def after_request(response):
    from shop.optimization import PerformanceMonitor
    PerformanceMonitor.end_timer()
    return response