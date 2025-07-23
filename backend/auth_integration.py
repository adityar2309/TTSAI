"""
Integration module for adding authentication to the main Flask app
"""
import os
import logging
from flask import Flask

# Import auth modules
from auth_routes import register_auth_routes
from db_service_auth import extend_db_service_with_auth
from auth_config import get_auth_config

# Configure logging
logger = logging.getLogger(__name__)

def integrate_auth(app, db_service):
    """
    Integrate authentication into the Flask app
    
    Args:
        app (Flask): Flask application
        db_service: Database service
        
    Returns:
        Flask: Updated Flask application
    """
    try:
        # Get database path from app config
        db_path = app.config.get('DATABASE_URL', '').replace('sqlite:///', '')
        
        # Extend database service with auth methods
        extended_db = extend_db_service_with_auth(db_service, db_path)
        
        # Add extended db_service to app config
        app.config['db_service'] = extended_db
        
        # Register auth routes
        register_auth_routes(app)
        
        # Configure session
        auth_config = get_auth_config()
        app.secret_key = auth_config['jwt_secret']
        
        logger.info("Authentication integration completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error integrating authentication: {e}")
        raise