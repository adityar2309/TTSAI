#!/usr/bin/env python3
"""
Setup script for TTSAI environment configuration
"""
import os
import sys

def create_backend_env():
    """Create a basic .env file for backend development"""
    backend_env_path = os.path.join('backend', '.env')
    
    if os.path.exists(backend_env_path):
        print(f"✓ Environment file already exists at {backend_env_path}")
        return
    
    # Create a minimal .env file for development
    env_content = """# TTSAI Backend Environment Configuration
# For development and testing

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
FLASK_DEBUG=True

# Optional: Add your Gemini API key here for full functionality
# GEMINI_API_KEY=your_api_key_here

# Optional: Google Cloud credentials path
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Database (defaults to SQLite)
DATABASE_URL=sqlite:///ttsai.db

# Application Settings
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,https://ttsai.netlify.app

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache Settings
CACHE_DURATION=300

# Logging
LOG_LEVEL=INFO
"""
    
    try:
        os.makedirs('backend', exist_ok=True)
        with open(backend_env_path, 'w') as f:
            f.write(env_content)
        print(f"✓ Created environment file at {backend_env_path}")
        print("📝 Edit this file to add your API keys and configuration")
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")

def create_frontend_env():
    """Create a basic .env file for frontend development"""
    frontend_env_path = os.path.join('frontend', '.env')
    
    if os.path.exists(frontend_env_path):
        print(f"✓ Environment file already exists at {frontend_env_path}")
        return
    
    env_content = """# TTSAI Frontend Environment Configuration
# For development

REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENVIRONMENT=development
"""
    
    try:
        os.makedirs('frontend', exist_ok=True)
        with open(frontend_env_path, 'w') as f:
            f.write(env_content)
        print(f"✓ Created environment file at {frontend_env_path}")
    except Exception as e:
        print(f"❌ Failed to create frontend environment file: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up TTSAI development environment...")
    print()
    
    # Create backend .env
    create_backend_env()
    
    # Create frontend .env
    create_frontend_env()
    
    print()
    print("🎉 Environment setup complete!")
    print()
    print("Next steps:")
    print("1. Edit backend/.env to add your GEMINI_API_KEY")
    print("2. Install dependencies: cd backend && pip install -r requirements.txt")
    print("3. Install frontend dependencies: cd frontend && npm install")
    print("4. Start backend: cd backend && python app.py")
    print("5. Start frontend: cd frontend && npm start")

if __name__ == '__main__':
    main() 