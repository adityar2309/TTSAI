"""
Authentication configuration module for Google OAuth
"""
import os
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_CALLBACK_URL = os.getenv('GOOGLE_CALLBACK_URL')

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 60 * 60 * 24  # 24 hours in seconds

# Session Configuration
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'ttsai_'

# Auth Routes
AUTH_ROUTES = {
    'google_auth': '/api/auth/google',
    'google_callback': '/api/auth/google/callback',
    'logout': '/api/auth/logout',
    'user_info': '/api/auth/user',
    'session_check': '/api/auth/session'
}

# Scopes required for Google OAuth
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def get_auth_config():
    """
    Returns the authentication configuration
    """
    return {
        'google_client_id': GOOGLE_CLIENT_ID,
        'google_client_secret': GOOGLE_CLIENT_SECRET,
        'google_callback_url': GOOGLE_CALLBACK_URL,
        'jwt_secret': JWT_SECRET,
        'jwt_algorithm': JWT_ALGORITHM,
        'jwt_expiration': JWT_EXPIRATION,
        'auth_routes': AUTH_ROUTES,
        'google_scopes': GOOGLE_SCOPES
    }