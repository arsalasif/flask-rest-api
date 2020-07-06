import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    """
    Base Configuration
    """
    # Base
    APP_NAME = os.environ.get('APP_NAME')
    DEBUG = False
    TESTING = False
    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    LOGGING_LOCATION = 'logs/flask.log'
    LOGGING_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0
    TOKEN_PASSWORD_EXPIRATION_DAYS = 1
    TOKEN_PASSWORD_EXPIRATION_SECONDS = 0
    TOKEN_EMAIL_EXPIRATION_DAYS = 1
    TOKEN_EMAIL_EXPIRATION_SECONDS = 0

    # Mail Server
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Folders
    STATIC_FOLDER = f"{os.environ.get('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.environ.get('APP_FOLDER')}/project/media"

    # Pagination
    POSTS_PER_PAGE = 10
    MAX_PER_PAGE = 100
    DATE_FORMAT = '%m-%d-%Y, %H:%M:%S'

    # Social Authentication
    GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", None)
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", None)
    FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", None)
    FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET", None)

class DevelopmentConfig(BaseConfig):
    """
    Development Configuration
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    BCRYPT_LOG_ROUNDS = 4

class TestingConfig(BaseConfig):
    """
    Testing Configuration
    """
    # Base
    DEBUG = True
    TESTING = True
    TEST_LOGGING_LEVEL = logging.DEBUG
    TEST_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    TEST_LOGGING_LOCATION = 'logs/flask_test.log'

    # Security
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3
    TOKEN_PASSWORD_EXPIRATION_DAYS = 0
    TOKEN_PASSWORD_EXPIRATION_SECONDS = 2
    TOKEN_EMAIL_EXPIRATION_DAYS = 1
    TOKEN_EMAIL_EXPIRATION_SECONDS = 0
    MAIL_SUPPRESS_SEND = True

    # Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_TEST_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    CELERY_TASK_ALWAYS_EAGER = True


class ProductionConfig(BaseConfig):
    """
    Production Configuration
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
