"""Campaign API routes"""
import datetime
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.campaign import CampaignStatus, Campaign
from app.services.gophish import CampaignService, TemplatesService
from app.services.gophish.groups import GroupsService
from app.services.load_balancer import LoadBalancerService
from app.repository.user_repository import UserRepository
from app.repository.tenant_repository import TenantRepository
from app.repository.instance_repository import InstanceRepository
from app.utils.auth_helper import get_current_user
from app.utils.tenant_helper import verify_tenant_ownership

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


def campaign_to_dict(campaign: Campaign) -> dict:
    """Convert campaign to dictionary"""
    return {
        'id': campaign.id,
        'name': campaign.name,
        'status': campaign.status.value,
        'tenant_id': campaign.tenant_id,
        'created_by_user_id': campaign.created_by_user_id,
        'template_id': campaign.template_id,
        'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
        'launched_at': campaign.launched_at.isoformat() if campaign.launched_at else None,
        'stopped_at': campaign.stopped_at.isoformat() if campaign.stopped_at else None,
    }

@bp.route('', methods=['GET'])
@jwt_required()
def get_all_campaigns():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = CampaignService()
        campaigns = service.get_all_campaigns(tenant_id=user.tenant_id)
        return jsonify({
            'campaigns': [campaign_to_dict(campaign) for campaign in campaigns]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting all campaigns')
        return jsonify({'error': 'Failed to get campaigns', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = CampaignService()
        campaign = service.get_campaign_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        return jsonify(campaign_to_dict(campaign)), 200
    except Exception as e:
        current_app.logger.exception('Error getting campaign')
        return jsonify({'error': 'Failed to get campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>/summary', methods=['GET'])
@jwt_required()
def get_campaign_summary(campaign_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = CampaignService()
        data = service.get_campaign_summary_and_results(campaign_id, tenant_id=user.tenant_id)
        
        return jsonify(data), 200
    except ValueError as e:
        return jsonify({'error': 'Campaign not found', 'message': str(e)}), 404
    except PermissionError as e:
        return jsonify({'error': 'Access denied', 'message': str(e)}), 403
    except Exception as e:
        current_app.logger.exception('Error getting campaign summary')
        return jsonify({'error': 'Failed to get campaign summary', 'message': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_campaign():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        required_fields = ['name', 'template_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields,
                'missing': missing_fields
            }), 400
        
        template_id = data.get('template_id')
        try:
            template_id_int = int(template_id)
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid template_id',
                'message': 'template_id must be a valid integer'
            }), 400
        
        templates_service = TemplatesService()
        template = templates_service.get_template_by_id(template_id_int)
        if not template:
            return jsonify({
                'error': 'Template not found',
                'message': f'Template with ID {template_id_int} does not exist'
            }), 404
        
        # Get tenant and its associated instance
        tenant_repo = TenantRepository()
        tenant = tenant_repo.get_by_id(user.tenant_id)
        
        if not tenant.instance_id:
            return jsonify({
                'error': 'Tenant instance not configured',
                'message': 'Your tenant does not have an associated instance. Please contact an administrator.'
            }), 400
        
        # Get and verify the instance is active
        instance_repo = InstanceRepository()
        gophish_instance = instance_repo.get_by_id(tenant.instance_id)
        
        if not gophish_instance:
            return jsonify({
                'error': 'Instance not found',
                'message': 'The instance associated with your tenant could not be found'
            }), 404
        
        if not gophish_instance.is_active:
            return jsonify({
                'error': 'Instance inactive',
                'message': 'The Gophish instance associated with your tenant is not active'
            }), 400
        
        # Check if tenant has a group associated, create one if not
        if not tenant.gophish_group_id:
            try:
                groups_service = GroupsService()
                gophish_group = groups_service.create_group(tenant, instance=gophish_instance)
                
                # Update tenant with the new group ID
                tenant_repo.update_by_id(tenant.id, gophish_group_id=gophish_group.id)
                tenant.gophish_group_id = gophish_group.id
                
                current_app.logger.info(f"Created Gophish group {gophish_group.id} for tenant {tenant.id} ({tenant.name})")
            except Exception as e:
                current_app.logger.error(f"Failed to create group for tenant {tenant.id}: {e}")
                return jsonify({
                    'error': 'Failed to create tenant group',
                    'message': f'Could not create Gophish group for tenant: {str(e)}'
                }), 500
        
        campaign = Campaign(
            name=data.get('name'),
            tenant_id=user.tenant_id,
            created_by_user_id=user.id,
            gophish_instance_id=gophish_instance.id,
            gophish_campaign_id=0,
            status=CampaignStatus.RUNNING,
            template_id=template_id_int,
            launched_at=datetime.datetime.utcnow()
        )

        service = CampaignService()
        result = service.create_campaign(campaign)
        
        if result.get('status') == 'success':
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except TypeError as e:
        current_app.logger.error(f'Type error creating campaign: {e}')
        return jsonify({'error': 'Invalid campaign data', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error creating campaign')
        return jsonify({'error': 'Failed to create campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = CampaignService()
        result = service.delete_campaign(campaign_id, tenant_id=user.tenant_id)
        
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({'error': 'Invalid campaign ID', 'message': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': 'Access denied', 'message': str(e)}), 403
    except Exception as e:
        current_app.logger.exception('Error deleting campaign')
        return jsonify({'error': 'Failed to delete campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>/complete', methods=['POST'])
@jwt_required()
def complete_campaign(campaign_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = CampaignService()
        result = service.complete_campaign(campaign_id, tenant_id=user.tenant_id)
        
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({'error': 'Invalid campaign ID', 'message': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': 'Access denied', 'message': str(e)}), 403
    except Exception as e:
        current_app.logger.exception('Error completing campaign')
        return jsonify({'error': 'Failed to complete campaign', 'message': str(e)}), 500
