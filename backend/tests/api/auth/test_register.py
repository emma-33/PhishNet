"""
Tests for Register API endpoint
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

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
def valid_invitation(db_session, test_tenant):
    """Create a valid invitation"""
    invitation = TenantInvitation(
        invitation_code="valid-invitation-code-12345",
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
def used_invitation(db_session, test_tenant):
    """Create a used invitation"""
    invitation = TenantInvitation(
        invitation_code="used-invitation-code",
        tenant_id=test_tenant.id,
        is_used=True,
        used_at=datetime.utcnow(),
        used_by_user_id=1,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def existing_user(db_session, test_tenant):
    """Create an existing user"""
    password_hash = bcrypt.generate_password_hash("existingpassword123").decode('utf-8')
    user = User(
        email="existing@example.com",
        first_name="Existing",
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


class TestRegister:
    """Tests for POST /api/auth/register"""
    
    @patch('app.api.auth.register.GroupsService')
    def test_register_success(self, mock_groups_service, client, test_tenant, valid_invitation):
        """Test successfully registering a user"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'message' in data
        assert data['message'] == 'User registered successfully'
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == register_data['email']
        assert data['user']['first_name'] == register_data['first_name']
        assert data['user']['last_name'] == register_data['last_name']
        assert data['user']['tenant_id'] == test_tenant.id
        assert data['user']['is_admin'] is False
    
    @patch('app.api.auth.register.GroupsService')
    def test_register_first_user_becomes_operator(self, mock_groups_service, client, db_session, test_tenant, valid_invitation):
        """Test that first user becomes operator"""
        # Ensure tenant has no operator
        test_tenant.operator_id = None
        db_session.commit()
        
        register_data = {
            'email': 'firstuser@example.com',
            'first_name': 'First',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['is_operator'] is True
        
        # Verify tenant operator was set
        db_session.refresh(test_tenant)
        from app.repository.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_email('firstuser@example.com')
        assert test_tenant.operator_id == user.id
    
    @patch('app.api.auth.register.GroupsService')
    def test_register_user_fields(self, mock_groups_service, client, test_tenant, valid_invitation):
        """Test that register response includes all user fields"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 201
        data = response.get_json()
        user = data['user']
        
        assert 'id' in user
        assert 'email' in user
        assert 'first_name' in user
        assert 'last_name' in user
        assert 'tenant_id' in user
        assert 'is_admin' in user
        assert 'is_operator' in user
    
    def test_register_missing_data(self, client):
        """Test register with missing data"""
        response = client.post('/api/auth/register', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'No data provided'
    
    def test_register_missing_email(self, client, valid_invitation):
        """Test register without email"""
        register_data = {
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'email' in data['required']
    
    def test_register_missing_first_name(self, client, valid_invitation):
        """Test register without first_name"""
        register_data = {
            'email': 'newuser@example.com',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'required' in data
        assert 'first_name' in data['required']
    
    def test_register_missing_last_name(self, client, valid_invitation):
        """Test register without last_name"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'required' in data
        assert 'last_name' in data['required']
    
    def test_register_missing_password(self, client, valid_invitation):
        """Test register without password"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'required' in data
        assert 'password' in data['required']
    
    def test_register_missing_invitation_code(self, client):
        """Test register without invitation_code"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing required fields' in data['error']
        assert 'required' in data
        assert 'invitation_code' in data['required']
    
    def test_register_invalid_email_format(self, client, valid_invitation):
        """Test register with invalid email format"""
        register_data = {
            'email': 'invalid-email',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid email format' in data['error']
    
    def test_register_short_password(self, client, valid_invitation):
        """Test register with password shorter than 6 characters"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': '12345',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Password must be at least 6 characters long' in data['error']
    
    def test_register_empty_first_name(self, client, valid_invitation):
        """Test register with empty first_name"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': '   ',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'First name and last name cannot be empty' in data['error']
    
    def test_register_empty_last_name(self, client, valid_invitation):
        """Test register with empty last_name"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': '   ',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'First name and last name cannot be empty' in data['error']
    
    def test_register_invalid_invitation_code(self, client):
        """Test register with invalid invitation code"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': 'invalid-code-12345'
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'Invalid invitation code' in data['message']
    
    def test_register_expired_invitation(self, client, expired_invitation):
        """Test register with expired invitation"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': expired_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'expired' in data['message']
    
    def test_register_used_invitation(self, client, used_invitation):
        """Test register with used invitation"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': used_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'already been used' in data['message']
    
    def test_register_duplicate_email(self, client, valid_invitation, existing_user):
        """Test register with duplicate email"""
        register_data = {
            'email': existing_user.email,
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'User with this email already exists' in data['error']
    
    @patch('app.api.auth.register.GroupsService')
    def test_register_password_is_hashed(self, mock_groups_service, client, test_tenant, valid_invitation):
        """Test that password is properly hashed"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 201
        
        # Verify password is hashed in database
        from app.repository.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_email('newuser@example.com')
        
        assert user.password_hash != 'password123'
        assert bcrypt.check_password_hash(user.password_hash, 'password123')
    
    @patch('app.api.auth.register.GroupsService')
    def test_register_invitation_marked_as_used(self, mock_groups_service, client, db_session, test_tenant, valid_invitation):
        """Test that invitation is marked as used after registration"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }
        
        response = client.post('/api/auth/register', json=register_data)
        
        assert response.status_code == 201
        
        # Verify invitation is marked as used
        db_session.refresh(valid_invitation)
        assert valid_invitation.is_used is True
        assert valid_invitation.used_by_user_id is not None
