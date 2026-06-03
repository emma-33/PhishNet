"""
Tests for Team API endpoints
"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant


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
    """Create another test tenant for isolation testing"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create a test user"""
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
    db_session.refresh(user)
    return user


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
def inactive_user(db_session, test_tenant):
    """Create an inactive user"""
    password_hash = bcrypt.generate_password_hash("inactivepassword123").decode('utf-8')
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
    db_session.refresh(user)
    return user


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
def auth_headers(test_user):
    """Create authorization headers with JWT token"""
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def operator_auth_headers(operator_user):
    """Create authorization headers for operator user"""
    token = create_access_token(identity=str(operator_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_auth_headers(admin_user):
    """Create authorization headers for admin user"""
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_auth_headers(another_user):
    """Create authorization headers for another tenant's user"""
    token = create_access_token(identity=str(another_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestGetTeamMembers:
    """Tests for GET /api/team"""
    
    def test_get_team_members_success(self, client, auth_headers, test_user, 
                                       operator_user, admin_user, inactive_user):
        """Test successfully getting team members"""
        response = client.get('/api/team', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        assert isinstance(data['team_members'], list)
        assert len(data['team_members']) == 4  # test_user, operator_user, admin_user, inactive_user
        
        # Check that all users are included
        member_ids = {member['id'] for member in data['team_members']}
        assert test_user.id in member_ids
        assert operator_user.id in member_ids
        assert admin_user.id in member_ids
        assert inactive_user.id in member_ids
    
    def test_get_team_members_includes_operator_status(self, client, operator_auth_headers,
                                                        test_user, operator_user, admin_user):
        """Test that operator status is correctly identified"""
        response = client.get('/api/team', headers=operator_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Find operator user in response
        operator_member = next(m for m in data['team_members'] if m['id'] == operator_user.id)
        assert operator_member['is_operator'] is True
        assert operator_member['role'] == 'Operator'
        
        # Find non-operator users
        test_member = next(m for m in data['team_members'] if m['id'] == test_user.id)
        assert test_member['is_operator'] is False
        assert test_member['role'] == 'User'
        
        admin_member = next(m for m in data['team_members'] if m['id'] == admin_user.id)
        assert admin_member['is_operator'] is False
        assert admin_member['role'] == 'User'
    
    def test_get_team_members_includes_inactive_users(self, client, auth_headers,
                                                       test_user, inactive_user):
        """Test that inactive users are included in team members"""
        response = client.get('/api/team', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Find inactive user
        inactive_member = next(m for m in data['team_members'] if m['id'] == inactive_user.id)
        assert inactive_member['is_active'] is False
        assert inactive_member['id'] == inactive_user.id
    
    def test_get_team_members_user_fields(self, client, auth_headers, test_user):
        """Test that all required user fields are present"""
        response = client.get('/api/team', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Find test user
        test_member = next(m for m in data['team_members'] if m['id'] == test_user.id)
        
        # Check all required fields
        assert 'id' in test_member
        assert 'email' in test_member
        assert 'first_name' in test_member
        assert 'last_name' in test_member
        assert 'tenant_id' in test_member
        assert 'is_active' in test_member
        assert 'is_admin' in test_member
        assert 'is_operator' in test_member
        assert 'role' in test_member
        assert 'created_at' in test_member
        
        # Check values
        assert test_member['email'] == test_user.email
        assert test_member['first_name'] == test_user.first_name
        assert test_member['last_name'] == test_user.last_name
        assert test_member['tenant_id'] == test_user.tenant_id
        assert test_member['is_active'] == test_user.is_active
        assert test_member['is_admin'] == test_user.is_admin
    
    def test_get_team_members_no_password_hash(self, client, auth_headers, test_user):
        """Test that password hash is not included in response"""
        response = client.get('/api/team', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check that password_hash is not in any member
        for member in data['team_members']:
            assert 'password_hash' not in member
            assert 'password' not in member
    
    def test_get_team_members_tenant_isolation(self, client, auth_headers, another_auth_headers,
                                                 test_user, operator_user, admin_user, inactive_user,
                                                 another_user):
        """Test that users only see team members from their own tenant"""
        # Get team members as test_user (from test_tenant)
        response = client.get('/api/team', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        member_ids = {member['id'] for member in data['team_members']}
        
        # Should include all users from test_tenant
        assert test_user.id in member_ids
        assert operator_user.id in member_ids
        assert admin_user.id in member_ids
        assert inactive_user.id in member_ids
        
        # Should NOT include user from another_tenant
        assert another_user.id not in member_ids
        
        # Get team members as another_user (from another_tenant)
        response2 = client.get('/api/team', headers=another_auth_headers)
        
        assert response2.status_code == 200
        data2 = response2.get_json()
        member_ids2 = {member['id'] for member in data2['team_members']}
        
        # Should only include user from another_tenant
        assert another_user.id in member_ids2
        assert len(member_ids2) == 1
    
    def test_get_team_members_empty_tenant(self, client, db_session):
        """Test getting team members when tenant has no other users"""
        # Create a tenant with only one user
        tenant = Tenant(name="Empty Tenant")
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)
        
        password_hash = bcrypt.generate_password_hash("lonelypassword123").decode('utf-8')
        user = User(
            email="lonely@example.com",
            first_name="Lonely",
            last_name="User",
            password_hash=password_hash,
            tenant_id=tenant.id,
            is_active=True,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/team', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        assert len(data['team_members']) == 1
        assert data['team_members'][0]['id'] == user.id
    
    def test_get_team_members_requires_auth(self, client):
        """Test that getting team members requires authentication"""
        response = client.get('/api/team')
        
        assert response.status_code == 401
    
    def test_get_team_members_admin_can_access(self, client, admin_auth_headers,
                                                 test_user, operator_user, admin_user):
        """Test that admin users can access team members"""
        response = client.get('/api/team', headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        assert len(data['team_members']) >= 3  # At least admin, test_user, operator_user
    
    def test_get_team_members_operator_can_access(self, client, operator_auth_headers,
                                                    test_user, operator_user, admin_user):
        """Test that operator users can access team members"""
        response = client.get('/api/team', headers=operator_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        assert len(data['team_members']) >= 3
    
    def test_get_team_members_operator_without_tenant_operator_id(self, client, db_session, test_tenant):
        """Test team members when tenant has no operator_id set"""
        # Ensure tenant has no operator
        test_tenant.operator_id = None
        db_session.commit()
        
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
        db_session.refresh(user)
        
        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/team', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        
        # All members should have is_operator=False (or None) when tenant has no operator
        for member in data['team_members']:
            # When tenant_operator_id is None, is_operator evaluates to None (falsy)
            assert member['is_operator'] in (False, None)
            assert member['role'] == 'User'
