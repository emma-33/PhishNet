"""
Configuration settings for PhishNet Backend
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'phishnet.db')
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # GoPhish Integration
    GOPHISH_API_URL = os.environ.get('GOPHISH_API_URL') or 'http://127.0.0.1:3333'
    GOPHISH_API_KEY = os.environ.get('GOPHISH_API_KEY') or 'imshy'
    GOPHISH_ENABLED = os.environ.get('GOPHISH_ENABLED', 'true').lower() == 'true'
    
    # MailTrap SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 2525)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'imshy'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'imshy'
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'phishnet@example.com'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    GOPHISH_ENABLED = False  # Disable GoPhish for unit tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
