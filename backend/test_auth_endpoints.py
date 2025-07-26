#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests
import json
import sys
import time

# Test configuration
BASE_URL = "http://localhost:5000/api"
AUTH_URL = f"{BASE_URL}/auth"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_auth_endpoints_structure():
    """Test if auth endpoints are accessible (should return 400/401, not 404)"""
    endpoints = [
        ("POST", "/google", {"token": "fake_token"}),
        ("GET", "/user", None),
        ("POST", "/logout", {}),
        ("GET", "/session", None),
        ("POST", "/refresh", {"token": "fake_token"})
    ]
    
    results = []
    
    for method, endpoint, data in endpoints:
        try:
            url = f"{AUTH_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            # We expect 400/401 for invalid data, not 404 for missing endpoints
            if response.status_code == 404:
                print(f"❌ {method} {endpoint}: Endpoint not found (404)")
                results.append(False)
            elif response.status_code in [400, 401, 403]:
                print(f"✅ {method} {endpoint}: Endpoint exists (got {response.status_code})")
                results.append(True)
            else:
                print(f"⚠️  {method} {endpoint}: Unexpected status {response.status_code}")
                results.append(True)  # Endpoint exists, just unexpected response
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint}: Request error: {e}")
            results.append(False)
    
    return all(results)

def test_google_auth_endpoint():
    """Test Google auth endpoint with invalid token (should return 401)"""
    try:
        response = requests.post(
            f"{AUTH_URL}/google",
            json={"token": "invalid_google_token"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ Google auth endpoint properly validates tokens")
            return True
        elif response.status_code == 400:
            print("✅ Google auth endpoint properly validates request format")
            return True
        else:
            print(f"⚠️  Google auth endpoint returned unexpected status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Response: {error_data}")
            except:
                print(f"   Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Google auth endpoint error: {e}")
        return False

def test_protected_endpoints():
    """Test protected endpoints without token (should return 401)"""
    protected_endpoints = [
        ("GET", "/user"),
        ("GET", "/session")
    ]
    
    results = []
    
    for method, endpoint in protected_endpoints:
        try:
            url = f"{AUTH_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 401:
                print(f"✅ {endpoint}: Properly protected (401 without token)")
                results.append(True)
            else:
                print(f"❌ {endpoint}: Not properly protected (got {response.status_code})")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Request error: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run all authentication tests"""
    print("🔍 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test if server is running
    print("1. Testing server health...")
    if not test_health_endpoint():
        print("\n❌ Server is not running or not responding")
        print("Please start the server with: python app.py")
        sys.exit(1)
    
    print("\n2. Testing auth endpoint structure...")
    endpoints_ok = test_auth_endpoints_structure()
    
    print("\n3. Testing Google auth endpoint...")
    google_auth_ok = test_google_auth_endpoint()
    
    print("\n4. Testing protected endpoints...")
    protected_ok = test_protected_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Server Health: {'✅' if True else '❌'}")
    print(f"   Endpoint Structure: {'✅' if endpoints_ok else '❌'}")
    print(f"   Google Auth: {'✅' if google_auth_ok else '❌'}")
    print(f"   Protected Routes: {'✅' if protected_ok else '❌'}")
    
    if endpoints_ok and google_auth_ok and protected_ok:
        print("\n🎉 All authentication tests passed!")
        print("The backend authentication system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed.")
        print("Please check the server logs for more details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)