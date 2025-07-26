#!/usr/bin/env python3
"""
Google OAuth Setup Script for TTSAI Application
This script helps set up Google OAuth credentials for both backend and frontend.
"""

import os
import secrets
import json

def generate_jwt_secret():
    """Generate a secure JWT secret"""
    return secrets.token_hex(32)

def setup_google_oauth():
    """Interactive setup for Google OAuth credentials"""
    print("=== Google OAuth Setup for TTSAI ===")
    print()
    print("Before running this script, you need to:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Google+ API and Google Identity API")
    print("4. Go to Credentials > Create Credentials > OAuth 2.0 Client ID")
    print("5. Set application type to 'Web application'")
    print("6. Add authorized JavaScript origins:")
    print("   - http://localhost:3000 (for development)")
    print("   - https://your-netlify-domain.netlify.app (for production)")
    print("7. Add authorized redirect URIs:")
    print("   - http://localhost:5000/api/auth/google/callback (for development)")
    print("   - https://your-backend-domain/api/auth/google/callback (for production)")
    print()
    
    # Get credentials from user
    client_id = input("Enter your Google OAuth Client ID: ").strip()
    client_secret = input("Enter your Google OAuth Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Error: Both Client ID and Client Secret are required!")
        return False
    
    # Generate JWT secret
    jwt_secret = generate_jwt_secret()
    
    # Update backend .env
    backend_env_path = "backend/.env"
    if os.path.exists(backend_env_path):
        with open(backend_env_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder values
        content = content.replace(
            'GOOGLE_CLIENT_ID="your_google_oauth_client_id_from_console"',
            f'GOOGLE_CLIENT_ID="{client_id}"'
        )
        content = content.replace(
            'GOOGLE_CLIENT_SECRET="your_google_oauth_client_secret_from_console"',
            f'GOOGLE_CLIENT_SECRET="{client_secret}"'
        )
        
        # Update JWT secret if it's the default one
        if 'JWT_SECRET="ab6ae859453bdb65cc660897807ee0c8e6ad533ff8640dc8ea74b33ed2834707"' in content:
            content = content.replace(
                'JWT_SECRET="ab6ae859453bdb65cc660897807ee0c8e6ad533ff8640dc8ea74b33ed2834707"',
                f'JWT_SECRET="{jwt_secret}"'
            )
        
        with open(backend_env_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Updated {backend_env_path}")
    else:
        print(f"Warning: {backend_env_path} not found!")
    
    # Update frontend .env
    frontend_env_path = "frontend/.env"
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder value
        content = content.replace(
            'REACT_APP_GOOGLE_CLIENT_ID="your_google_oauth_client_id_from_console"',
            f'REACT_APP_GOOGLE_CLIENT_ID="{client_id}"'
        )
        
        with open(frontend_env_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Updated {frontend_env_path}")
    else:
        print(f"Warning: {frontend_env_path} not found!")
    
    # Update frontend production env
    frontend_prod_env_path = "frontend/.env.production"
    if os.path.exists(frontend_prod_env_path):
        with open(frontend_prod_env_path, 'r') as f:
            content = f.read()
        
        # Add or update Google Client ID
        if 'REACT_APP_GOOGLE_CLIENT_ID' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('REACT_APP_GOOGLE_CLIENT_ID'):
                    lines[i] = f'REACT_APP_GOOGLE_CLIENT_ID="{client_id}"'
                    break
            content = '\n'.join(lines)
        else:
            content += f'\nREACT_APP_GOOGLE_CLIENT_ID="{client_id}"\n'
        
        with open(frontend_prod_env_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Updated {frontend_prod_env_path}")
    
    print()
    print("=== Setup Complete! ===")
    print("Your Google OAuth credentials have been configured.")
    print()
    print("Next steps:")
    print("1. Test the authentication locally:")
    print("   - Start backend: cd backend && python app.py")
    print("   - Start frontend: cd frontend && npm start")
    print("   - Visit http://localhost:3000 and try logging in")
    print()
    print("2. For production deployment:")
    print("   - Update the authorized origins and redirect URIs in Google Console")
    print("   - Deploy to Google Cloud and Netlify")
    print()
    
    return True

if __name__ == "__main__":
    setup_google_oauth()