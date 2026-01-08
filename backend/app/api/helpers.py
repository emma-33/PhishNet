"""Helper functions and decorators for API routes"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repository.user_repository import UserRepository


def format_date(date_value):
    """Convert date to ISO format string."""
    if not date_value:
        return None
    if isinstance(date_value, str):
        return date_value
    if hasattr(date_value, 'isoformat'):
        return date_value.isoformat()
    return str(date_value)


def get_current_user():
    """Get the current authenticated user from JWT token"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    
    user_repo = UserRepository()
    return user_repo.get_by_id(user_id)


def verify_tenant_ownership(resource_tenant_id: int, user_tenant_id: int):
    """Verify tenant ownership"""
    return resource_tenant_id == user_tenant_id


def is_tenant_operator(user_id: int, tenant_id: int):
    """Check if user is the operator (owner) of the tenant."""
    from app.repository.tenant_repository import TenantRepository
    tenant_repo = TenantRepository()
    tenant = tenant_repo.get_by_id(tenant_id)
    return tenant and tenant.operator_id == user_id


def admin_required(f):
    """Require admin access"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
