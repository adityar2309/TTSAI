#!/usr/bin/env python3
"""
Complete deployment script with authentication for TTSAI
This script handles:
1. Authentication setup verification
2. Backend deployment to Google Cloud Run
3. Frontend deployment to Netlify
4. Environment configuration for production
"""

import os
import subprocess
import sys
import json
import time
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_auth_setup():
    """Check if authentication is properly configured"""
    print("=== Checking Authentication Setup ===")
    
    # Check backend .env
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        print("❌ Backend .env file not found!")
        return False
    
    with open(backend_env, 'r') as f:
        backend_content = f.read()
    
    if 'your_google_oauth_client_id_from_console' in backend_content:
        print("❌ Google OAuth credentials not configured in backend!")
        print("Please run: python setup_google_oauth.py")
        return False
    
    # Check frontend .env
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        print("❌ Frontend .env file not found!")
        return False
    
    with open(frontend_env, 'r') as f:
        frontend_content = f.read()
    
    if 'your_google_oauth_client_id_from_console' in frontend_content:
        print("❌ Google OAuth credentials not configured in frontend!")
        print("Please run: python setup_google_oauth.py")
        return False
    
    print("✅ Authentication setup verified!")
    return True

def setup_backend_production_env():
    """Setup backend production environment variables"""
    print("=== Setting up Backend Production Environment ===")
    
    # Read development .env
    with open("backend/.env", 'r') as f:
        env_content = f.read()
    
    # Update for production
    production_env = env_content.replace(
        'FLASK_ENV=development',
        'FLASK_ENV=production'
    ).replace(
        'http://localhost:5000/api/auth/google/callback',
        'https://ttsai-backend-321805997355.us-central1.run.app/api/auth/google/callback'
    )
    
    # Write production .env
    with open("backend/.env.production", 'w') as f:
        f.write(production_env)
    
    print("✅ Backend production environment configured!")

def deploy_backend():
    """Deploy backend to Google Cloud Run"""
    print("=== Deploying Backend to Google Cloud Run ===")
    
    # Setup production environment
    setup_backend_production_env()
    
    # Copy production env for deployment
    run_command("copy backend\\.env.production backend\\.env", check=False)
    
    # Deploy to Google Cloud Run
    deploy_cmd = (
        "gcloud run deploy ttsai-backend "
        "--source backend "
        "--platform managed "
        "--region us-central1 "
        "--allow-unauthenticated "
        "--memory 1Gi "
        "--cpu 1 "
        "--timeout 300 "
        "--max-instances 10 "
        "--set-env-vars FLASK_ENV=production"
    )
    
    result = run_command(deploy_cmd)
    
    if result.returncode == 0:
        print("✅ Backend deployed successfully!")
        return True
    else:
        print("❌ Backend deployment failed!")
        return False

