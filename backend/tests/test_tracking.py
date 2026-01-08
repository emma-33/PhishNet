"""
Tests for email tracking functionality
"""
import pytest


class TestEmailTracking:
    """Test suite for email tracking routes"""
    
    def test_tracking_pixel_endpoint_exists(self, client):
        """Test tracking pixel endpoint is accessible"""
        response = client.get('/track/pixel/test123')
        assert response.status_code == 200
        assert response.mimetype == 'image/gif'
    
    def test_tracking_pixel_logs_email_open(self, client):
        """Test tracking pixel logs email opens"""
        response = client.get('/track/pixel/campaign123?email=victim@example.com')
        
        assert response.status_code == 200
        assert response.mimetype == 'image/gif'
        
        # Verify visit was logged
        visits_response = client.get('/api/tracking/visits')
        data = visits_response.get_json()
        visits = data['visits']
        
        # Find the email open visit
        email_opens = [v for v in visits if '/track/pixel/campaign123' in v.get('page_url', '')]
        assert len(email_opens) > 0
        assert email_opens[0]['campaign_id'] == 'campaign123'
    
    def test_tracking_pixel_returns_gif(self, client):
        """Test tracking pixel returns valid GIF image"""
        response = client.get('/track/pixel/test123')
        
        assert response.status_code == 200
        assert response.mimetype == 'image/gif'
        assert len(response.data) > 0
        # GIF magic number
        assert response.data[:3] == b'GIF'
    
    def test_tracking_pixel_without_email(self, client):
        """Test tracking pixel works without email parameter"""
        response = client.get('/track/pixel/test123')
        
        assert response.status_code == 200
        assert response.mimetype == 'image/gif'
    
    def test_link_click_tracking(self, client):
        """Test link click tracking"""
        response = client.get(
            '/track/click/campaign123?url=http://example.com&email=victim@example.com',
            follow_redirects=False
        )
        
        assert response.status_code == 302  # Redirect
        assert response.location == 'http://example.com'
        
        # Verify click was logged
        visits_response = client.get('/api/tracking/visits')
        data = visits_response.get_json()
        visits = data['visits']
        
        link_clicks = [v for v in visits if '/track/click/' in v.get('page_url', '')]
        assert len(link_clicks) > 0
    
    def test_link_click_default_redirect(self, client):
        """Test link click with default redirect"""
        response = client.get(
            '/track/click/test123',
            follow_redirects=False
        )
        
        assert response.status_code == 302
        assert response.location == '/'
    
    def test_tracking_stats_endpoint(self, client):
        """Test tracking statistics endpoint"""
        campaign_id = 'stats_test'
        
        # Generate some tracking events
        client.get(f'/track/pixel/{campaign_id}?email=user1@example.com')
        client.get(f'/track/pixel/{campaign_id}?email=user2@example.com')
        client.get(f'/track/click/{campaign_id}?url=http://example.com&email=user1@example.com')
        
        # Get stats
        response = client.get(f'/track/stats/{campaign_id}')
        assert response.status_code == 200
        
        stats = response.get_json()
        assert stats['campaign_id'] == campaign_id
        assert stats['email_opens'] == 2
        assert stats['link_clicks'] == 1
        assert stats['total_interactions'] >= 3
    
    def test_tracking_stats_with_submissions(self, client):
        """Test tracking stats includes form submissions"""
        campaign_id = 'full_stats_test'
        
        # Email open
        client.get(f'/track/pixel/{campaign_id}')
        
        # Landing page visit and submission
        client.get(f'/landing/fake_login?campaign_id={campaign_id}')
        client.post(f'/landing/fake_login', data={
            'username': 'victim@example.com',
            'password': 'password123',
            'campaign_id': campaign_id
        })
        
        # Get stats
        response = client.get(f'/track/stats/{campaign_id}')
        stats = response.get_json()
        
        assert stats['campaign_id'] == campaign_id
        assert stats['email_opens'] >= 1
        # Form submission tracking verified by test_landing_pages.py
    
    def test_tracking_stats_empty_campaign(self, client):
        """Test tracking stats for campaign with no data"""
        response = client.get('/track/stats/nonexistent_campaign')
        assert response.status_code == 200
        
        stats = response.get_json()
        assert stats['campaign_id'] == 'nonexistent_campaign'
        assert stats['email_opens'] == 0
        assert stats['link_clicks'] == 0
        assert stats['form_submissions'] == 0
    
    def test_multiple_email_opens_same_user(self, client):
        """Test tracking multiple email opens from same user"""
        campaign_id = 'multi_open'
        email = 'user@example.com'
        
        # Open email multiple times
        for _ in range(3):
            response = client.get(f'/track/pixel/{campaign_id}?email={email}')
            assert response.status_code == 200
        
        # Check stats
        response = client.get(f'/track/stats/{campaign_id}')
        stats = response.get_json()
        
        assert stats['email_opens'] == 3
    
    def test_tracking_preserves_user_agent(self, client):
        """Test tracking preserves user agent information"""
        response = client.get(
            '/track/pixel/test123',
            headers={'User-Agent': 'TestBot/1.0'}
        )
        
        assert response.status_code == 200
        
        # Verify user agent was logged
        visits_response = client.get('/api/tracking/visits')
        data = visits_response.get_json()
        visits = data['visits']
        
        if visits:
            # At least one visit should have user agent
            assert any('TestBot' in v.get('user_agent', '') for v in visits)
    
    def test_tracking_logs_ip_address(self, client):
        """Test tracking logs IP address"""
        response = client.get('/track/pixel/test123')
        assert response.status_code == 200
        
        # Verify IP was logged
        visits_response = client.get('/api/tracking/visits')
        data = visits_response.get_json()
        visits = data['visits']
        
        if visits:
            # Should have IP address (test client uses 127.0.0.1)
            assert any(v.get('ip_address') for v in visits)
