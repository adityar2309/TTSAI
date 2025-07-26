#!/usr/bin/env python3
"""
Test script to verify auth configuration is loading correctly
"""

from auth_config import get_auth_config

def test_auth_config():
    """Test that auth configuration loads correctly"""
    try:
        config = get_auth_config()
        
        print("✅ Auth configuration loaded successfully!")
        print(f"   Callback URL: {config['google_callback_url']}")
        print(f"   JWT Algorithm: {config['jwt_algorithm']}")
        print(f"   JWT Expiration: {config['jwt_expiration']} seconds")
        print(f"   Google Scopes: {', '.join(config['google_scopes'])}")
        
        # Check if client ID and secret are set (but don't print them)
        if config['google_client_id']:
            print("   Google Client ID: Configured")
        else:
            print("   Google Client ID: Not set")
            
        if config['google_client_secret']:
            print("   Google Client Secret: Configured")
        else:
            print("   Google Client Secret: Not set")
            
        return True
        
    except Exception as e:
        print(f"❌ Error loading auth configuration: {e}")
        return False

if __name__ == "__main__":
    test_auth_config()