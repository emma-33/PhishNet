"""
Tests for GoPhish API routes
"""
import json


def test_gophish_status_when_disabled(client):
    """Test GoPhish status endpoint when integration is disabled"""
    response = client.get('/api/gophish/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'disabled'
    assert 'message' in data


def test_campaigns_endpoint_when_disabled(client):
    """Test campaigns endpoint returns 503 when GoPhish is disabled"""
    response = client.get('/api/gophish/campaigns')
    assert response.status_code == 503
    
    data = json.loads(response.data)
    assert 'error' in data


def test_groups_endpoint_when_disabled(client):
    """Test groups endpoint returns 503 when GoPhish is disabled"""
    response = client.get('/api/gophish/groups')
    assert response.status_code == 503
    
    data = json.loads(response.data)
    assert 'error' in data


def test_templates_endpoint_when_disabled(client):
    """Test templates endpoint returns 503 when GoPhish is disabled"""
    response = client.get('/api/gophish/templates')
    assert response.status_code == 503
    
    data = json.loads(response.data)
    assert 'error' in data


def test_all_gophish_routes_exist(client):
    """Test that all expected GoPhish routes are registered"""
    routes = [
        '/api/gophish/status',
        '/api/gophish/campaigns',
        '/api/gophish/groups',
        '/api/gophish/templates'
    ]
    
    for route in routes:
        response = client.get(route)
        # Should not return 404 (route exists)
        assert response.status_code != 404
