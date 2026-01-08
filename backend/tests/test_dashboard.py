"""
Tests for dashboard API routes
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestDashboardOverview:
    """Tests for dashboard overview endpoint"""
    
    def test_overview_endpoint_exists(self, client):
        """Test dashboard overview endpoint is accessible"""
        response = client.get('/api/dashboard/overview')
        assert response.status_code == 200
    
    def test_overview_returns_statistics(self, client):
        """Test overview returns required statistics"""
        response = client.get('/api/dashboard/overview')
        data = response.get_json()
        
        assert 'statistics' in data
        assert 'system_status' in data
        assert 'timestamp' in data
        
        stats = data['statistics']
        assert 'total_campaigns' in stats
        assert 'active_campaigns' in stats
        assert 'total_visits' in stats
        assert 'total_submissions' in stats
    
    def test_overview_system_status(self, client):
        """Test system status is included"""
        response = client.get('/api/dashboard/overview')
        data = response.get_json()
        
        status = data['system_status']
        assert 'gophish' in status
        assert 'email' in status
        assert 'database' in status
        assert status['database'] == 'operational'


class TestCampaignsList:
    """Tests for campaigns list endpoint"""
    
    def test_campaigns_list_when_disabled(self, client):
        """Test campaigns list when GoPhish disabled"""
        response = client.get('/api/dashboard/campaigns')
        assert response.status_code == 503
        
        data = response.get_json()
        assert 'error' in data
    
    @patch('routes.dashboard.GoPhishClient')
    def test_campaigns_list_structure(self, mock_client_class, app, client):
        """Test campaigns list returns correct structure"""
        # Enable GoPhish for this test
        app.config['GOPHISH_ENABLED'] = True
        
        # Mock GoPhish client
        mock_client = Mock()
        mock_client.get_campaigns.return_value = [
            {
                'id': 1,
                'name': 'Test Campaign',
                'status': 'Completed',
                'created_date': '2026-01-01T00:00:00Z',
                'launch_date': '2026-01-01T00:00:00Z',
                'completed_date': '2026-01-08T00:00:00Z',
                'results': []
            }
        ]
        mock_client_class.return_value = mock_client
        
        response = client.get('/api/dashboard/campaigns')
        data = response.get_json()
        
        assert 'campaigns' in data
        assert 'count' in data
        assert isinstance(data['campaigns'], list)


class TestCampaignMetrics:
    """Tests for campaign metrics calculation"""
    
    def test_campaign_metrics_endpoint(self, client):
        """Test campaign metrics endpoint"""
        # Create some test data
        client.get('/track/pixel/test_campaign?email=user@example.com')
        client.get('/track/click/test_campaign?url=http://example.com&email=user@example.com')
        
        response = client.get('/api/dashboard/campaigns/test_campaign/metrics')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'campaign_id' in data
        assert 'metrics' in data
        assert 'recommendations' in data
    
    def test_metrics_calculation(self, client):
        """Test metrics are calculated correctly"""
        campaign_id = 'metrics_test'
        
        # Generate tracking data
        for i in range(5):
            client.get(f'/track/pixel/{campaign_id}?email=user{i}@example.com')
        
        for i in range(3):
            client.get(f'/track/click/{campaign_id}?url=http://example.com&email=user{i}@example.com')
        
        response = client.get(f'/api/dashboard/campaigns/{campaign_id}/metrics')
        data = response.get_json()
        
        metrics = data['metrics']
        assert metrics['email_opens'] == 5
        assert metrics['link_clicks'] == 3
    
    def test_recommendations_generated(self, client):
        """Test that recommendations are generated"""
        response = client.get('/api/dashboard/campaigns/test/metrics')
        data = response.get_json()
        
        assert 'recommendations' in data
        assert isinstance(data['recommendations'], list)


class TestCampaignComparison:
    """Tests for campaign comparison"""
    
    def test_compare_campaigns_requires_ids(self, client):
        """Test comparison requires campaign IDs"""
        response = client.post('/api/dashboard/campaigns/compare',
                              json={})
        assert response.status_code == 400
    
    def test_compare_campaigns_structure(self, client):
        """Test comparison returns correct structure"""
        # Create data for multiple campaigns
        client.get('/track/pixel/campaign1')
        client.get('/track/pixel/campaign2')
        
        response = client.post('/api/dashboard/campaigns/compare',
                              json={'campaign_ids': ['campaign1', 'campaign2']})
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'comparison' in data
        assert 'analysis' in data
        assert len(data['comparison']) == 2
    
    def test_comparison_analysis(self, client):
        """Test comparison includes analysis"""
        response = client.post('/api/dashboard/campaigns/compare',
                              json={'campaign_ids': ['test1', 'test2']})
        data = response.get_json()
        
        analysis = data['analysis']
        assert 'most_effective' in analysis
        assert 'least_effective' in analysis
        assert 'total_campaigns' in analysis


class TestEmailSending:
    """Tests for email sending endpoint"""
    
    @patch('routes.dashboard.EmailClient')
    def test_send_email_requires_fields(self, mock_email_class, client):
        """Test email sending requires all fields"""
        response = client.post('/api/dashboard/email/send',
                              json={'to': 'test@example.com'})
        assert response.status_code == 400
    
    @patch('routes.dashboard.EmailClient')
    def test_send_email_success(self, mock_email_class, client):
        """Test successful email sending"""
        mock_email = Mock()
        mock_email.send_phishing_email.return_value = True
        mock_email_class.return_value = mock_email
        
        response = client.post('/api/dashboard/email/send',
                              json={
                                  'to': 'test@example.com',
                                  'subject': 'Test',
                                  'body_text': 'Test body',
                                  'campaign_id': 'test123'
                              })
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    @patch('routes.dashboard.EmailClient')
    def test_send_email_failure(self, mock_email_class, client):
        """Test email sending failure handling"""
        mock_email = Mock()
        mock_email.send_phishing_email.return_value = False
        mock_email_class.return_value = mock_email
        
        response = client.post('/api/dashboard/email/send',
                              json={
                                  'to': 'test@example.com',
                                  'subject': 'Test',
                                  'body_text': 'Test body',
                                  'campaign_id': 'test123'
                              })
        assert response.status_code == 500


class TestResourceLists:
    """Tests for resource listing endpoints"""
    
    def test_list_templates_when_disabled(self, client):
        """Test templates list when GoPhish disabled"""
        response = client.get('/api/dashboard/templates')
        assert response.status_code == 503
    
    def test_list_groups_when_disabled(self, client):
        """Test groups list when GoPhish disabled"""
        response = client.get('/api/dashboard/groups')
        assert response.status_code == 503
    
    def test_list_landing_pages_when_disabled(self, client):
        """Test landing pages list when GoPhish disabled"""
        response = client.get('/api/dashboard/landing-pages')
        assert response.status_code == 503
    
    @patch('routes.dashboard.GoPhishClient')
    def test_list_templates_structure(self, mock_client_class, app, client):
        """Test templates list structure"""
        app.config['GOPHISH_ENABLED'] = True
        
        mock_client = Mock()
        mock_client.get_templates.return_value = [
            {'id': 1, 'name': 'Template 1'},
            {'id': 2, 'name': 'Template 2'}
        ]
        mock_client_class.return_value = mock_client
        
        response = client.get('/api/dashboard/templates')
        data = response.get_json()
        
        assert 'templates' in data
        assert 'count' in data
        assert data['count'] == 2


class TestAnalyticsTimeline:
    """Tests for analytics timeline"""
    
    def test_timeline_endpoint(self, client):
        """Test analytics timeline endpoint"""
        response = client.get('/api/dashboard/analytics/timeline')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'timeline' in data
        assert 'total_days' in data
        assert isinstance(data['timeline'], list)
    
    def test_timeline_with_campaign_filter(self, client):
        """Test timeline filtered by campaign"""
        # Generate some data
        client.get('/track/pixel/timeline_test')
        
        response = client.get('/api/dashboard/analytics/timeline?campaign_id=timeline_test')
        data = response.get_json()
        
        assert data['campaign_id'] == 'timeline_test'
        assert 'timeline' in data
    
    def test_timeline_structure(self, client):
        """Test timeline data structure"""
        response = client.get('/api/dashboard/analytics/timeline')
        data = response.get_json()
        
        # Timeline items should have date, visits, submissions
        for item in data['timeline']:
            assert 'date' in item
            assert 'visits' in item
            assert 'submissions' in item


class TestRecommendations:
    """Tests for security recommendations"""
    
    def test_high_open_rate_recommendation(self, client):
        """Test high open rate generates recommendation"""
        from routes.dashboard import generate_recommendations
        
        recommendations = generate_recommendations({
            'open_rate': 60,
            'click_rate': 10,
            'submission_rate': 5
        })
        
        assert len(recommendations) > 0
        assert any('email' in r['category'].lower() for r in recommendations)
    
    def test_high_click_rate_recommendation(self, client):
        """Test high click rate generates recommendation"""
        from routes.dashboard import generate_recommendations
        
        recommendations = generate_recommendations({
            'open_rate': 20,
            'click_rate': 50,
            'submission_rate': 10
        })
        
        assert any('awareness' in r['category'].lower() for r in recommendations)
    
    def test_high_submission_rate_recommendation(self, client):
        """Test high submission rate generates critical recommendation"""
        from routes.dashboard import generate_recommendations
        
        recommendations = generate_recommendations({
            'open_rate': 20,
            'click_rate': 20,
            'submission_rate': 40
        })
        
        critical = [r for r in recommendations if r['severity'] == 'critical']
        assert len(critical) > 0
    
    def test_positive_feedback(self, client):
        """Test low rates generate positive feedback"""
        from routes.dashboard import generate_recommendations
        
        recommendations = generate_recommendations({
            'open_rate': 15,
            'click_rate': 10,
            'submission_rate': 5
        })
        
        assert any('positive' in r['category'].lower() for r in recommendations)
