#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests
import json
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
API_BASE = os.getenv('API_BASE', 'http://localhost:5000/api')

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f'{API_BASE}/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status', 'N/A')}")
            print(f"   Services: {data.get('services', {})}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("Testing authentication endpoints...")
    try:
        # Test auth routes availability
        response = requests.post(f'{API_BASE}/auth/google', json={})
        if response.status_code == 400:  # Expected error for missing token
            print("✅ Google auth endpoint available")
        else:
            print(f"❌ Google auth endpoint unexpected response: {response.status_code}")
            return False
        
        # Test session check endpoint
        response = requests.get(f'{API_BASE}/auth/session')
        if response.status_code == 401:  # Expected error for missing token
            print("✅ Session check endpoint available")
        else:
            print(f"❌ Session check endpoint unexpected response: {response.status_code}")
            return False
        
        # Test user info endpoint
        response = requests.get(f'{API_BASE}/auth/user')
        if response.status_code == 401:  # Expected error for missing token
            print("✅ User info endpoint available")
        else:
            print(f"❌ User info endpoint unexpected response: {response.status_code}")
            return False
        
        # Test logout endpoint
        response = requests.post(f'{API_BASE}/auth/logout')
        if response.status_code == 200:
            print("✅ Logout endpoint available")
        else:
            print(f"❌ Logout endpoint unexpected response: {response.status_code}")
            return False
        
        # Test token refresh endpoint
        response = requests.post(f'{API_BASE}/auth/refresh', json={})
        if response.status_code == 400:  # Expected error for missing token
            print("✅ Token refresh endpoint available")
        else:
            print(f"❌ Token refresh endpoint unexpected response: {response.status_code}")
            return False
        
        return True
    except requests.RequestException as e:
        print(f"❌ Auth endpoints error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Authentication Backend APIs\n")
    
    tests = [
        test_health,
        test_auth_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication tests passed!")
    else:
        print("⚠️ Some tests failed. Check the backend logs for details.")

if __name__ == '__main__':
    main()