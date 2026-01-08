"""
Dashboard API Routes - Central control for PhishNet operations
"""
from flask import Blueprint, jsonify, request, current_app
from utils.gophish_client import GoPhishClient
from utils.email_client import EmailClient
from utils.database import get_db
from models.tracking import PageVisit, FormSubmission
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    """
    Get overall dashboard statistics and system status.
    
    Returns:
        - Total campaigns
        - Active campaigns
        - Total visits
        - Total submissions
        - GoPhish status
        - Email system status
    """
    try:
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Database statistics
        total_visits = len(db.fetchall('SELECT id FROM page_visits'))
        total_submissions = len(db.fetchall('SELECT id FROM form_submissions'))
        
        # GoPhish statistics (if enabled)
        gophish_status = 'disabled'
        total_campaigns = 0
        active_campaigns = 0
        
        if current_app.config.get('GOPHISH_ENABLED'):
            try:
                client = GoPhishClient(
                    current_app.config['GOPHISH_API_URL'],
                    current_app.config['GOPHISH_API_KEY']
                )
                if client.health_check():
                    gophish_status = 'connected'
                    campaigns = client.get_campaigns()
                    total_campaigns = len(campaigns)
                    active_campaigns = sum(1 for c in campaigns 
                                         if c.get('status') == 'In progress')
                else:
                    gophish_status = 'unreachable'
            except Exception as e:
                logger.error(f"GoPhish health check failed: {str(e)}")
                gophish_status = 'error'
        
        # Email system status
        email_status = 'configured'
        try:
            email_client = EmailClient(current_app.config)
            if email_client.test_connection():
                email_status = 'connected'
            else:
                email_status = 'unreachable'
        except Exception as e:
            logger.error(f"Email system check failed: {str(e)}")
            email_status = 'error'
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'statistics': {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'total_visits': total_visits,
                'total_submissions': total_submissions
            },
            'system_status': {
                'gophish': gophish_status,
                'email': email_status,
                'database': 'operational'
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/campaigns', methods=['GET'])
def list_campaigns():
    """
    List all campaigns from GoPhish with enhanced statistics.
    
    Returns:
        List of campaigns with visit/submission counts
    """
    try:
        if not current_app.config.get('GOPHISH_ENABLED'):
            return jsonify({'error': 'GoPhish integration disabled'}), 503
        
        client = GoPhishClient(
            current_app.config['GOPHISH_API_URL'],
            current_app.config['GOPHISH_API_KEY']
        )
        
        campaigns = client.get_campaigns()
        
        # Enhance with tracking data
        db = get_db(current_app.config['DATABASE_PATH'])
        
        enhanced_campaigns = []
        for campaign in campaigns:
            campaign_id = str(campaign.get('id', ''))
            
            # Get tracking statistics
            visits = PageVisit.get_by_campaign(db, campaign_id)
            submissions = FormSubmission.get_by_campaign(db, campaign_id)
            
            enhanced_campaigns.append({
                'id': campaign.get('id'),
                'name': campaign.get('name'),
                'status': campaign.get('status'),
                'created_date': campaign.get('created_date'),
                'launch_date': campaign.get('launch_date'),
                'completed_date': campaign.get('completed_date'),
                'statistics': {
                    'total_visits': len(visits),
                    'total_submissions': len(submissions),
                    'targets': len(campaign.get('results', []))
                }
            })
        
        return jsonify({
            'campaigns': enhanced_campaigns,
            'count': len(enhanced_campaigns)
        })
        
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/campaigns/<campaign_id>/metrics', methods=['GET'])
def get_campaign_metrics(campaign_id):
    """
    Calculate detailed metrics for a specific campaign.
    
    Metrics:
        - Open rate (email opens / emails sent)
        - Click rate (link clicks / email opens)
        - Submission rate (form submissions / link clicks)
        - Overall success rate (submissions / emails sent)
    """
    try:
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Get all tracking data
        visits = PageVisit.get_by_campaign(db, campaign_id)
        submissions = FormSubmission.get_by_campaign(db, campaign_id)
        
        # Categorize visits
        email_opens = sum(1 for v in visits 
                         if '/track/pixel/' in dict(v).get('page_url', ''))
        link_clicks = sum(1 for v in visits 
                         if '/track/click/' in dict(v).get('page_url', ''))
        landing_visits = sum(1 for v in visits 
                            if '/landing/' in dict(v).get('page_url', ''))
        
        # Get campaign details from GoPhish (if available)
        emails_sent = 0
        campaign_name = f"Campaign {campaign_id}"
        
        if current_app.config.get('GOPHISH_ENABLED'):
            try:
                client = GoPhishClient(
                    current_app.config['GOPHISH_API_URL'],
                    current_app.config['GOPHISH_API_KEY']
                )
                campaign = client.get_campaign(campaign_id)
                if campaign:
                    campaign_name = campaign.get('name', campaign_name)
                    emails_sent = len(campaign.get('results', []))
            except Exception as e:
                logger.warning(f"Could not fetch campaign from GoPhish: {str(e)}")
        
        # Calculate rates
        open_rate = (email_opens / emails_sent * 100) if emails_sent > 0 else 0
        click_rate = (link_clicks / email_opens * 100) if email_opens > 0 else 0
        submission_rate = (len(submissions) / link_clicks * 100) if link_clicks > 0 else 0
        success_rate = (len(submissions) / emails_sent * 100) if emails_sent > 0 else 0
        
        return jsonify({
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'metrics': {
                'emails_sent': emails_sent,
                'email_opens': email_opens,
                'link_clicks': link_clicks,
                'landing_visits': landing_visits,
                'form_submissions': len(submissions),
                'open_rate': round(open_rate, 2),
                'click_rate': round(click_rate, 2),
                'submission_rate': round(submission_rate, 2),
                'success_rate': round(success_rate, 2)
            },
            'recommendations': generate_recommendations({
                'open_rate': open_rate,
                'click_rate': click_rate,
                'submission_rate': submission_rate
            })
        })
        
    except Exception as e:
        logger.error(f"Error calculating campaign metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


def generate_recommendations(metrics):
    """Generate security recommendations based on campaign metrics"""
    recommendations = []
    
    open_rate = metrics['open_rate']
    click_rate = metrics['click_rate']
    submission_rate = metrics['submission_rate']
    
    # Open rate analysis
    if open_rate > 50:
        recommendations.append({
            'severity': 'high',
            'category': 'email_security',
            'message': f'High open rate ({open_rate:.1f}%) indicates poor email filtering. Recommend implementing stricter email security policies.'
        })
    elif open_rate > 30:
        recommendations.append({
            'severity': 'medium',
            'category': 'email_security',
            'message': f'Moderate open rate ({open_rate:.1f}%). Consider enhancing spam filters and email security awareness.'
        })
    
    # Click rate analysis
    if click_rate > 40:
        recommendations.append({
            'severity': 'high',
            'category': 'user_awareness',
            'message': f'High click rate ({click_rate:.1f}%) shows users readily click suspicious links. Immediate security awareness training recommended.'
        })
    elif click_rate > 20:
        recommendations.append({
            'severity': 'medium',
            'category': 'user_awareness',
            'message': f'Moderate click rate ({click_rate:.1f}%). Schedule regular phishing awareness sessions.'
        })
    
    # Submission rate analysis
    if submission_rate > 30:
        recommendations.append({
            'severity': 'critical',
            'category': 'credential_security',
            'message': f'Critical: {submission_rate:.1f}% of users submitted credentials. Implement mandatory security training and password policy review.'
        })
    elif submission_rate > 15:
        recommendations.append({
            'severity': 'high',
            'category': 'credential_security',
            'message': f'High submission rate ({submission_rate:.1f}%). Users need training on recognizing fake login pages.'
        })
    
    # Positive feedback
    if open_rate < 20 and click_rate < 15 and submission_rate < 10:
        recommendations.append({
            'severity': 'info',
            'category': 'positive',
            'message': 'Good security posture! Users are demonstrating awareness of phishing attempts.'
        })
    
    return recommendations


@dashboard_bp.route('/campaigns/compare', methods=['POST'])
def compare_campaigns():
    """
    Compare effectiveness of multiple campaigns.
    
    Request body:
        campaign_ids: List of campaign IDs to compare
    """
    try:
        data = request.get_json()
        campaign_ids = data.get('campaign_ids', [])
        
        if not campaign_ids:
            return jsonify({'error': 'campaign_ids required'}), 400
        
        db = get_db(current_app.config['DATABASE_PATH'])
        comparison = []
        
        for campaign_id in campaign_ids:
            visits = PageVisit.get_by_campaign(db, str(campaign_id))
            submissions = FormSubmission.get_by_campaign(db, str(campaign_id))
            
            email_opens = sum(1 for v in visits 
                             if '/track/pixel/' in dict(v).get('page_url', ''))
            link_clicks = sum(1 for v in visits 
                             if '/track/click/' in dict(v).get('page_url', ''))
            
            comparison.append({
                'campaign_id': campaign_id,
                'email_opens': email_opens,
                'link_clicks': link_clicks,
                'submissions': len(submissions),
                'total_interactions': len(visits) + len(submissions)
            })
        
        # Find most/least effective
        if comparison:
            most_effective = max(comparison, key=lambda x: x['submissions'])
            least_effective = min(comparison, key=lambda x: x['submissions'])
        else:
            most_effective = None
            least_effective = None
        
        return jsonify({
            'comparison': comparison,
            'analysis': {
                'most_effective': most_effective,
                'least_effective': least_effective,
                'total_campaigns': len(comparison)
            }
        })
        
    except Exception as e:
        logger.error(f"Error comparing campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/email/send', methods=['POST'])
def send_test_email():
    """
    Send a test phishing email.
    
    Request body:
        to: Recipient email
        subject: Email subject
        body_text: Plain text body
        body_html: HTML body (optional)
        campaign_id: Campaign identifier
        tracking_url: Base URL for tracking
    """
    try:
        data = request.get_json()
        
        required_fields = ['to', 'subject', 'body_text', 'campaign_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        email_client = EmailClient(current_app.config)
        
        success = email_client.send_phishing_email(
            to=data['to'],
            template_data={
                'subject': data['subject'],
                'body_text': data['body_text'],
                'body_html': data.get('body_html', '')
            },
            campaign_id=data['campaign_id'],
            tracking_url=data.get('tracking_url', request.host_url.rstrip('/'))
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'recipient': data['to'],
                'campaign_id': data['campaign_id']
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/templates', methods=['GET'])
def list_templates():
    """List all email templates from GoPhish"""
    try:
        if not current_app.config.get('GOPHISH_ENABLED'):
            return jsonify({'error': 'GoPhish integration disabled'}), 503
        
        client = GoPhishClient(
            current_app.config['GOPHISH_API_URL'],
            current_app.config['GOPHISH_API_KEY']
        )
        
        templates = client.get_templates()
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        })
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/groups', methods=['GET'])
def list_groups():
    """List all target groups from GoPhish"""
    try:
        if not current_app.config.get('GOPHISH_ENABLED'):
            return jsonify({'error': 'GoPhish integration disabled'}), 503
        
        client = GoPhishClient(
            current_app.config['GOPHISH_API_URL'],
            current_app.config['GOPHISH_API_KEY']
        )
        
        groups = client.get_groups()
        
        return jsonify({
            'groups': groups,
            'count': len(groups)
        })
        
    except Exception as e:
        logger.error(f"Error listing groups: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/landing-pages', methods=['GET'])
def list_landing_pages():
    """List all landing pages from GoPhish"""
    try:
        if not current_app.config.get('GOPHISH_ENABLED'):
            return jsonify({'error': 'GoPhish integration disabled'}), 503
        
        client = GoPhishClient(
            current_app.config['GOPHISH_API_URL'],
            current_app.config['GOPHISH_API_KEY']
        )
        
        pages = client.get_landing_pages()
        
        return jsonify({
            'landing_pages': pages,
            'count': len(pages)
        })
        
    except Exception as e:
        logger.error(f"Error listing landing pages: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/analytics/timeline', methods=['GET'])
def get_analytics_timeline():
    """
    Get timeline analytics for all campaigns.
    
    Query params:
        campaign_id: Filter by campaign (optional)
        days: Number of days to include (default: 30)
    """
    try:
        campaign_id = request.args.get('campaign_id')
        days = int(request.args.get('days', 30))
        
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Get visits and submissions
        if campaign_id:
            visits = PageVisit.get_by_campaign(db, campaign_id)
            submissions = FormSubmission.get_by_campaign(db, campaign_id)
        else:
            visits = db.fetchall('SELECT * FROM page_visits ORDER BY visit_timestamp DESC')
            submissions = db.fetchall('SELECT * FROM form_submissions ORDER BY submission_timestamp DESC')
        
        # Group by date
        timeline = {}
        
        for visit in visits:
            visit_dict = dict(visit)
            timestamp = visit_dict.get('visit_timestamp', '')
            if timestamp:
                date = timestamp.split('T')[0]
                if date not in timeline:
                    timeline[date] = {'visits': 0, 'submissions': 0}
                timeline[date]['visits'] += 1
        
        for submission in submissions:
            sub_dict = dict(submission)
            timestamp = sub_dict.get('submission_timestamp', '')
            if timestamp:
                date = timestamp.split('T')[0]
                if date not in timeline:
                    timeline[date] = {'visits': 0, 'submissions': 0}
                timeline[date]['submissions'] += 1
        
        # Convert to list and sort
        timeline_list = [
            {'date': date, 'visits': data['visits'], 'submissions': data['submissions']}
            for date, data in sorted(timeline.items())
        ]
        
        return jsonify({
            'timeline': timeline_list,
            'total_days': len(timeline_list),
            'campaign_id': campaign_id
        })
        
    except Exception as e:
        logger.error(f"Error fetching analytics timeline: {str(e)}")
        return jsonify({'error': str(e)}), 500