def setup_frontend_production_env():
    """Setup frontend production environment"""
    print("=== Setting up Frontend Production Environment ===")
    
    # Read current production env or create new one
    prod_env_path = Path("frontend/.env.production")
    
    if prod_env_path.exists():
        with open(prod_env_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Ensure production API URL is set
    api_url_line = "REACT_APP_API_URL=https://ttsai-backend-321805997355.us-central1.run.app/api"
    
    if "REACT_APP_API_URL" in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('REACT_APP_API_URL'):
                lines[i] = api_url_line
                break
        content = '\n'.join(lines)
    else:
        content += f"\n{api_url_line}\n"
    
    # Add Google Client ID if not present
    with open("frontend/.env", 'r') as f:
        dev_content = f.read()
    
    for line in dev_content.split('\n'):
        if line.startswith('REACT_APP_GOOGLE_CLIENT_ID') and 'REACT_APP_GOOGLE_CLIENT_ID' not in content:
            content += f"\n{line}\n"
            break
    
    with open(prod_env_path, 'w') as f:
        f.write(content)
    
    print("✅ Frontend production environment configured!")

def build_frontend():
    """Build frontend for production"""
    print("=== Building Frontend ===")
    
    # Setup production environment
    setup_frontend_production_env()
    
    # Install dependencies
    run_command("npm install", cwd="frontend")
    
    # Build for production
    run_command("npm run build", cwd="frontend")
    
    print("✅ Frontend built successfully!")

def deploy_frontend():
    """Deploy frontend to Netlify"""
    print("=== Deploying Frontend to Netlify ===")
    
    # Build frontend first
    build_frontend()
    
    # Deploy to Netlify
    result = run_command("netlify deploy --prod --dir=build", cwd="frontend", check=False)
    
    if result.returncode == 0:
        print("✅ Frontend deployed successfully!")
        return True
    else:
        print("❌ Frontend deployment failed!")
        print("Make sure you have Netlify CLI installed and are logged in:")
        print("npm install -g netlify-cli")
        print("netlify login")
        return False

def update_cors_origins():
    """Update CORS origins in backend for production"""
    print("=== Updating CORS Origins ===")
    
    # This would typically be done in the backend code
    # For now, we'll just print a reminder
    print("📝 Remember to update CORS origins in backend/app.py if needed")
    print("Current origins should include:")
    print("- https://ttsai.netlify.app")
    print("- https://*.netlify.app")

def test_deployment():
    """Test the deployed application"""
    print("=== Testing Deployment ===")
    
    backend_url = "https://ttsai-backend-321805997355.us-central1.run.app"
    frontend_url = "https://ttsai.netlify.app"
    
    print(f"Backend URL: {backend_url}")
    print(f"Frontend URL: {frontend_url}")
    
    # Test backend health
    try:
        import requests
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed!")
        else:
            print(f"⚠️ Backend health check returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Backend health check failed: {e}")
    
    print(f"🌐 Visit {frontend_url} to test the application")

def push_to_github():
    """Push changes to GitHub"""
    print("=== Pushing to GitHub ===")
    
    try:
        # Check git status
        result = run_command("git status --porcelain", check=False)
        if result.returncode != 0:
            print("❌ Git repository not initialized!")
            return False
        
        if not result.stdout.strip():
            print("✅ No changes to commit")
            return True
        
        # Add all changes
        run_command("git add .")
        
        # Commit changes
        commit_message = """Implement complete authentication system with Google OAuth

- Add Google OAuth integration for backend and frontend
- Implement JWT-based session management  
- Add user database models and operations
- Create comprehensive auth components for React
- Add authentication middleware and route protection
- Include deployment scripts for Google Cloud and Netlify
- Add testing and setup automation scripts
- Update CORS configuration for production
- Add comprehensive documentation and guides"""
        
        run_command(f'git commit -m "{commit_message}"')
        
        # Push to GitHub
        run_command("git push origin main")
        
        print("✅ Successfully pushed to GitHub!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to push to GitHub: {e}")
        return False

def main():
    """Main deployment function"""
    print("=== TTSAI Deployment with Authentication ===")
    print()
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the project root directory!")
        sys.exit(1)
    
    # Check authentication setup
    if not check_auth_setup():
        print("❌ Authentication setup incomplete!")
        print("Please run: python setup_google_oauth.py")
        sys.exit(1)
    
    # Ask user what to deploy
    print("What would you like to deploy?")
    print("1. Backend only")
    print("2. Frontend only") 
    print("3. Both backend and frontend")
    print("4. Push to GitHub and deploy")
    print("5. Test deployment")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    success = True
    
    if choice == '4':
        success &= push_to_github()
        if success:
            success &= deploy_backend()
            success &= deploy_frontend()
    elif choice in ['1', '3']:
        success &= deploy_backend()
    
    if choice in ['2', '3']:
        success &= deploy_frontend()
    
    if choice == '5':
        test_deployment()
        return
    
    if success:
        print()
        print("🎉 Deployment completed successfully!")
        update_cors_origins()
        test_deployment()
    else:
        print()
        print("❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()