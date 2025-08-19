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

# Upload configuration
app.config['UPLOADED_PHOTOS_DEST'] = 'shop/static/images'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customer_login'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

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