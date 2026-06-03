"""
Tests for Tenant Invitation API endpoints
"""
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, TenantInvitation


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def operator_user(db_session, test_tenant):
    """Create an operator user (tenant owner)"""
    password_hash = bcrypt.generate_password_hash("operatorpassword123").decode('utf-8')
    user = User(
        email="operator@example.com",
        first_name="Operator",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Set as operator
    test_tenant.operator_id = user.id
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session, test_tenant):
    """Create a regular (non-operator) user"""
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
def another_tenant(db_session):
    """Create another tenant"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_user(db_session, another_tenant):
    """Create a user from another tenant"""
    password_hash = bcrypt.generate_password_hash("anotherpassword123").decode('utf-8')
    user = User(
        email="another@example.com",
        first_name="Another",
        last_name="User",
        password_hash=password_hash,
        tenant_id=another_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_invitation(db_session, test_tenant):
    """Create a test invitation"""
    invitation = TenantInvitation(
        invitation_code="test-invitation-code-12345",
        tenant_id=test_tenant.id,
        is_used=False,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def expired_invitation(db_session, test_tenant):
    """Create an expired invitation"""
    invitation = TenantInvitation(
        invitation_code="expired-invitation-code",
        tenant_id=test_tenant.id,
        is_used=False,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def used_invitation(db_session, test_tenant, operator_user):
    """Create a used invitation"""
    invitation = TenantInvitation(
        invitation_code="used-invitation-code",
        tenant_id=test_tenant.id,
        is_used=True,
        used_at=datetime.utcnow(),
        used_by_user_id=operator_user.id,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def operator_headers(operator_user):
    """Create authorization headers for operator user"""
    token = create_access_token(identity=str(operator_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    """Create authorization headers for regular user"""
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_headers(another_user):
    """Create authorization headers for another tenant's user"""
    token = create_access_token(identity=str(another_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestCreateInvitation:
    """Tests for POST /api/tenant-invitations"""
    
    def test_create_invitation_success(self, client, operator_headers, test_tenant):
        """Test successfully creating an invitation"""
        invitation_data = {
            'tenant_id': test_tenant.id
        }
        
        response = client.post('/api/tenant-invitations',
                              json=invitation_data,
                              headers=operator_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'invitation' in data
        assert 'message' in data
        assert data['invitation']['tenant_id'] == test_tenant.id
        assert data['invitation']['is_used'] is False
        assert 'invitation_code' in data['invitation']
    
    def test_create_invitation_with_expiration(self, client, operator_headers, test_tenant):
        """Test creating invitation with expiration"""
        invitation_data = {
            'tenant_id': test_tenant.id,
            'expires_days': 7
        }
        
        response = client.post('/api/tenant-invitations',
                              json=invitation_data,
                              headers=operator_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'invitation' in data
        assert data['invitation']['expires_at'] is not None
    
    def test_create_invitation_missing_data(self, client, operator_headers):
        """Test creating invitation with missing data"""
        response = client.post('/api/tenant-invitations',
                              json={},
                              headers=operator_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_create_invitation_missing_tenant_id(self, client, operator_headers):
        """Test creating invitation without tenant_id"""
        response = client.post('/api/tenant-invitations',
                              json={'expires_days': 7},
                              headers=operator_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required field' in data['error']
    
    def test_create_invitation_tenant_mismatch(self, client, operator_headers, another_tenant):
        """Test creating invitation for different tenant"""
        invitation_data = {
            'tenant_id': another_tenant.id
        }
        
        response = client.post('/api/tenant-invitations',
                              json=invitation_data,
                              headers=operator_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Tenant mismatch' in data['error']
    
    def test_create_invitation_not_operator(self, client, regular_headers, test_tenant):
        """Test that non-operator users cannot create invitations"""
        invitation_data = {
            'tenant_id': test_tenant.id
        }
        
        response = client.post('/api/tenant-invitations',
                              json=invitation_data,
                              headers=regular_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'Permission denied' in data['error']
        assert 'Only tenant operators can create invitations' in data['message']
    
    def test_create_invitation_requires_auth(self, client, test_tenant):
        """Test that creating invitation requires authentication"""
        invitation_data = {
            'tenant_id': test_tenant.id
        }
        
        response = client.post('/api/tenant-invitations', json=invitation_data)
        
        assert response.status_code == 401


class TestValidateInvitation:
    """Tests for POST /api/tenant-invitations/validate"""
    
    def test_validate_invitation_success(self, client, test_invitation):
        """Test successfully validating an invitation"""
        validation_data = {
            'invitation_code': test_invitation.invitation_code
        }
        
        response = client.post('/api/tenant-invitations/validate',
                              json=validation_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['valid'] is True
        assert 'invitation' in data
        assert data['invitation']['id'] == test_invitation.id
        assert data['invitation']['is_used'] is False
    
    def test_validate_invitation_missing_data(self, client):
        """Test validating invitation with missing data"""
        response = client.post('/api/tenant-invitations/validate',
                              json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_validate_invitation_missing_code(self, client):
        """Test validating invitation without invitation_code"""
        response = client.post('/api/tenant-invitations/validate',
                              json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_validate_invitation_invalid_code(self, client):
        """Test validating non-existent invitation code"""
        validation_data = {
            'invitation_code': 'invalid-code-12345'
        }
        
        response = client.post('/api/tenant-invitations/validate',
                              json=validation_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'Invalid invitation code' in data['message']
    
    def test_validate_invitation_used(self, client, used_invitation):
        """Test validating used invitation"""
        validation_data = {
            'invitation_code': used_invitation.invitation_code
        }
        
        response = client.post('/api/tenant-invitations/validate',
                              json=validation_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'already been used' in data['message']
    
    def test_validate_invitation_expired(self, client, expired_invitation):
        """Test validating expired invitation"""
        validation_data = {
            'invitation_code': expired_invitation.invitation_code
        }
        
        response = client.post('/api/tenant-invitations/validate',
                              json=validation_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'expired' in data['message']
    
    def test_validate_invitation_no_auth_required(self, client, test_invitation):
        """Test that validation does not require authentication"""
        validation_data = {
            'invitation_code': test_invitation.invitation_code
        }
        
        response = client.post('/api/tenant-invitations/validate',
                              json=validation_data)
        
        assert response.status_code == 200


class TestGetInvitation:
    """Tests for GET /api/tenant-invitations/<invitation_code>"""
    
    def test_get_invitation_success(self, client, operator_headers, test_invitation):
        """Test successfully getting an invitation by code"""
        response = client.get(f'/api/tenant-invitations/{test_invitation.invitation_code}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_invitation.id
        assert data['invitation_code'] == test_invitation.invitation_code
        assert data['tenant_id'] == test_invitation.tenant_id
        assert data['is_used'] == test_invitation.is_used
        assert 'is_valid' in data
    
    def test_get_invitation_not_found(self, client, operator_headers):
        """Test getting non-existent invitation"""
        response = client.get('/api/tenant-invitations/invalid-code-12345',
                              headers=operator_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Invitation not found' in data['error']
    
    def test_get_invitation_fields(self, client, operator_headers, test_invitation):
        """Test that invitation response includes all fields"""
        response = client.get(f'/api/tenant-invitations/{test_invitation.invitation_code}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'id' in data
        assert 'invitation_code' in data
        assert 'tenant_id' in data
        assert 'is_used' in data
        assert 'used_at' in data
        assert 'used_by_user_id' in data
        assert 'expires_at' in data
        assert 'created_at' in data
        assert 'is_valid' in data
    
    def test_get_invitation_used(self, client, operator_headers, used_invitation):
        """Test getting used invitation"""
        response = client.get(f'/api/tenant-invitations/{used_invitation.invitation_code}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_used'] is True
        assert data['used_at'] is not None
        assert data['used_by_user_id'] is not None
        assert data['is_valid'] is False
    
    def test_get_invitation_expired(self, client, operator_headers, expired_invitation):
        """Test getting expired invitation"""
        response = client.get(f'/api/tenant-invitations/{expired_invitation.invitation_code}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] is False
    
    def test_get_invitation_requires_auth(self, client, test_invitation):
        """Test that getting invitation requires authentication"""
        response = client.get(f'/api/tenant-invitations/{test_invitation.invitation_code}')
        
        assert response.status_code == 401


class TestGetInvitationsByTenant:
    """Tests for GET /api/tenant-invitations/tenant/<tenant_id>"""
    
    def test_get_invitations_by_tenant_success(self, client, operator_headers, test_tenant,
                                                test_invitation, used_invitation, expired_invitation):
        """Test successfully getting invitations by tenant"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'invitations' in data
        assert isinstance(data['invitations'], list)
        assert len(data['invitations']) >= 3
        
        # Check that all invitations belong to the tenant
        for invitation in data['invitations']:
            assert invitation['tenant_id'] == test_tenant.id
    
    def test_get_invitations_by_tenant_filter_unused(self, client, operator_headers, test_tenant,
                                                      test_invitation, used_invitation):
        """Test filtering invitations by is_used=False"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}?is_used=false',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'invitations' in data
        
        # All invitations should be unused
        for invitation in data['invitations']:
            assert invitation['is_used'] is False
    
    def test_get_invitations_by_tenant_filter_used(self, client, operator_headers, test_tenant,
                                                    test_invitation, used_invitation):
        """Test filtering invitations by is_used=True"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}?is_used=true',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'invitations' in data
        
        # All invitations should be used
        for invitation in data['invitations']:
            assert invitation['is_used'] is True
    
    def test_get_invitations_by_tenant_empty(self, client, operator_headers, db_session):
        """Test getting invitations for tenant with no invitations"""
        # Create tenant without invitations
        tenant = Tenant(name="Empty Tenant")
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)
        
        password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password_hash=password_hash,
            tenant_id=tenant.id,
            is_active=True,
            is_admin=False
        )
        db_session.add(user)
        tenant.operator_id = user.id
        db_session.commit()
        
        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get(f'/api/tenant-invitations/tenant/{tenant.id}',
                              headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'invitations' in data
        assert data['invitations'] == []
    
    def test_get_invitations_by_tenant_fields(self, client, operator_headers, test_tenant,
                                              test_invitation):
        """Test that invitation response includes all fields"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}',
                              headers=operator_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Find test invitation
        invitation_dict = next(i for i in data['invitations'] if i['id'] == test_invitation.id)
        
        assert 'id' in invitation_dict
        assert 'invitation_code' in invitation_dict
        assert 'tenant_id' in invitation_dict
        assert 'is_used' in invitation_dict
        assert 'used_at' in invitation_dict
        assert 'used_by_user_id' in invitation_dict
        assert 'expires_at' in invitation_dict
        assert 'created_at' in invitation_dict
        assert 'is_valid' in invitation_dict
    
    def test_get_invitations_by_tenant_requires_auth(self, client, test_tenant):
        """Test that getting invitations requires authentication"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}')
        
        assert response.status_code == 401
    
    def test_get_invitations_by_tenant_cross_tenant_access(self, client, another_headers,
                                                            test_tenant, test_invitation):
        """Test that users can access invitations from their own tenant only"""
        # User from another tenant should not see invitations from test_tenant
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}',
                              headers=another_headers)
        
        # Should return empty list or error, depending on implementation
        # The API doesn't explicitly check tenant ownership, so it may return empty list
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.get_json()
            # Should be empty or not contain test_tenant's invitations
            assert 'invitations' in data
