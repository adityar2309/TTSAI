#!/usr/bin/env python3
"""
Test Flask application integration with VectorService
"""

import sys
import os
import requests
import json
import time

# Add backend to path
sys.path.append('backend')

def test_flask_integration():
    """Test Flask application integration"""
    print("Testing Flask application integration with VectorService...")
    
    # Test if we can import the app
    try:
        from app import app, vector_service_available, vector_service
        print("✅ Successfully imported Flask app and vector service")
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False
    
    # Test vector service availability
    print(f"Vector service available: {vector_service_available}")
    if vector_service_available and vector_service:
        print(f"Vector service ready: {vector_service.is_ready()}")
        if not vector_service.is_ready():
            print("Loading vector index...")
            success = vector_service.load_index()
            print(f"Index loaded: {success}")
    
    # Test app context
    with app.app_context():
        print("✅ Flask app context working")
        
        # Test vector service in app context
        if vector_service_available and vector_service and vector_service.is_ready():
            stats = vector_service.get_stats()
            print(f"📊 Vector service stats in app context:")
            print(f"   - Documents: {stats.get('total_documents', 0)}")
            print(f"   - Languages: {len(stats.get('available_languages', []))}")
    
    print("✅ Flask integration test completed!")
    return True

def test_endpoints_locally():
    """Test endpoints if server is running locally"""
    print("\nTesting endpoints (if server is running on localhost:5000)...")
    
    base_url = "http://localhost:5000"
    
    # Test vector service status endpoint
    try:
        response = requests.get(f"{base_url}/api/vector-service/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector service status endpoint working")
            print(f"   - Available: {data.get('available', False)}")
            print(f"   - Ready: {data.get('ready', False)}")
        else:
            print(f"⚠️  Status endpoint returned {response.status_code}")
    except requests.exceptions.RequestException:
        print("⚠️  Server not running on localhost:5000 (this is expected)")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/vector-service/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector service health endpoint working")
            print(f"   - Healthy: {data.get('healthy', False)}")
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
    except requests.exceptions.RequestException:
        print("⚠️  Server not running on localhost:5000 (this is expected)")

if __name__ == "__main__":
    success = test_flask_integration()
    test_endpoints_locally()
    
    if success:
        print("\n🎉 Flask integration test completed successfully!")
    else:
        print("\n❌ Flask integration test failed!")