"""
Tests for CORS Configuration
"""
import pytest


def test_cors_headers_present_on_api_routes(client):
    """Test that CORS headers are present on API routes"""
    # Test with an endpoint that exists (may return 401/403 but should have CORS headers)
    response = client.get('/api/campaigns')
    
    # Check that Access-Control-Allow-Origin header is present
    assert 'Access-Control-Allow-Origin' in response.headers


def test_cors_allows_localhost_5173(client):
    """Test that CORS allows requests from frontend dev server"""
    # Test with an API endpoint
    response = client.get(
        '/api/campaigns',
        headers={'Origin': 'http://localhost:5173'}
    )
    
    # Should have CORS headers regardless of auth status
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:5173'


def test_cors_allows_127_0_0_1_5173(client):
    """Test that CORS allows requests from 127.0.0.1:5173"""
    response = client.get(
        '/api/campaigns',
        headers={'Origin': 'http://127.0.0.1:5173'}
    )
    
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == 'http://127.0.0.1:5173'


def test_cors_allows_localhost_3000(client):
    """Test that CORS allows requests from localhost:3000"""
    response = client.get(
        '/api/campaigns',
        headers={'Origin': 'http://localhost:3000'}
    )
    
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:3000'


def test_cors_allows_localhost_4173(client):
    """Test that CORS allows requests from localhost:4173 (preview server)"""
    response = client.get(
        '/api/campaigns',
        headers={'Origin': 'http://localhost:4173'}
    )
    
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:4173'


def test_cors_supports_options_preflight(client):
    """Test that CORS handles OPTIONS preflight requests"""
    response = client.options(
        '/api/campaigns',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET'
        }
    )
    
    # OPTIONS request should be successful
    assert response.status_code in [200, 204]
    assert 'Access-Control-Allow-Origin' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers


def test_cors_allows_post_methods(client):
    """Test that CORS allows POST methods"""
    response = client.options(
        '/api/auth/register',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST'
        }
    )
    
    assert response.status_code in [200, 204]
    assert 'Access-Control-Allow-Methods' in response.headers
    # Check that POST is in allowed methods
    allowed_methods = response.headers['Access-Control-Allow-Methods']
    assert 'POST' in allowed_methods


def test_cors_allows_content_type_header(client):
    """Test that CORS allows Content-Type header"""
    response = client.options(
        '/api/campaigns',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
    )
    
    assert response.status_code in [200, 204]
    assert 'Access-Control-Allow-Headers' in response.headers
    allowed_headers = response.headers['Access-Control-Allow-Headers']
    assert 'Content-Type' in allowed_headers


def test_cors_allows_authorization_header(client):
    """Test that CORS allows Authorization header"""
    response = client.options(
        '/api/campaigns',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
    )
    
    assert response.status_code in [200, 204]
    assert 'Access-Control-Allow-Headers' in response.headers
    allowed_headers = response.headers['Access-Control-Allow-Headers']
    assert 'Authorization' in allowed_headers


def test_cors_rejects_unauthorized_origin(client):
    """Test that CORS rejects requests from unauthorized origins"""
    response = client.get(
        '/api/campaigns',
        headers={'Origin': 'http://malicious-site.com'}
    )
    
    if 'Access-Control-Allow-Origin' in response.headers:
        assert response.headers['Access-Control-Allow-Origin'] != 'http://malicious-site.com'


def test_cors_not_present_on_non_api_routes(client):
    """Test that CORS is only applied to /api/* routes"""
    response = client.get('/')
    
    if response.status_code == 200:
        assert 'Access-Control-Allow-Origin' not in response.headers or \
               response.headers.get('Access-Control-Allow-Origin') != 'http://localhost:5173'
