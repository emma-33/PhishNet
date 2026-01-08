"""
GoPhish Integration Routes
"""
from flask import Blueprint, jsonify, current_app
from utils.gophish_client import GoPhishClient

gophish_bp = Blueprint('gophish', __name__, url_prefix='/api/gophish')


def get_gophish_client():
    """Get configured GoPhish client instance"""
    return GoPhishClient(
        base_url=current_app.config['GOPHISH_API_URL'],
        api_key=current_app.config['GOPHISH_API_KEY']
    )


@gophish_bp.route('/status')
def gophish_status():
    """Check GoPhish server connectivity"""
    if not current_app.config['GOPHISH_ENABLED']:
        return jsonify({
            'status': 'disabled',
            'message': 'GoPhish integration is disabled in config'
        }), 200
    
    try:
        client = get_gophish_client()
        is_healthy = client.health_check()
        
        return jsonify({
            'status': 'connected' if is_healthy else 'unreachable',
            'url': current_app.config['GOPHISH_API_URL'],
            'healthy': is_healthy
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@gophish_bp.route('/campaigns')
def list_campaigns():
    """Get all campaigns from GoPhish"""
    if not current_app.config['GOPHISH_ENABLED']:
        return jsonify({
            'error': 'GoPhish integration is disabled'
        }), 503
    
    try:
        client = get_gophish_client()
        campaigns = client.get_campaigns()
        
        return jsonify({
            'campaigns': campaigns,
            'count': len(campaigns)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gophish_bp.route('/campaigns/<int:campaign_id>')
def get_campaign(campaign_id):
    """Get specific campaign details"""
    if not current_app.config['GOPHISH_ENABLED']:
        return jsonify({
            'error': 'GoPhish integration is disabled'
        }), 503
    
    try:
        client = get_gophish_client()
        campaign = client.get_campaign(campaign_id)
        
        return jsonify(campaign)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gophish_bp.route('/groups')
def list_groups():
    """Get all target groups"""
    if not current_app.config['GOPHISH_ENABLED']:
        return jsonify({
            'error': 'GoPhish integration is disabled'
        }), 503
    
    try:
        client = get_gophish_client()
        groups = client.get_groups()
        
        return jsonify({
            'groups': groups,
            'count': len(groups)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gophish_bp.route('/templates')
def list_templates():
    """Get all email templates"""
    if not current_app.config['GOPHISH_ENABLED']:
        return jsonify({
            'error': 'GoPhish integration is disabled'
        }), 503
    
    try:
        client = get_gophish_client()
        templates = client.get_templates()
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
