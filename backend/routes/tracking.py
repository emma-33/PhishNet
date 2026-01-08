"""
Email tracking routes for tracking opens and clicks
"""
from flask import Blueprint, request, send_file, jsonify, current_app
from models.tracking import PageVisit
from utils.database import get_db
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)

tracking_bp = Blueprint('tracking', __name__, url_prefix='/track')

# 1x1 transparent GIF pixel for email open tracking
TRACKING_PIXEL = bytes([
    0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00,
    0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x21,
    0xF9, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x02, 0x44,
    0x01, 0x00, 0x3B
])


@tracking_bp.route('/pixel/<campaign_id>', methods=['GET'])
def track_email_open(campaign_id):
    """
    Track email opens via tracking pixel.
    Returns a 1x1 transparent GIF.
    
    Query params:
        email: recipient email address
    """
    try:
        email = request.args.get('email', 'unknown')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Log email open as page visit
        PageVisit.create(
            db=db,
            campaign_id=campaign_id,
            user_identifier=email,
            ip_address=ip_address,
            user_agent=user_agent,
            page_url=f'/track/pixel/{campaign_id}'
        )
        
        logger.info(f"Email open tracked: campaign={campaign_id}, email={email}")
        
    except Exception as e:
        logger.error(f"Error tracking email open: {str(e)}")
    
    # Always return tracking pixel (even on error)
    return send_file(
        io.BytesIO(TRACKING_PIXEL),
        mimetype='image/gif',
        as_attachment=False,
        download_name='pixel.gif'
    )


@tracking_bp.route('/click/<campaign_id>', methods=['GET'])
def track_link_click(campaign_id):
    """
    Track link clicks in emails.
    Redirects to the target URL after logging.
    
    Query params:
        url: target URL to redirect to
        email: recipient email address
    """
    try:
        target_url = request.args.get('url', '/')
        email = request.args.get('email', 'unknown')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Log link click as page visit
        PageVisit.create(
            db=db,
            campaign_id=campaign_id,
            user_identifier=email,
            ip_address=ip_address,
            user_agent=user_agent,
            page_url=f'/track/click/{campaign_id}?url={target_url}'
        )
        
        logger.info(f"Link click tracked: campaign={campaign_id}, email={email}, url={target_url}")
        
        # Redirect to target URL
        from flask import redirect
        return redirect(target_url, code=302)
        
    except Exception as e:
        logger.error(f"Error tracking link click: {str(e)}")
        return jsonify({'error': 'Tracking failed'}), 500


@tracking_bp.route('/stats/<campaign_id>', methods=['GET'])
def get_tracking_stats(campaign_id):
    """
    Get tracking statistics for a campaign.
    Returns counts of email opens, link clicks, and form submissions.
    """
    try:
        db = get_db(current_app.config['DATABASE_PATH'])
        
        # Get all page visits for this campaign
        visits = PageVisit.get_by_campaign(db, campaign_id)
        
        # Count by type (check page_url patterns)
        email_opens = 0
        link_clicks = 0
        landing_page_visits = 0
        
        for visit in visits:
            # Convert Row to dict if needed
            visit_dict = dict(visit) if not isinstance(visit, dict) else visit
            page_url = visit_dict.get('page_url', '')
            
            if '/track/pixel/' in page_url:
                email_opens += 1
            elif '/track/click/' in page_url:
                link_clicks += 1
            elif '/landing/' in page_url:
                landing_page_visits += 1
        
        # Get form submissions
        from models.tracking import FormSubmission
        submissions = FormSubmission.get_by_campaign(db, campaign_id)
        
        return jsonify({
            'campaign_id': campaign_id,
            'email_opens': email_opens,
            'link_clicks': link_clicks,
            'landing_page_visits': landing_page_visits,
            'form_submissions': len(submissions),
            'total_interactions': len(visits) + len(submissions)
        })
        
    except Exception as e:
        logger.error(f"Error getting tracking stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
