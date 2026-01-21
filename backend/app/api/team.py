"""Team API routes"""
from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from app.repository.user_repository import UserRepository
from app.repository.target_repository import TargetRepository
from app.models.target import Target
from app.services.gophish.groups import GroupsService
from app.services.audit_log_service import audit_service
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


def target_to_dict(target):
    """Convert target to dictionary."""
    return {
        'id': target.id,
        'email': target.email,
        'first_name': target.first_name,
        'last_name': target.last_name,
        'position': target.position,
        'tenant_id': target.tenant_id,
        'created_at': target.created_at.isoformat() if target.created_at else None
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


@bp.route('/targets', methods=['GET'])
@jwt_required()
def get_targets():
    """Get all phishing targets for the current tenant."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        target_repo = TargetRepository()
        targets = target_repo.get_all_by_tenant_id(user.tenant_id)

        return jsonify({
            'targets': [target_to_dict(t) for t in targets]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting targets')
        return jsonify({'error': 'Failed to get targets', 'message': str(e)}), 500


@bp.route('/targets', methods=['POST'])
@jwt_required()
def add_target():
    """Add a new phishing target and sync with GoPhish."""
    try:
        data = request.get_json()
        user = get_current_user()

        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        position = data.get('position', '')

        if not email or not first_name or not last_name:
            return jsonify({'error': 'Missing required fields'}), 400

        target_repo = TargetRepository()

        # Check if target already exists for this tenant
        existing = target_repo.get_by_email(email, user.tenant_id)
        if existing:
            return jsonify({'error': 'Target already exists'}), 409

        target = Target(
            email=email,
            first_name=first_name,
            last_name=last_name,
            position=position,
            tenant_id=user.tenant_id
        )

        target = target_repo.create(target)

        # Log action
        audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action='CREATE_TARGET',
            resource_type='Target',
            resource_id=str(target.id),
            details={
                'email': target.email,
                'first_name': target.first_name,
                'last_name': target.last_name
            }
        )

        # Sync with GoPhish
        try:
            from app.repository.tenant_repository import TenantRepository
            from app.repository.instance_repository import InstanceRepository
            from app.services.load_balancer import LoadBalancerService

            tenant_repo = TenantRepository()
            tenant = tenant_repo.get_by_id(user.tenant_id)
            groups_service = GroupsService()

            if tenant:
                if not tenant.gophish_group_id:
                    # Create group automatically if it doesn't exist
                    lb = LoadBalancerService()
                    instance = lb.select_instance_for_load_balancing()
                    if instance:
                        gophish_group = groups_service.create_group(tenant, instance=instance)
                        tenant_repo.update_by_id(tenant.id, gophish_group_id=gophish_group.id, instance_id=instance.id)
                        current_app.logger.info(f"Created GoPhish group '{tenant.name}' (ID: {gophish_group.id}) on instance '{instance.name}'")
                else:
                    # Add to existing group
                    instance_repo = InstanceRepository()
                    instance = instance_repo.get_by_id(tenant.instance_id) if tenant.instance_id else None

                    groups_service.add_target_to_group(
                        group_id=tenant.gophish_group_id,
                        first_name=target.first_name,
                        last_name=target.last_name,
                        email=target.email,
                        position=target.position,
                        instance=instance
                    )
                    current_app.logger.info(f'Synced target {email} with GoPhish group {tenant.gophish_group_id}')
        except Exception as sync_e:
            current_app.logger.warning(f'Failed to sync target with GoPhish: {sync_e}')

        return jsonify(target_to_dict(target)), 201

    except Exception as e:
        current_app.logger.exception('Error adding target')
        return jsonify({'error': 'Failed to add target', 'message': str(e)}), 500


@bp.route('/targets/<int:target_id>', methods=['DELETE'])
@jwt_required()
def delete_target(target_id):
    """Delete a phishing target and sync with GoPhish."""
    try:
        user = get_current_user()
        target_repo = TargetRepository()

        target = target_repo.get_by_id(target_id)
        if not target or target.tenant_id != user.tenant_id:
            return jsonify({'error': 'Target not found'}), 404

        email = target.email
        target_repo.delete_by_id(target_id)

        # Log action
        audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action='DELETE_TARGET',
            resource_type='Target',
            resource_id=str(target_id),
            details={'email': email}
        )

        # Sync with GoPhish if tenant has a group
        try:
            from app.repository.tenant_repository import TenantRepository
            from app.repository.instance_repository import InstanceRepository

            tenant_repo = TenantRepository()
            tenant = tenant_repo.get_by_id(user.tenant_id)

            if tenant and tenant.gophish_group_id:
                instance_repo = InstanceRepository()
                instance = instance_repo.get_by_id(tenant.instance_id) if tenant.instance_id else None

                groups_service = GroupsService()
                groups_service.remove_target_from_group(
                    group_id=tenant.gophish_group_id,
                    email=email,
                    instance=instance
                )
                current_app.logger.info(f'Removed target {email} from GoPhish group {tenant.gophish_group_id}')
        except Exception as sync_e:
            current_app.logger.warning(f'Failed to remove target from GoPhish: {sync_e}')

        return jsonify({'message': 'Target deleted successfully'}), 200

    except Exception as e:
        current_app.logger.exception('Error deleting target')
        return jsonify({'error': 'Failed to delete target', 'message': str(e)}), 500
