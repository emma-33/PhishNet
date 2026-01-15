"""
Tests for Template API endpoints
"""
import pytest
from unittest.mock import Mock, patch
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, Instance, Template


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db_session, test_tenant):
    """Create an admin user"""
    password_hash = bcrypt.generate_password_hash("adminpassword123").decode('utf-8')
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session, test_tenant):
    """Create a regular (non-admin) user"""
    password_hash = bcrypt.generate_password_hash("userpassword123").decode('utf-8')
    user = User(
        email="user@example.com",
        first_name="Regular",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_instance(db_session):
    """Create a test Gophish instance"""
    instance = Instance(
        name="Test Instance",
        base_url="https://test-gophish.example.com",
        api_key="test-api-key",
        redirect_url="https://test-redirect.example.com",
        is_active=True
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


@pytest.fixture
def test_template(db_session, test_instance, admin_user):
    """Create a test template"""
    template = Template(
        name="Test Template",
        gophish_instance_id=test_instance.id,
        gophish_email_template_id=1,
        gophish_landing_page_id=1,
        created_by_user_id=admin_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def admin_headers(admin_user):
    """Create authorization headers with admin JWT token"""
    token = create_access_token(identity=admin_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    """Create authorization headers with regular user JWT token"""
    token = create_access_token(identity=regular_user.id)
    return {'Authorization': f'Bearer {token}'}


class TestGetAllTemplates:
    """Tests for GET /api/templates"""
    
    @patch('app.services.gophish.templates.TemplatesService.get_all_templates')
    def test_get_all_templates_success(self, mock_get_templates, client, regular_headers, test_template):
        """Test successfully getting all templates"""
        mock_get_templates.return_value = [test_template]
        
        response = client.get('/api/templates', headers=regular_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'templates' in data
        assert isinstance(data['templates'], list)
        assert len(data['templates']) == 1
        assert data['templates'][0]['id'] == test_template.id
        assert data['templates'][0]['name'] == test_template.name
    
    @patch('app.services.gophish.templates.TemplatesService.get_all_templates')
    def test_get_all_templates_empty(self, mock_get_templates, client, regular_headers):
        """Test getting all templates when none exist"""
        mock_get_templates.return_value = []
        
        response = client.get('/api/templates', headers=regular_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'templates' in data
        assert data['templates'] == []
    
    @patch('app.services.gophish.templates.TemplatesService.get_all_templates')
    def test_get_all_templates_summary_fields(self, mock_get_templates, client, regular_headers, test_template):
        """Test that template summary includes correct fields"""
        mock_get_templates.return_value = [test_template]
        
        response = client.get('/api/templates', headers=regular_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        template = data['templates'][0]
        
        assert 'id' in template
        assert 'name' in template
        assert 'created_by_user_id' in template
        assert 'created_at' in template
        # Should not include detailed fields
        assert 'email_template' not in template
        assert 'landing_page' not in template
    
    def test_get_all_templates_requires_auth(self, client):
        """Test that getting templates requires authentication"""
        response = client.get('/api/templates')
        
        assert response.status_code == 401


class TestGetTemplate:
    """Tests for GET /api/templates/<id>"""
    
    @patch('app.services.gophish.templates.TemplatesService.get_template_details')
    def test_get_template_success(self, mock_get_details, client, admin_headers, test_template):
        """Test successfully getting template details"""
        # Mock template details response
        mock_email_template = Mock()
        mock_email_template.id = 1
        mock_email_template.name = "Email Template"
        mock_email_template.subject = "Test Subject"
        mock_email_template.html = "<html>Email</html>"
        mock_email_template.attachments = []
        
        mock_landing_page = Mock()
        mock_landing_page.id = 1
        mock_landing_page.name = "Landing Page"
        mock_landing_page.html = "<html>Landing</html>"
        mock_landing_page.capture_credentials = False
        mock_landing_page.capture_passwords = False
        mock_landing_page.redirect_url = ""
        
        mock_get_details.return_value = {
            'template_map': test_template,
            'email_template': mock_email_template,
            'landing_page': mock_landing_page
        }
        
        response = client.get(f'/api/templates/{test_template.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_template.id
        assert data['name'] == test_template.name
        assert 'email_template' in data
        assert 'landing_page' in data
        assert data['email_template']['subject'] == "Test Subject"
        assert data['landing_page']['name'] == "Landing Page"
    
    @patch('app.services.gophish.templates.TemplatesService.get_template_details')
    def test_get_template_not_found(self, mock_get_details, client, admin_headers):
        """Test getting a non-existent template"""
        mock_get_details.return_value = None
        
        response = client.get('/api/templates/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Template not found' in data['error']
    
    def test_get_template_requires_auth(self, client, test_template):
        """Test that getting template details requires authentication"""
        response = client.get(f'/api/templates/{test_template.id}')
        
        assert response.status_code == 401
    
    def test_get_template_requires_admin(self, client, regular_headers, test_template):
        """Test that getting template details requires admin access"""
        response = client.get(f'/api/templates/{test_template.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestCreateTemplate:
    """Tests for POST /api/templates"""
    
    @patch('app.services.gophish.templates.TemplatesService.create_template')
    def test_create_template_success(self, mock_create_template, client, admin_headers):
        """Test successfully creating a template"""
        mock_create_template.return_value = {
            'status': 'success',
            'message': 'Template created successfully',
            'template': {'id': 1, 'name': 'New Template'}
        }
        
        template_data = {
            'name': 'New Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email content</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing page content</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_create_template_missing_data(self, client, admin_headers):
        """Test creating template with missing data"""
        response = client.post('/api/templates',
                              json={},
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_create_template_missing_name(self, client, admin_headers):
        """Test creating template without name"""
        template_data = {
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'missing' in data
        assert 'name' in data['missing']
    
    def test_create_template_missing_email_template_data(self, client, admin_headers):
        """Test creating template without email_template_data"""
        template_data = {
            'name': 'Test Template',
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'missing' in data
        assert 'email_template_data' in data['missing']
    
    def test_create_template_missing_landing_page_data(self, client, admin_headers):
        """Test creating template without landing_page_data"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'missing' in data
        assert 'landing_page_data' in data['missing']
    
    def test_create_template_empty_subject(self, client, admin_headers):
        """Test creating template with empty email subject"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': '',
                'html': '<html>Email</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email template subject is required' in data['error']
    
    def test_create_template_missing_email_html(self, client, admin_headers):
        """Test creating template without email HTML"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': 'Test Subject'
            },
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email template HTML is required' in data['error']
    
    def test_create_template_missing_landing_page_html(self, client, admin_headers):
        """Test creating template without landing page HTML"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email</html>'
            },
            'landing_page_data': {
                'html': ''  # Empty string, not missing
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Landing page HTML is required' in data['error']
    
    def test_create_template_requires_auth(self, client):
        """Test that creating template requires authentication"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates', json=template_data)
        
        assert response.status_code == 401
    
    def test_create_template_requires_admin(self, client, regular_headers):
        """Test that creating template requires admin access"""
        template_data = {
            'name': 'Test Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing</html>'
            }
        }
        
        response = client.post('/api/templates',
                              json=template_data,
                              headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestUpdateTemplate:
    """Tests for PUT /api/templates/<id>"""
    
    @patch('app.services.gophish.templates.TemplatesService.update_template')
    def test_update_template_success(self, mock_update_template, client, admin_headers, test_template):
        """Test successfully updating a template"""
        mock_update_template.return_value = {
            'status': 'success',
            'message': 'Template updated successfully'
        }
        
        update_data = {
            'name': 'Updated Template',
            'email_template_data': {
                'subject': 'Updated Subject',
                'html': '<html>Updated Email</html>'
            },
            'landing_page_data': {
                'html': '<html>Updated Landing</html>'
            }
        }
        
        response = client.put(f'/api/templates/{test_template.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    @patch('app.services.gophish.templates.TemplatesService.update_template')
    def test_update_template_partial(self, mock_update_template, client, admin_headers, test_template):
        """Test updating template with partial data"""
        mock_update_template.return_value = {
            'status': 'success',
            'message': 'Template updated successfully'
        }
        
        update_data = {
            'name': 'Updated Name'
        }
        
        response = client.put(f'/api/templates/{test_template.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_update_template_no_data(self, client, admin_headers, test_template):
        """Test updating template with no data"""
        response = client.put(f'/api/templates/{test_template.id}',
                             json={},
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_update_template_empty_subject(self, client, admin_headers, test_template):
        """Test updating template with empty email subject"""
        update_data = {
            'email_template_data': {
                'subject': '',
                'html': '<html>Email</html>'
            }
        }
        
        response = client.put(f'/api/templates/{test_template.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email template subject is required' in data['error']
    
    def test_update_template_requires_auth(self, client, test_template):
        """Test that updating template requires authentication"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/templates/{test_template.id}', json=update_data)
        
        assert response.status_code == 401
    
    def test_update_template_requires_admin(self, client, regular_headers, test_template):
        """Test that updating template requires admin access"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/templates/{test_template.id}',
                             json=update_data,
                             headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestDeleteTemplate:
    """Tests for DELETE /api/templates/<id>"""
    
    @patch('app.services.gophish.templates.TemplatesService.delete_template')
    def test_delete_template_success(self, mock_delete_template, client, admin_headers, test_template):
        """Test successfully deleting a template"""
        mock_delete_template.return_value = {
            'status': 'success',
            'message': 'Template deleted successfully'
        }
        
        response = client.delete(f'/api/templates/{test_template.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    @patch('app.services.gophish.templates.TemplatesService.delete_template')
    def test_delete_template_not_found(self, mock_delete_template, client, admin_headers):
        """Test deleting a non-existent template"""
        mock_delete_template.return_value = {
            'status': 'error',
            'message': 'Template not found'
        }
        
        response = client.delete('/api/templates/99999', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_delete_template_requires_auth(self, client, test_template):
        """Test that deleting template requires authentication"""
        response = client.delete(f'/api/templates/{test_template.id}')
        
        assert response.status_code == 401
    
    def test_delete_template_requires_admin(self, client, regular_headers, test_template):
        """Test that deleting template requires admin access"""
        response = client.delete(f'/api/templates/{test_template.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']
