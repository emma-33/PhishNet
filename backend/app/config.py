import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "app.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173').split(',')

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