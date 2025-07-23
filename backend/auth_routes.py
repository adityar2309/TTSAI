"""
Authentication routes for Google OAuth integration
"""
from flask import Blueprint, request, jsonify, redirect, session, url_for
import logging
import json
import jwt
from functools import wraps

# Import auth service and configuration
from auth_service import auth_service
from auth_config import get_auth_config, AUTH_ROUTES

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Get auth configuration
auth_config = get_auth_config()

def token_required(f):
    """
    Decorator for routes that require authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Verify token
            payload = auth_service.verify_jwt_token(token)
            # Add user info to request
            request.user = payload
            
        except jwt.InvalidTokenError as e:
            return jsonify({'error': 'Invalid authentication token', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """
    Handle Google authentication token verification
    """
    try:
        # Get token from request
        data = request.json
        if not data or 'token' not in data:
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        
        # Verify Google token
        user_info = auth_service.verify_google_token(token)
        
        # Get database service from app context
        db_service = request.app.config.get('db_service')
        if not db_service:
            return jsonify({'error': 'Database service not available'}), 500
        
        # Create or update user
        user = auth_service.create_user_from_google_data(user_info, db_service)
        
        # Generate JWT token
        jwt_token = auth_service.generate_jwt_token(user)
        
        # Return user info and token
        return jsonify({
            'token': jwt_token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'profile_picture': user.get('profile_picture'),
                'created_at': user.get('created_at')
            }
        })
        
    except ValueError as e:
        logger.error(f"Google auth error: {e}")
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
    except Exception as e:
        logger.error(f"Unexpected error in Google auth: {e}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """
    Handle Google OAuth callback
    This is a fallback for the frontend-based OAuth flow
    """
    # In a frontend-based OAuth flow, this endpoint might not be needed
    # as the token is handled directly by the frontend
    return redirect(url_for('frontend_redirect'))

@auth_bp.route('/user', methods=['GET'])
@token_required
def get_user():
    """
    Get current authenticated user information
    """
    try:
        # User info is added to request by token_required decorator
        user_id = request.user['sub']
        
        # Get database service from app context
        db_service = request.app.config.get('db_service')
        if not db_service:
            return jsonify({'error': 'Database service not available'}), 500
        
        # Get user from database
        user = db_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return user info
        return jsonify({
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'profile_picture': user.get('profile_picture'),
                'created_at': user.get('created_at')
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out user by invalidating session
    """
    # Clear session
    session.clear()
    
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/session', methods=['GET'])
@token_required
def check_session():
    """
    Check if user session is valid
    """
    # If we get here, the token is valid (checked by token_required decorator)
    return jsonify({'valid': True})

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh authentication token
    """
    try:
        # Get token from request
        data = request.json
        if not data or 'token' not in data:
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        
        # Refresh token
        new_token = auth_service.refresh_token(token)
        
        # Return new token
        return jsonify({'token': new_token})
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
    except Exception as e:
        logger.error(f"Unexpected error in token refresh: {e}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

def register_auth_routes(app):
    """
    Register authentication routes with Flask app
    """
    app.register_blueprint(auth_bp, url_prefix='/api/auth')