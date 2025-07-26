#!/usr/bin/env python3
"""
Validation script for Google OAuth configuration
Run this script to verify that your environment variables are properly configured.
"""

import os
import sys
from dotenv import load_dotenv

def validate_auth_config():
    """Validate that all required authentication environment variables are set"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Validating Google OAuth Configuration...")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'GOOGLE_CLIENT_ID': 'Google OAuth Client ID',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth Client Secret', 
        'GOOGLE_CALLBACK_URL': 'Google OAuth Callback URL',
        'JWT_SECRET': 'JWT Secret Key'
    }
    
    # Check each required variable
    missing_vars = []
    placeholder_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        
        if not value:
            missing_vars.append(f"❌ {var_name}: Missing")
            continue
            
        # Check for placeholder values
        placeholder_indicators = [
            'your_client_id_here',
            'your_client_secret_here', 
            'your_google_oauth_client_id_from_console',
            'your_google_oauth_client_secret_from_console',
            'generate_a_secure_random_string_here'
        ]
        
        if any(placeholder in value for placeholder in placeholder_indicators):
            placeholder_vars.append(f"⚠️  {var_name}: Contains placeholder value")
        else:
            print(f"✅ {var_name}: Configured")
    
    # Print missing variables
    if missing_vars:
        print("\n❌ Missing Environment Variables:")
        for var in missing_vars:
            print(f"   {var}")
    
    # Print placeholder variables
    if placeholder_vars:
        print("\n⚠️  Variables with Placeholder Values:")
        for var in placeholder_vars:
            print(f"   {var}")
    
    # Overall status
    print("\n" + "=" * 50)
    
    if not missing_vars and not placeholder_vars:
        print("🎉 All authentication environment variables are properly configured!")
        print("\nNext steps:")
        print("1. Start the backend server: python app.py")
        print("2. Start the frontend server: npm start")
        print("3. Test the Google OAuth login flow")
        return True
    else:
        print("❌ Configuration incomplete!")
        print("\nNext steps:")
        print("1. Review the GOOGLE_AUTH_SETUP.md guide")
        print("2. Set up Google OAuth credentials in Google Cloud Console")
        print("3. Update the .env files with actual values")
        print("4. Run this script again to validate")
        return False

def check_jwt_secret_strength():
    """Check if JWT secret is strong enough"""
    jwt_secret = os.getenv('JWT_SECRET')
    
    if not jwt_secret:
        return False
        
    if len(jwt_secret) < 32:
        print("⚠️  JWT_SECRET should be at least 32 characters long")
        return False
        
    if jwt_secret == "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456":
        print("⚠️  JWT_SECRET is using the default value - please generate a new one")
        print("   Run: python -c \"import secrets; print(secrets.token_hex(32))\"")
        return False
        
    return True

if __name__ == "__main__":
    print("Google OAuth Configuration Validator")
    print("=" * 50)
    
    # Validate configuration
    config_valid = validate_auth_config()
    
    # Check JWT secret strength
    print("\n🔐 JWT Secret Validation...")
    jwt_valid = check_jwt_secret_strength()
    
    if jwt_valid:
        print("✅ JWT Secret: Strong")
    
    # Exit with appropriate code
    if config_valid and jwt_valid:
        sys.exit(0)
    else:
        sys.exit(1)