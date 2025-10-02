import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/dbname')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VNPay
    VNPAY_URL = os.getenv('VNPAY_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
    VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE', 'YOUR_VNPAY_TMN_CODE')
    VNPAY_HASH_SECRET = os.getenv('VNPAY_HASH_SECRET', 'YOUR_VNPAY_HASH_SECRET')
    VNPAY_RETURN_URL = os.getenv('VNPAY_RETURN_URL', 'http://localhost:5000/vnpay_return')
    VNPAY_IPN_URL = os.getenv('VNPAY_IPN_URL', 'http://localhost:5000/vnpay_ipn')

    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_app_password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@gmail.com')

    # Upload
    UPLOADED_PHOTOS_DEST = os.getenv('UPLOADED_PHOTOS_DEST', 'shop/static/images')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])