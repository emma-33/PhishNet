import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "app.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', "jwt-secret-key") # move to env in prod
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_COOKIE_SECURE = False          # False on localhost HTTP
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    # CORS Configuration
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ORIGINS = ["http://localhost:5173"] 
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    """Configuration for testing"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    LOG_LEVEL = 'DEBUG'