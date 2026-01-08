"""
Tests for landing page routes
"""
import json


def test_landing_page_route_exists(client):
    """Test that landing page route is registered"""
    response = client.get('/landing/fake_login')
    # Should not return 404
    assert response.status_code != 404


def test_landing_page_logs_visit(client, app):
    """Test that visiting a landing page logs the visit"""
    response = client.get('/landing/fake_login?c=test_campaign&u=user123')
    
    # Check that visit was logged
    with app.app_context():
        from utils.database import get_db
        db = get_db(app.config['DATABASE_PATH'])
        visits = db.fetchall('SELECT * FROM page_visits WHERE campaign_id = ?', ('test_campaign',))
        
        assert len(visits) > 0
        assert visits[0]['user_identifier'] == 'user123'


def test_landing_page_post_logs_submission(client, app):
    """Test that form submission is logged"""
    response = client.post(
        '/landing/fake_login?c=test_campaign&u=user123',
        data={
            'username': 'testuser',
            'password': 'testpass123',
            'redirect_url': 'https://example.com'
        },
        follow_redirects=False
    )
    
    # Should redirect
    assert response.status_code == 302
    
    # Check that submission was logged
    with app.app_context():
        from utils.database import get_db
        db = get_db(app.config['DATABASE_PATH'])
        submissions = db.fetchall(
            'SELECT * FROM form_submissions WHERE campaign_id = ?',
            ('test_campaign',)
        )
        
        assert len(submissions) > 0
        assert submissions[0]['username'] == 'testuser'
        assert submissions[0]['password'] == 'testpass123'


def test_landing_page_redirect(client):
    """Test that form submission redirects correctly"""
    response = client.post(
        '/landing/fake_login',
        data={
            'username': 'test',
            'password': 'pass',
            'redirect_url': 'https://google.com'
        },
        follow_redirects=False
    )
    
    assert response.status_code == 302
    assert response.location == 'https://google.com'


def test_tracking_visits_api(client, app):
    """Test API endpoint for retrieving visits"""
    # Create a visit first
    client.get('/landing/fake_login?c=api_test')
    
    # Get visits
    response = client.get('/api/tracking/visits?campaign_id=api_test')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'visits' in data
    assert 'count' in data
    assert data['count'] > 0


def test_tracking_submissions_api(client, app):
    """Test API endpoint for retrieving submissions"""
    # Create a submission first
    client.post(
        '/landing/fake_login?c=api_test',
        data={
            'username': 'apitest',
            'password': 'secret123',
            'redirect_url': 'https://example.com'
        }
    )
    
    # Get submissions
    response = client.get('/api/tracking/submissions?campaign_id=api_test')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'submissions' in data
    assert 'count' in data
    assert data['count'] > 0
    
    # Verify password is masked
    assert data['submissions'][0]['password'] == '***'


def test_tracking_without_campaign_id(client):
    """Test tracking APIs work without campaign_id parameter"""
    response = client.get('/api/tracking/visits')
    assert response.status_code == 200
    
    response = client.get('/api/tracking/submissions')
    assert response.status_code == 200


def test_landing_page_captures_additional_fields(client, app):
    """Test that additional form fields are captured"""
    client.post(
        '/landing/fake_login?c=extra_test',
        data={
            'username': 'user',
            'password': 'pass',
            'email': 'user@example.com',
            'phone': '123-456-7890',
            'redirect_url': 'https://example.com'
        }
    )
    
    # Check additional data was stored
    with app.app_context():
        from utils.database import get_db
        db = get_db(app.config['DATABASE_PATH'])
        submissions = db.fetchall(
            'SELECT * FROM form_submissions WHERE campaign_id = ?',
            ('extra_test',)
        )
        
        assert len(submissions) > 0
        additional_data = json.loads(submissions[0]['additional_data'])
        assert 'email' in additional_data
        assert 'phone' in additional_data
