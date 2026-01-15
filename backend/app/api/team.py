"""Team API routes"""
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.repository.user_repository import UserRepository
from app.utils.auth_helper import get_current_user

bp = Blueprint('team', __name__, url_prefix='/api/team')


def user_to_dict(user, tenant_operator_id=None):
    """Convert user to dictionary (excluding sensitive information)."""
    is_operator = tenant_operator_id and user.id == tenant_operator_id
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tenant_id': user.tenant_id,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'is_operator': is_operator,
        'role': 'Operator' if is_operator else 'User',
        'created_at': user.created_at.isoformat() if user.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def get_team_members():
    """Get all team members in the same tenant as the current user."""
    try:
        from app.repository.tenant_repository import TenantRepository
        
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tenant_repo = TenantRepository()
        tenant = tenant_repo.get_by_id(user.tenant_id)
        tenant_operator_id = tenant.operator_id if tenant else None
        
        user_repo = UserRepository()
        team_members = user_repo.get_all_by_tenant_id(user.tenant_id, active_only=False)
        
        return jsonify({
            'team_members': [user_to_dict(member, tenant_operator_id) for member in team_members]
        }), 200
        
    except Exception as e:
        current_app.logger.exception('Error getting team members')
        return jsonify({'error': 'Failed to get team members', 'message': str(e)}), 500
