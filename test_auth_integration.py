#!/usr/bin/env python3
"""
Authentication Integration Test Script
Tests the complete authentication flow for TTSAI application
"""

import requests
import json
import time
import sys
from pathlib import Path

# Test configuration
BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test if backend is running and healthy"""
    print("=== Testing Backend Health ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("=== Testing Auth Endpoints ===")
    
    # Test auth endpoints availability
    endpoints = [
        "/api/auth/google",
        "/api/auth/user", 
        "/api/auth/logout",
        "/api/auth/session",
        "/api/auth/refresh"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            # For POST endpoints, expect 400 (missing data) or 401 (unauthorized)
            # For GET endpoints with auth required, expect 401 (unauthorized)
            if endpoint in ["/api/auth/google", "/api/auth/logout", "/api/auth/refresh"]:
                response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=5)
            else:
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            
            # Expected status codes for unauthenticated requests
            expected_codes = [400, 401, 405]  # Bad request, Unauthorized, Method not allowed
            
            if response.status_code in expected_codes:
                print(f"✅ {endpoint} - Available (status: {response.status_code})")
                results[endpoint] = True
            else:
                print(f"⚠️ {endpoint} - Unexpected status: {response.status_code}")
                results[endpoint] = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Not accessible: {e}")
            results[endpoint] = False
    
    return all(results.values())

def test_cors_configuration():
    """Test CORS configuration"""
    print("=== Testing CORS Configuration ===")
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(f"{BACKEND_URL}/api/auth/google", headers=headers, timeout=5)
        
        if response.status_code == 200:
            cors_headers = response.headers
            if 'Access-Control-Allow-Origin' in cors_headers:
                print("✅ CORS is properly configured!")
                print(f"   Allowed Origin: {cors_headers.get('Access-Control-Allow-Origin')}")
                return True
            else:
                print("⚠️ CORS headers missing in response")
                return False
        else:
            print(f"⚠️ CORS preflight failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_database_connection():
    """Test database connection and auth tables"""
    print("=== Testing Database Connection ===")
    
    try:
        # Import database components
        sys.path.append('backend')
        from db_service_auth import AuthDBService
        
        # Test database connection
        auth_db = AuthDBService('backend/ttsai.db')
        
        # Test creating a dummy user (will be cleaned up)
        test_user_data = {
            'google_id': 'test_google_id_12345',
            'name': 'Test User',
            'email': 'test@example.com',
            'profile_picture': 'https://example.com/avatar.jpg'
        }
        
        # Create test user
        user_id = auth_db.create_user(test_user_data)
        print(f"✅ Created test user with ID: {user_id}")
        
        # Retrieve test user
        user = auth_db.get_user_by_id(user_id)
        if user and user['email'] == 'test@example.com':
            print("✅ User retrieval successful!")
        else:
            print("❌ User retrieval failed!")
            return False
        
        # Clean up test user
        import sqlite3
        conn = sqlite3.connect('backend/ttsai.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        print("✅ Test user cleaned up!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_environment_configuration():
    """Test environment configuration"""
    print("=== Testing Environment Configuration ===")
    
    # Check backend .env
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        print("❌ Backend .env file not found!")
        return False
    
    with open(backend_env, 'r') as f:
        backend_content = f.read()
    
    # Check for required variables
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'JWT_SECRET',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        if var not in backend_content:
            missing_vars.append(var)
        elif 'your_google_oauth_client_id_from_console' in backend_content or 'your_google_oauth_client_secret_from_console' in backend_content:
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    if placeholder_vars:
        print(f"⚠️ Placeholder values found for: {placeholder_vars}")
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
        print("⚠️ Frontend Google Client ID not configured!")
        print("Please run: python setup_google_oauth.py")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def test_google_oauth_config():
    """Test Google OAuth configuration"""
    print("=== Testing Google OAuth Configuration ===")
    
    try:
        sys.path.append('backend')
        from auth_config import get_auth_config
        
        config = get_auth_config()
        
        if not config['google_client_id'] or config['google_client_id'] == 'your_google_oauth_client_id_from_console':
            print("❌ Google Client ID not configured!")
            return False
        
        if not config['google_client_secret'] or config['google_client_secret'] == 'your_google_oauth_client_secret_from_console':
            print("❌ Google Client Secret not configured!")
            return False
        
        if not config['jwt_secret']:
            print("❌ JWT Secret not configured!")
            return False
        
        print("✅ Google OAuth configuration is valid!")
        print(f"   Client ID: {config['google_client_id'][:20]}...")
        print(f"   JWT Secret: {config['jwt_secret'][:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth config test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all authentication tests"""
    print("🔐 TTSAI Authentication Integration Test")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("Google OAuth Configuration", test_google_oauth_config),
        ("Database Connection", test_database_connection),
        ("Backend Health", test_backend_health),
        ("Auth Endpoints", test_auth_endpoints),
        ("CORS Configuration", test_cors_configuration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print()
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print()
    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print()
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Authentication is ready for deployment.")
        print()
        print("Next steps:")
        print("1. Start the backend: cd backend && python app.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Test login at: http://localhost:3000/login")
        print("4. Deploy with: python deploy_with_auth.py")
    else:
        print("⚠️ Some tests failed. Please fix the issues before deployment.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)