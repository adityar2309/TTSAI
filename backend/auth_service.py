"""
Authentication service for Google OAuth integration
"""
import os
import json
import time
from datetime import datetime, timedelta
import logging
import requests
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Import auth configuration
from auth_config import get_auth_config

# Configure logging
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for handling Google OAuth and user sessions
    """
    def __init__(self):
        """Initialize the auth service with configuration"""
        self.config = get_auth_config()
        self.client_id = self.config['google_client_id']
        self.client_secret = self.config['google_client_secret']
        self.callback_url = self.config['google_callback_url']
        self.jwt_secret = self.config['jwt_secret']
        self.jwt_algorithm = self.config['jwt_algorithm']
        self.jwt_expiration = self.config['jwt_expiration']
        
        # Validate configuration
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not properly configured")
    
    def verify_google_token(self, token):
        """
        Verify the Google ID token and extract user information
        
        Args:
            token (str): The Google ID token to verify
            
        Returns:
            dict: User information extracted from the token
            
        Raises:
            ValueError: If token verification fails
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Check issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'locale': idinfo.get('locale'),
                'verified_email': idinfo.get('email_verified', False)
            }
            
            return user_info
            
        except ValueError as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError(f"Token verification failed: {e}")
    
    def create_user_from_google_data(self, user_info, db_service):
        """
        Create or update a user based on Google authentication data
        
        Args:
            user_info (dict): User information from Google
            db_service: Database service for user operations
            
        Returns:
            dict: User record from database
        """
        try:
            # Check if user exists
            existing_user = db_service.get_user_by_google_id(user_info['google_id'])
            
            if existing_user:
                # Update existing user
                updated_user = {
                    'id': existing_user['id'],
                    'name': user_info['name'],
                    'email': user_info['email'],
                    'profile_picture': user_info['picture'],
                    'last_login': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                db_service.update_user(updated_user)
                return db_service.get_user_by_id(existing_user['id'])
            else:
                # Create new user
                new_user = {
                    'google_id': user_info['google_id'],
                    'name': user_info['name'],
                    'email': user_info['email'],
                    'profile_picture': user_info['picture'],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'last_login': datetime.now().isoformat()
                }
                
                user_id = db_service.create_user(new_user)
                return db_service.get_user_by_id(user_id)
                
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def generate_jwt_token(self, user):
        """
        Generate a JWT token for the authenticated user
        
        Args:
            user (dict): User information to encode in the token
            
        Returns:
            str: JWT token
        """
        try:
            # Set token expiration
            exp_time = datetime.utcnow() + timedelta(seconds=self.jwt_expiration)
            
            # Create token payload
            payload = {
                'sub': str(user['id']),
                'name': user['name'],
                'email': user['email'],
                'iat': datetime.utcnow(),
                'exp': exp_time
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                self.jwt_secret,
                algorithm=self.jwt_algorithm
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token):
        """
        Verify a JWT token and extract user information
        
        Args:
            token (str): JWT token to verify
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise jwt.InvalidTokenError("Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise
    
    def refresh_token(self, token):
        """
        Refresh a valid JWT token
        
        Args:
            token (str): Current valid JWT token
            
        Returns:
            str: New JWT token with extended expiration
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            # Verify current token
            payload = self.verify_jwt_token(token)
            
            # Create new token with extended expiration
            exp_time = datetime.utcnow() + timedelta(seconds=self.jwt_expiration)
            payload['exp'] = exp_time
            payload['iat'] = datetime.utcnow()
            
            # Generate new token
            new_token = jwt.encode(
                payload,
                self.jwt_secret,
                algorithm=self.jwt_algorithm
            )
            
            return new_token
            
        except jwt.InvalidTokenError:
            logger.warning("Cannot refresh invalid token")
            raise

# Create singleton instance
auth_service = AuthService()