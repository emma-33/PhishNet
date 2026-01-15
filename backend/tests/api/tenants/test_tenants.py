"""
Tests for Tenant API endpoints
"""
import pytest
from unittest.mock import Mock, patch
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, TenantInvitation, TenantInvitation


@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    tenant = Tenant(name="Admin Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    
    password_hash = bcrypt.generate_password_hash("adminpassword123").decode('utf-8')
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        tenant_id=tenant.id,
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create a regular (non-admin) user"""
    tenant = Tenant(name="Regular Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    
    password_hash = bcrypt.generate_password_hash("userpassword123").decode('utf-8')
    user = User(
        email="user@example.com",
        first_name="Regular",
        last_name="User",
        password_hash=password_hash,
        tenant_id=tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_tenant(db_session):
    """Create another test tenant"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


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


class TestCreateTenant:
    """Tests for POST /api/tenants"""
    
    @patch('app.api.tenants.tenants.create_tenant')
    def test_create_tenant_success(self, mock_create_tenant, client, admin_headers, db_session):
        """Test successfully creating a tenant"""
        # Create mock tenant and invitation (not in DB to avoid conflicts)
        tenant = Tenant(name="New Tenant")
        invitation = TenantInvitation(
            invitation_code="test-invitation-code-12345",
            tenant_id=1,
            is_used=False,
            expires_at=None
        )
        
        mock_create_tenant.return_value = {
            'status': 'success',
            'message': 'Tenant created successfully',
            'tenant': tenant,
            'invitation': invitation
        }
        
        tenant_data = {
            'name': 'New Tenant'
        }
        
        response = client.post('/api/tenants',
                              json=tenant_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'tenant' in data
        assert 'invitation' in data
        assert data['tenant']['name'] == tenant.name
        assert data['invitation']['invitation_code'] == invitation.invitation_code
    
    @patch('app.api.tenants.tenants.create_tenant')
    def test_create_tenant_with_expiration(self, mock_create_tenant, client, admin_headers):
        """Test creating tenant with invitation expiration"""
        tenant = Tenant(name="New Tenant")
        invitation = TenantInvitation(
            invitation_code="test-code",
            tenant_id=1,
            is_used=False,
            expires_at=None
        )
        
        mock_create_tenant.return_value = {
            'status': 'success',
            'message': 'Tenant created successfully',
            'tenant': tenant,
            'invitation': invitation
        }
        
        tenant_data = {
            'name': 'New Tenant',
            'invitation_expires_days': 7
        }
        
        response = client.post('/api/tenants',
                              json=tenant_data,
                              headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'invitation' in data
    
    def test_create_tenant_missing_data(self, client, admin_headers):
        """Test creating tenant with missing data"""
        response = client.post('/api/tenants',
                              json={},
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_create_tenant_missing_name(self, client, admin_headers):
        """Test creating tenant without name"""
        response = client.post('/api/tenants',
                              json={'invitation_expires_days': 7},
                              headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required field' in data['error']
    
    @patch('app.api.tenants.tenants.create_tenant')
    def test_create_tenant_duplicate_name(self, mock_create_tenant, client, admin_headers):
        """Test creating tenant with duplicate name"""
        mock_create_tenant.return_value = {
            'status': 'error',
            'message': 'Tenant with name "Existing Tenant" already exists',
            'tenant': None,
            'invitation': None
        }
        
        tenant_data = {
            'name': 'Existing Tenant'
        }
        
        response = client.post('/api/tenants',
                              json=tenant_data,
                              headers=admin_headers)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'Existing Tenant' in data['error']
    
    def test_create_tenant_requires_auth(self, client):
        """Test that creating tenant requires authentication"""
        tenant_data = {'name': 'New Tenant'}
        
        response = client.post('/api/tenants', json=tenant_data)
        
        assert response.status_code == 401
    
    def test_create_tenant_requires_admin(self, client, regular_headers):
        """Test that creating tenant requires admin access"""
        tenant_data = {'name': 'New Tenant'}
        
        response = client.post('/api/tenants',
                              json=tenant_data,
                              headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestGetAllTenants:
    """Tests for GET /api/tenants"""
    
    def test_get_all_tenants_success(self, client, admin_headers, test_tenant, another_tenant):
        """Test successfully getting all tenants"""
        response = client.get('/api/tenants', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tenants' in data
        assert isinstance(data['tenants'], list)
        assert len(data['tenants']) >= 2
        
        # Check tenant fields
        tenant_dicts = {t['id']: t for t in data['tenants']}
        assert test_tenant.id in tenant_dicts
        assert another_tenant.id in tenant_dicts
        assert tenant_dicts[test_tenant.id]['name'] == test_tenant.name
    
    def test_get_all_tenants_empty(self, client, admin_headers):
        """Test getting all tenants when none exist (except fixtures)"""
        response = client.get('/api/tenants', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tenants' in data
        assert isinstance(data['tenants'], list)
    
    def test_get_all_tenants_fields(self, client, admin_headers, test_tenant):
        """Test that tenant response includes correct fields"""
        response = client.get('/api/tenants', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Find test tenant
        test_tenant_dict = next(t for t in data['tenants'] if t['id'] == test_tenant.id)
        
        assert 'id' in test_tenant_dict
        assert 'name' in test_tenant_dict
        assert 'gophish_group_id' in test_tenant_dict
        assert 'created_at' in test_tenant_dict
    
    def test_get_all_tenants_requires_auth(self, client):
        """Test that getting tenants requires authentication"""
        response = client.get('/api/tenants')
        
        assert response.status_code == 401
    
    def test_get_all_tenants_requires_admin(self, client, regular_headers):
        """Test that getting tenants requires admin access"""
        response = client.get('/api/tenants', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestGetTenant:
    """Tests for GET /api/tenants/<id>"""
    
    def test_get_tenant_success(self, client, admin_headers, test_tenant):
        """Test successfully getting a tenant by ID"""
        response = client.get(f'/api/tenants/{test_tenant.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_tenant.id
        assert data['name'] == test_tenant.name
        assert data['gophish_group_id'] == test_tenant.gophish_group_id
    
    def test_get_tenant_not_found(self, client, admin_headers):
        """Test getting a non-existent tenant"""
        response = client.get('/api/tenants/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant not found' in data['error']
    
    def test_get_tenant_requires_auth(self, client, test_tenant):
        """Test that getting a tenant requires authentication"""
        response = client.get(f'/api/tenants/{test_tenant.id}')
        
        assert response.status_code == 401
    
    def test_get_tenant_requires_admin(self, client, regular_headers, test_tenant):
        """Test that getting a tenant requires admin access"""
        response = client.get(f'/api/tenants/{test_tenant.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestUpdateTenant:
    """Tests for PUT /api/tenants/<id>"""
    
    def test_update_tenant_success(self, client, admin_headers, test_tenant):
        """Test successfully updating a tenant"""
        update_data = {
            'name': 'Updated Tenant Name'
        }
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['tenant']['name'] == update_data['name']
    
    def test_update_tenant_not_found(self, client, admin_headers):
        """Test updating a non-existent tenant"""
        update_data = {'name': 'Updated'}
        
        response = client.put('/api/tenants/99999',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant not found' in data['error']
    
    def test_update_tenant_no_data(self, client, admin_headers, test_tenant):
        """Test updating tenant with no data"""
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json={},
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_update_tenant_empty_name(self, client, admin_headers, test_tenant):
        """Test updating tenant with empty name"""
        update_data = {
            'name': '   '
        }
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant name cannot be empty' in data['error']
    
    def test_update_tenant_duplicate_name(self, client, admin_headers, test_tenant, another_tenant):
        """Test updating tenant with duplicate name"""
        update_data = {
            'name': another_tenant.name
        }
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant with this name already exists' in data['error']
    
    def test_update_tenant_same_name(self, client, admin_headers, test_tenant):
        """Test updating tenant with same name (should succeed)"""
        update_data = {
            'name': test_tenant.name
        }
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_update_tenant_no_fields(self, client, admin_headers, test_tenant):
        """Test updating tenant with no valid fields to update"""
        # Send data with fields that aren't 'name'
        update_data = {
            'gophish_group_id': 123
        }
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No fields to update' in data['error']
    
    def test_update_tenant_requires_auth(self, client, test_tenant):
        """Test that updating tenant requires authentication"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/tenants/{test_tenant.id}', json=update_data)
        
        assert response.status_code == 401
    
    def test_update_tenant_requires_admin(self, client, regular_headers, test_tenant):
        """Test that updating tenant requires admin access"""
        update_data = {'name': 'Updated'}
        
        response = client.put(f'/api/tenants/{test_tenant.id}',
                             json=update_data,
                             headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']


class TestDeleteTenant:
    """Tests for DELETE /api/tenants/<id>"""
    
    def test_delete_tenant_success(self, client, admin_headers, db_session):
        """Test successfully deleting a tenant"""
        # Create tenant without users
        tenant = Tenant(name="To Delete")
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)
        
        response = client.delete(f'/api/tenants/{tenant.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        
        # Verify tenant is deleted
        from app.repository.tenant_repository import TenantRepository
        tenant_repo = TenantRepository()
        deleted_tenant = tenant_repo.get_by_id(tenant.id)
        assert deleted_tenant is None
    
    def test_delete_tenant_not_found(self, client, admin_headers):
        """Test deleting a non-existent tenant"""
        response = client.delete('/api/tenants/99999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant not found' in data['error']
    
    def test_delete_tenant_with_users(self, client, admin_headers, test_tenant, db_session):
        """Test that tenant with users cannot be deleted"""
        # Create a user in the tenant
        password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password_hash=password_hash,
            tenant_id=test_tenant.id,
            is_active=True,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.delete(f'/api/tenants/{test_tenant.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Cannot delete tenant with associated users' in data['error']
        assert 'users' in data
    
    def test_delete_tenant_with_inactive_users(self, client, admin_headers, test_tenant, db_session):
        """Test that tenant with inactive users cannot be deleted"""
        # Create an inactive user in the tenant
        password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
        user = User(
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            password_hash=password_hash,
            tenant_id=test_tenant.id,
            is_active=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.delete(f'/api/tenants/{test_tenant.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Cannot delete tenant with associated users' in data['error']
    
    def test_delete_tenant_requires_auth(self, client, test_tenant):
        """Test that deleting tenant requires authentication"""
        response = client.delete(f'/api/tenants/{test_tenant.id}')
        
        assert response.status_code == 401
    
    def test_delete_tenant_requires_admin(self, client, regular_headers, test_tenant):
        """Test that deleting tenant requires admin access"""
        response = client.delete(f'/api/tenants/{test_tenant.id}', headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Admin access required' in data['error']
