"""
PhishNet Backend - Main Application Entry Point
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import os

from config import config


def create_app(config_name='development'):
    """
    Application factory pattern for Flask app
    
    Args:
        config_name: Configuration to use (development, testing, default)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS for frontend communication
    # Allow both localhost and 127.0.0.1 on port 5173
    CORS(app, 
         origins=["http://localhost:5173", "http://127.0.0.1:5173"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Register blueprints
    register_blueprints(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_blueprints(app):
    """Register all application blueprints"""
    from routes.gophish import gophish_bp
    from routes.landing import landing_bp
    from routes.tracking import tracking_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(gophish_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(dashboard_bp)


def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Root endpoint - Basic info"""
        return jsonify({
            'name': 'PhishNet Backend API',
            'version': '0.1.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': 'phishnet-backend'
        })


# Create app instance for direct running
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
