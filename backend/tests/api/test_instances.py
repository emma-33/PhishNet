"""
Tests for Instance API endpoints
"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, Instance, Campaign, CampaignStatus, Template
from app.repository.instance_repository import InstanceRepository
from app.repository.campaign_repository import CampaignRepository
from app.repository.template_repository import TemplateMapRepository


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
def admin_headers(admin_user):
    """Create authorization headers with admin JWT token"""
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    """Create authorization headers with regular user JWT token"""
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_instance(db_session):
    """Create a test Gophish instance"""
    instance = Instance(
        name="Test Instance",
        base_url="https://test-gophish.example.com",
        api_key="test-api-key-12345",
        redirect_url="https://test-redirect.example.com",
        is_active=True
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


@pytest.fixture
def another_instance(db_session):
    """Create another test instance"""
    instance = Instance(
        name="Another Instance",
        base_url="https://another-gophish.example.com",
        api_key="another-api-key-67890",
        redirect_url="https://another-redirect.example.com",
        is_active=False
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


class TestGetAllInstances:
    """Tests for GET /api/instances"""
    
    def test_get_all_instances_success(self, client, admin_headers, test_instance, another_instance):
        """Test successfully getting all instances as admin"""
        response = client.get('/api/instances', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'instances' in data
        assert isinstance(data['instances'], list)
        assert len(data['instances']) == 2
        
        # Check API keys are masked (mask all but last 4 characters)
        instance_dicts = {inst['id']: inst for inst in data['instances']}
        assert instance_dicts[test_instance.id]['api_key'] == '**************2345'
        assert instance_dicts[another_instance.id]['api_key'] == '*****************7890'  # 21 chars -> 17 stars + 7890
    
    def test_get_all_instances_empty(self, client, admin_headers):
        """Test getting all instances when none exist"""
        response = client.get('/api/instances', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'instances' in data
        assert data['instances'] == []
    
    def test_get_all_instances_requires_auth(self, client):
        """Test that getting instances requires authentication"""
        response = client.get('/api/instances')
        
        assert response.status_code == 401
    
    def test_get_all_instances_requires_admin(self, client, regular_headers):
        """Test that getting instances requires admin access"""
        response = client.get('/api/instances', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestGetInstance:
    """Tests for GET /api/instances/<id>"""
    
    def test_get_instance_success(self, client, admin_headers, test_instance):
        """Test successfully getting an instance by ID"""
        response = client.get(f'/api/instances/{test_instance.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_instance.id
        assert data['name'] == test_instance.name
        assert data['base_url'] == test_instance.base_url
        assert data['api_key'] == '**************2345'  # Masked (all but last 4 chars)
        assert data['is_active'] == test_instance.is_active
        assert data['redirect_url'] == test_instance.redirect_url
    
    def test_get_instance_not_found(self, client, admin_headers):
        """Test getting a non-existent instance"""
        response = client.get('/api/instances/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Instance not found' in data['error']
    
    def test_get_instance_requires_auth(self, client, test_instance):
        """Test that getting an instance requires authentication"""
        response = client.get(f'/api/instances/{test_instance.id}')
        
        assert response.status_code == 401
    
    def test_get_instance_requires_admin(self, client, regular_headers, test_instance):
        """Test that getting an instance requires admin access"""
        response = client.get(f'/api/instances/{test_instance.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestCreateInstance:
    """Tests for POST /api/instances"""
    
    def test_create_instance_success(self, client, admin_headers):
        """Test successfully creating an instance"""
        instance_data = {
            'name': 'New Instance',
            'base_url': 'https://new-instance.example.com',
            'api_key': 'new-api-key-abcdef',
            'redirect_url': 'https://new-redirect.example.com',
            'is_active': True
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'instance' in data
        assert data['instance']['name'] == instance_data['name']
        assert data['instance']['api_key'] == '**************cdef'  # Masked (18 chars -> 14 stars + cdef)
    
    def test_create_instance_missing_data(self, client, admin_headers):
        """Test creating instance with missing data"""
        response = client.post('/api/instances',
                              json={},
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_create_instance_missing_name(self, client, admin_headers):
        """Test creating instance without name"""
        instance_data = {
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'missing' in data
        assert 'name' in data['missing']
    
    def test_create_instance_invalid_base_url(self, client, admin_headers):
        """Test creating instance with invalid base_url"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'invalid-url',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid base_url' in data['error']
    
    def test_create_instance_invalid_redirect_url(self, client, admin_headers):
        """Test creating instance with invalid redirect_url"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'invalid-url'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid redirect_url' in data['error']
    
    def test_create_instance_duplicate_name(self, client, admin_headers, test_instance):
        """Test creating instance with duplicate name"""
        instance_data = {
            'name': test_instance.name,
            'base_url': 'https://different.example.com',
            'api_key': 'different-key',
            'redirect_url': 'https://different-redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Instance with this name already exists' in data['error']
    
    def test_create_instance_strips_base_url_trailing_slash(self, client, admin_headers):
        """Test that base_url trailing slash is stripped"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'https://test.example.com/',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['instance']['base_url'] == 'https://test.example.com'
    
    def test_create_instance_defaults_is_active(self, client, admin_headers):
        """Test that is_active defaults to True"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['instance']['is_active'] is True
    
    def test_create_instance_requires_auth(self, client):
        """Test that creating instance requires authentication"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances', json=instance_data)
        
        assert response.status_code == 401
    
    def test_create_instance_requires_admin(self, client, regular_headers):
        """Test that creating instance requires admin access"""
        instance_data = {
            'name': 'Test Instance',
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }
        
        response = client.post('/api/instances',
                              json=instance_data,
                              headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestUpdateInstance:
    """Tests for PUT /api/instances/<id>"""
    
    def test_update_instance_success(self, client, admin_headers, test_instance):
        """Test successfully updating an instance"""
        update_data = {
            'name': 'Updated Instance',
            'base_url': 'https://updated.example.com',
            'api_key': 'updated-api-key',
            'is_active': False,
            'redirect_url': 'https://updated-redirect.example.com'
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['instance']['name'] == update_data['name']
        assert data['instance']['base_url'] == update_data['base_url']
        assert data['instance']['is_active'] == update_data['is_active']
    
    def test_update_instance_partial(self, client, admin_headers, test_instance):
        """Test updating instance with partial data"""
        update_data = {
            'name': 'Partially Updated'
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['instance']['name'] == update_data['name']
        # Other fields should remain unchanged
        assert data['instance']['base_url'] == test_instance.base_url
    
    def test_update_instance_not_found(self, client, admin_headers):
        """Test updating a non-existent instance"""
        update_data = {'name': 'Updated'}
        
        response = client.put('/api/instances/99999',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Instance not found' in data['error']
    
    def test_update_instance_no_data(self, client, admin_headers, test_instance):
        """Test updating instance with no data"""
        response = client.put(f'/api/instances/{test_instance.id}',
                             json={},
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_update_instance_invalid_base_url(self, client, admin_headers, test_instance):
        """Test updating instance with invalid base_url"""
        update_data = {
            'base_url': 'invalid-url'
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid base_url' in data['error']
    
    def test_update_instance_invalid_redirect_url(self, client, admin_headers, test_instance):
        """Test updating instance with invalid redirect_url"""
        update_data = {
            'redirect_url': 'invalid-url'
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid redirect_url' in data['error']
    
    def test_update_instance_empty_redirect_url(self, client, admin_headers, test_instance):
        """Test updating instance with empty redirect_url"""
        update_data = {
            'redirect_url': ''
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid redirect_url' in data['error']
    
    def test_update_instance_duplicate_name(self, client, admin_headers, test_instance, another_instance):
        """Test updating instance with duplicate name"""
        update_data = {
            'name': another_instance.name
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Instance with this name already exists' in data['error']
    
    def test_update_instance_same_name(self, client, admin_headers, test_instance):
        """Test updating instance with same name (should succeed)"""
        update_data = {
            'name': test_instance.name
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
    
    def test_update_instance_strips_base_url_trailing_slash(self, client, admin_headers, test_instance):
        """Test that base_url trailing slash is stripped on update"""
        update_data = {
            'base_url': 'https://updated.example.com/'
        }
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['instance']['base_url'] == 'https://updated.example.com'
    
    def test_update_instance_requires_auth(self, client, test_instance):
        """Test that updating instance requires authentication"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/instances/{test_instance.id}', json=update_data)
        
        assert response.status_code == 401
    
    def test_update_instance_requires_admin(self, client, regular_headers, test_instance):
        """Test that updating instance requires admin access"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/instances/{test_instance.id}',
                             json=update_data,
                             headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestDeleteInstance:
    """Tests for DELETE /api/instances/<id>"""
    
    def test_delete_instance_success(self, client, admin_headers, db_session):
        """Test successfully deleting an instance"""
        # Create instance without any dependencies
        instance = Instance(
            name="To Delete",
            base_url="https://delete.example.com",
            api_key="delete-key",
            redirect_url="https://delete-redirect.example.com",
            is_active=True
        )
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)
        
        response = client.delete(f'/api/instances/{instance.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        
        # Verify instance is deleted
        instance_repo = InstanceRepository()
        deleted_instance = instance_repo.get_by_id(instance.id)
        assert deleted_instance is None
    
    def test_delete_instance_not_found(self, client, admin_headers):
        """Test deleting a non-existent instance"""
        response = client.delete('/api/instances/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Instance not found' in data['error']
    
    def test_delete_instance_with_running_campaigns(self, client, admin_headers, test_instance,
                                                     db_session, test_tenant, admin_user, test_template):
        """Test that instance with running campaigns cannot be deleted"""
        # Create a running campaign
        campaign = Campaign(
            name="Running Campaign",
            tenant_id=test_tenant.id,
            created_by_user_id=admin_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=1,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(campaign)
        db_session.commit()
        
        response = client.delete(f'/api/instances/{test_instance.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Cannot delete instance with running campaigns' in data['error']
        assert 'running_campaigns' in data
    
    def test_delete_instance_with_campaigns(self, client, admin_headers, test_instance,
                                             db_session, test_tenant, admin_user, test_template):
        """Test that instance with campaigns cannot be deleted"""
        # Create a stopped campaign
        campaign = Campaign(
            name="Stopped Campaign",
            tenant_id=test_tenant.id,
            created_by_user_id=admin_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=1,
            status=CampaignStatus.STOPPED,
            template_id=test_template.id
        )
        db_session.add(campaign)
        db_session.commit()
        
        response = client.delete(f'/api/instances/{test_instance.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Cannot delete instance with associated campaigns' in data['error']
        assert 'campaigns' in data
    
    def test_delete_instance_with_templates(self, client, admin_headers, test_instance,
                                           db_session, admin_user):
        """Test that instance with templates cannot be deleted"""
        # Create a template
        template = Template(
            name="Test Template",
            gophish_instance_id=test_instance.id,
            gophish_email_template_id=1,
            gophish_landing_page_id=1,
            created_by_user_id=admin_user.id
        )
        db_session.add(template)
        db_session.commit()
        
        response = client.delete(f'/api/instances/{test_instance.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Cannot delete instance with associated templates' in data['error']
        assert 'templates' in data
    
    def test_delete_instance_requires_auth(self, client, test_instance):
        """Test that deleting instance requires authentication"""
        response = client.delete(f'/api/instances/{test_instance.id}')
        
        assert response.status_code == 401
    
    def test_delete_instance_requires_admin(self, client, regular_headers, test_instance):
        """Test that deleting instance requires admin access"""
        response = client.delete(f'/api/instances/{test_instance.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestToggleInstanceStatus:
    """Tests for PATCH /api/instances/<id>/toggle"""
    
    def test_toggle_instance_status_activate(self, client, admin_headers, another_instance):
        """Test activating an inactive instance"""
        assert another_instance.is_active is False
        
        response = client.patch(f'/api/instances/{another_instance.id}/toggle',
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'activated' in data['message']
        assert data['instance']['is_active'] is True
    
    def test_toggle_instance_status_deactivate(self, client, admin_headers, test_instance):
        """Test deactivating an active instance"""
        assert test_instance.is_active is True
        
        response = client.patch(f'/api/instances/{test_instance.id}/toggle',
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'deactivated' in data['message']
        assert data['instance']['is_active'] is False
    
    def test_toggle_instance_status_not_found(self, client, admin_headers):
        """Test toggling status of non-existent instance"""
        response = client.patch('/api/instances/99999/toggle',
                               headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Instance not found' in data['error']
    
    def test_toggle_instance_status_requires_auth(self, client, test_instance):
        """Test that toggling instance status requires authentication"""
        response = client.patch(f'/api/instances/{test_instance.id}/toggle')
        
        assert response.status_code == 401
    
    def test_toggle_instance_status_requires_admin(self, client, regular_headers, test_instance):
        """Test that toggling instance status requires admin access"""
        response = client.patch(f'/api/instances/{test_instance.id}/toggle',
                               headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']
