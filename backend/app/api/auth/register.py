from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from app.extensions import bcrypt
from app.repository.user_repository import UserRepository
from app.repository.tenant_repository import TenantRepository
from app.models.user import User
from app.services.tenant_invitation_service import validate_invitation, use_invitation
from app.services.gophish.groups import GroupsService
from . import bp


@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        invitation_code = data.get('invitation_code')
        
        if not email or not first_name or not last_name or not password or not invitation_code:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['email', 'first_name', 'last_name', 'password', 'invitation_code']
            }), 400
        
        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        first_name = first_name.strip()
        last_name = last_name.strip()
        if not first_name or not last_name:
            return jsonify({'error': 'First name and last name cannot be empty'}), 400
        
        user_repo = UserRepository()
        
        validation_result = validate_invitation(invitation_code)
        if validation_result['status'] == 'error':
            return jsonify({
                'message': validation_result['message']
            }), 400
        
        invitation = validation_result['invitation']
        tenant_id = invitation.tenant_id
        
        existing_user = user_repo.get_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            tenant_id=tenant_id,
            is_active=True,
            is_admin=False
        )
        
        try:
            user = user_repo.create(user)
        except IntegrityError as e:
            current_app.logger.error(f'Integrity error during user creation: {e}')
            return jsonify({'error': 'User creation failed due to constraint violation'}), 409
        
        use_result = use_invitation(invitation_code, user.id)
        if use_result['status'] == 'error':
            current_app.logger.warning(f'Failed to mark invitation as used: {use_result["message"]}')
        
        try:
            tenant_repo = TenantRepository()
            tenant = tenant_repo.get_by_id(tenant_id)
            
            # Set first user as operator if tenant doesn't have one
            if tenant and not tenant.operator_id:
                tenant_repo.update_by_id(tenant_id, operator_id=user.id)
                tenant.operator_id = user.id
            if tenant and tenant.gophish_group_id:
                groups_service = GroupsService()
                groups_service.add_user_to_group(
                    group_id=tenant.gophish_group_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    position=""
                )
                current_app.logger.info(f'Added user {user.email} to Gophish group {tenant.gophish_group_id}')
        except Exception as e:
            current_app.logger.warning(f'Failed to add user to Gophish group: {e}')
        
        access_token = create_access_token(identity=user.id)
        
        # Check if user is operator
        tenant_repo = TenantRepository()
        tenant = tenant_repo.get_by_id(tenant_id)
        is_operator = tenant and tenant.operator_id == user.id
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tenant_id': user.tenant_id,
                'is_admin': user.is_admin,
                'is_operator': is_operator
            },
            'access_token': access_token
        }), 201
        
    except Exception as e:
        current_app.logger.exception('Error during registration')
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500
