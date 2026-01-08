"""Instance API routes"""
from flask import Blueprint, request, jsonify, current_app
from app.models.instance import Instance
from app.models.campaign import CampaignStatus
from app.repository.instance_repository import InstanceRepository
from app.repository.campaign_repository import CampaignRepository
from app.repository.template_repository import TemplateMapRepository
from app.api.helpers import admin_required

bp = Blueprint('instances', __name__, url_prefix='/api/instances')


def mask_api_key(api_key: str) -> str:
    """Mask API key"""
    if not api_key or len(api_key) <= 4:
        return "****"
    return "*" * (len(api_key) - 4) + api_key[-4:]


def instance_to_dict(instance: Instance, mask_key: bool = True) -> dict:
    """Convert instance to dictionary"""
    return {
        'id': instance.id,
        'name': instance.name,
        'base_url': instance.base_url,
        'api_key': mask_api_key(instance.api_key) if mask_key else instance.api_key,
        'is_active': instance.is_active,
        'created_at': instance.created_at.isoformat() if instance.created_at else None,
    }


@bp.route('', methods=['GET'])
@admin_required
def get_all_instances():
    try:
        instance_repo = InstanceRepository()
        instances = instance_repo.get_all()
        
        return jsonify({
            'instances': [instance_to_dict(instance) for instance in instances]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting all instances')
        return jsonify({'error': 'Failed to get instances', 'message': str(e)}), 500


@bp.route('/<int:instance_id>', methods=['GET'])
@admin_required
def get_instance(instance_id):
    try:
        instance_repo = InstanceRepository()
        instance = instance_repo.get_by_id(instance_id)
        
        if not instance:
            return jsonify({'error': 'Instance not found'}), 404
        
        return jsonify(instance_to_dict(instance)), 200
    except Exception as e:
        current_app.logger.exception('Error getting instance')
        return jsonify({'error': 'Failed to get instance', 'message': str(e)}), 500


@bp.route('', methods=['POST'])
@admin_required
def create_instance():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'base_url', 'api_key']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields,
                'missing': missing_fields
            }), 400
        
        base_url = data.get('base_url', '').strip()
        if not base_url.startswith(('http://', 'https://')):
            return jsonify({
                'error': 'Invalid base_url',
                'message': 'base_url must start with http:// or https://'
            }), 400
        
        instance_repo = InstanceRepository()
        existing_instances = instance_repo.get_all(name=data.get('name'))
        if existing_instances:
            return jsonify({
                'error': 'Instance with this name already exists',
                'message': 'Instance names must be unique'
            }), 400
        
        instance = Instance(
            name=data.get('name'),
            base_url=base_url.rstrip('/'),
            api_key=data.get('api_key'),
            is_active=data.get('is_active', True)
        )
        
        created_instance = instance_repo.create(instance)
        
        return jsonify({
            'status': 'success',
            'message': 'Instance created successfully',
            'instance': instance_to_dict(created_instance)
        }), 201
            
    except ValueError as e:
        current_app.logger.error(f'Validation error creating instance: {e}')
        return jsonify({'error': 'Invalid instance data', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error creating instance')
        return jsonify({'error': 'Failed to create instance', 'message': str(e)}), 500


@bp.route('/<int:instance_id>', methods=['PUT'])
@admin_required
def update_instance(instance_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        instance_repo = InstanceRepository()
        instance = instance_repo.get_by_id(instance_id)
        
        if not instance:
            return jsonify({'error': 'Instance not found'}), 404
        
        update_data = {}
        
        if 'name' in data:
            if data['name'] != instance.name:
                existing_instances = instance_repo.get_all(name=data['name'])
                if existing_instances:
                    return jsonify({
                        'error': 'Instance with this name already exists',
                        'message': 'Instance names must be unique'
                    }), 400
            update_data['name'] = data['name']
        
        if 'base_url' in data:
            base_url = data['base_url'].strip()
            if not base_url.startswith(('http://', 'https://')):
                return jsonify({
                    'error': 'Invalid base_url',
                    'message': 'base_url must start with http:// or https://'
                }), 400
            update_data['base_url'] = base_url.rstrip('/')
        
        if 'api_key' in data:
            update_data['api_key'] = data['api_key']
        
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        updated_instance = instance_repo.update_by_id(instance_id, **update_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Instance updated successfully',
            'instance': instance_to_dict(updated_instance)
        }), 200
            
    except ValueError as e:
        current_app.logger.error(f'Validation error updating instance: {e}')
        return jsonify({'error': 'Invalid instance data', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error updating instance')
        return jsonify({'error': 'Failed to update instance', 'message': str(e)}), 500


@bp.route('/<int:instance_id>', methods=['DELETE'])
@admin_required
def delete_instance(instance_id):
    try:
        instance_repo = InstanceRepository()
        instance = instance_repo.get_by_id(instance_id)
        
        if not instance:
            return jsonify({'error': 'Instance not found'}), 404
        
        campaign_repo = CampaignRepository()
        campaigns = campaign_repo.get_by_instance_id(instance_id)
        
        running_campaigns = [c for c in campaigns if c.status == CampaignStatus.RUNNING]
        if running_campaigns:
            campaign_names = [c.name for c in running_campaigns]
            return jsonify({
                'error': 'Cannot delete instance with running campaigns',
                'message': f'There are {len(running_campaigns)} running campaign(s) using this instance',
                'running_campaigns': campaign_names,
                'details': 'Please stop all running campaigns before deleting this instance'
            }), 400
        
        if campaigns:
            campaign_names = [c.name for c in campaigns]
            return jsonify({
                'error': 'Cannot delete instance with associated campaigns',
                'message': f'There are {len(campaigns)} campaign(s) using this instance',
                'campaigns': campaign_names,
                'details': 'Please delete or reassign all campaigns before deleting this instance'
            }), 400
        
        template_repo = TemplateMapRepository()
        templates = template_repo.get_by_instance_id(instance_id)
        
        if templates:
            template_names = [t.name for t in templates]
            return jsonify({
                'error': 'Cannot delete instance with associated templates',
                'message': f'There are {len(templates)} template(s) using this instance',
                'templates': template_names,
                'details': 'Please delete all templates before deleting this instance'
            }), 400
        
        instance_repo.delete(instance_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Instance deleted successfully'
        }), 200
            
    except ValueError as e:
        return jsonify({'error': 'Invalid instance ID', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error deleting instance')
        return jsonify({'error': 'Failed to delete instance', 'message': str(e)}), 500


@bp.route('/<int:instance_id>/toggle', methods=['PATCH'])
@admin_required
def toggle_instance_status(instance_id):
    try:
        instance_repo = InstanceRepository()
        instance = instance_repo.get_by_id(instance_id)
        
        if not instance:
            return jsonify({'error': 'Instance not found'}), 404
        
        new_status = not instance.is_active
        if new_status:
            updated_instance = instance_repo.activate(instance_id)
        else:
            updated_instance = instance_repo.deactivate(instance_id)
        
        return jsonify({
            'status': 'success',
            'message': f'Instance {"activated" if new_status else "deactivated"} successfully',
            'instance': instance_to_dict(updated_instance)
        }), 200
            
    except ValueError as e:
        return jsonify({'error': 'Invalid instance ID', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error toggling instance status')
        return jsonify({'error': 'Failed to toggle instance status', 'message': str(e)}), 500
