"""
Test configuration and fixtures for PhishNet Backend
"""
import pytest
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from utils.database import get_db


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    # Initialize database for testing
    with app.app_context():
        db = get_db(app.config['DATABASE_PATH'])
        db.init_schema()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db = get_db(app.config['DATABASE_PATH'])
        db.close()


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()
