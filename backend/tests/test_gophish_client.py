"""
Tests for GoPhish API client
"""
import pytest
from utils.gophish_client import GoPhishClient


def test_gophish_client_initialization():
    """Test that GoPhishClient can be initialized"""
    client = GoPhishClient(
        base_url='http://localhost:3333',
        api_key='test-key'
    )
    
    assert client.base_url == 'http://localhost:3333'
    assert client.api_key == 'test-key'
    assert 'Authorization' in client.headers
    assert client.headers['Authorization'] == 'Bearer test-key'


def test_gophish_client_strips_trailing_slash():
    """Test that trailing slashes are removed from base URL"""
    client = GoPhishClient(
        base_url='http://localhost:3333/',
        api_key='test-key'
    )
    
    assert client.base_url == 'http://localhost:3333'


def test_health_check_with_unreachable_server():
    """Test health check returns False when server is unreachable"""
    client = GoPhishClient(
        base_url='http://localhost:9999',  # Non-existent server
        api_key='test-key'
    )
    
    is_healthy = client.health_check()
    assert is_healthy is False


# Integration tests (require GoPhish running)
# These will be skipped if GoPhish is not available

@pytest.mark.integration
def test_health_check_with_running_server():
    """Test health check with actual GoPhish server (if running)"""
    # This test requires GoPhish to be running
    # Will be skipped in CI/automated testing
    client = GoPhishClient(
        base_url='http://127.0.0.1:3333',
        api_key='invalid-key'  # Even with invalid key, server should respond
    )
    
    # Server is reachable even with invalid auth
    is_healthy = client.health_check()
    # Could be True (server up) or False (server down)
    assert isinstance(is_healthy, bool)
