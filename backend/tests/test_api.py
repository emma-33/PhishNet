"""
Test suite for basic API endpoints
"""
import json
from datetime import datetime, timezone


def test_index_endpoint(client):
    """Test the root endpoint returns basic info"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['name'] == 'PhishNet Backend API'
    assert data['status'] == 'running'
    assert 'version' in data


def test_health_check_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'phishnet-backend'
    assert 'timestamp' in data
    
    # Verify timestamp is valid ISO format
    try:
        datetime.fromisoformat(data['timestamp'])
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")


def test_health_check_returns_current_time(client):
    """Test that health check returns a recent timestamp"""
    response = client.get('/health')
    data = json.loads(response.data)
    
    timestamp = datetime.fromisoformat(data['timestamp'])
    now = datetime.now(timezone.utc)
    
    # Timestamp should be within last 5 seconds
    time_diff = (now - timestamp).total_seconds()
    assert time_diff < 5, "Health check timestamp is not recent"


def test_app_is_in_testing_mode(app):
    """Test that the app is configured for testing"""
    assert app.config['TESTING'] is True
    assert app.config['DATABASE_PATH'] == ':memory:'
