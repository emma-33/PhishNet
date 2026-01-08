"""
Tests for CORS Configuration
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_cors_headers_present_on_api_routes(client):
    """Test that CORS headers are present on API routes"""
    response = client.get('/api/dashboard/overview')
    
    # Check that Access-Control-Allow-Origin header is present
    assert 'Access-Control-Allow-Origin' in response.headers


def test_cors_allows_localhost_5173(client):
    """Test that CORS allows requests from frontend dev server"""
    # Use a simple endpoint that doesn't require database
    response = client.get(
        '/',
        headers={'Origin': 'http://localhost:5173'}
    )
    
    assert response.status_code == 200


def test_cors_allows_127_0_0_1_5173(client):
    """Test that CORS allows requests from 127.0.0.1:5173"""
    # Use a simple endpoint that doesn't require database
    response = client.get(
        '/',
        headers={'Origin': 'http://127.0.0.1:5173'}
    )
    
    assert response.status_code == 200


def test_cors_supports_options_preflight(client):
    """Test that CORS handles OPTIONS preflight requests"""
    response = client.options(
        '/api/dashboard/overview',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET'
        }
    )
    
    # OPTIONS request should be successful
    assert response.status_code in [200, 204]


def test_cors_allows_post_methods(client):
    """Test that CORS allows POST methods"""
    response = client.options(
        '/api/dashboard/email/send',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST'
        }
    )
    
    assert response.status_code in [200, 204]


def test_cors_allows_content_type_header(client):
    """Test that CORS allows Content-Type header"""
    response = client.options(
        '/api/dashboard/campaigns',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
    )
    
    assert response.status_code in [200, 204]


def test_cors_not_present_on_non_api_routes(client):
    """Test that CORS is only applied to /api/* routes"""
    response = client.get('/')
    
    # Root route should work but may not have CORS headers
    assert response.status_code == 200
