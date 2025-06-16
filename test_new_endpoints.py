#!/usr/bin/env python3
"""
Test script for the new Text-to-Speech and Speech-to-Text endpoints
"""

import requests
import json
import base64

# Backend URL
BACKEND_URL = "https://ttsai-backend-321805997355.us-central1.run.app"

def test_text_to_speech():
    """Test the new Text-to-Speech endpoint"""
    print("🎵 Testing Text-to-Speech endpoint...")
    
    url = f"{BACKEND_URL}/api/text-to-speech"
    
    test_data = {
        "text": "Hello, this is a test of the text-to-speech functionality.",
        "language": "en",
        "voiceGender": "NEUTRAL"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ TTS endpoint working!")
            print(f"   Provider: {data.get('provider', 'Unknown')}")
            print(f"   Format: {data.get('format', 'Unknown')}")
            print(f"   Audio length: {len(data.get('audio', ''))} characters")
            print(f"   Success: {data.get('success', False)}")
        else:
            print("❌ TTS endpoint failed!")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ TTS test failed with exception: {e}")

def test_speech_to_text():
    """Test the new Speech-to-Text endpoint"""
    print("\n🎤 Testing Speech-to-Text endpoint...")
    
    url = f"{BACKEND_URL}/api/speech-to-text"
    
    # For this test, we'll just check if the endpoint exists and handles requests properly
    test_data = {
        "language": "en"
    }
    
    try:
        response = requests.post(url, data=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            # Expected - no audio data provided
            data = response.json()
            if "No audio data provided" in data.get('error', ''):
                print("✅ STT endpoint working! (Expected 400 for missing audio)")
            else:
                print(f"❌ Unexpected error: {data.get('error', 'Unknown')}")
        elif response.status_code == 200:
            print("✅ STT endpoint working!")
            data = response.json()
            print(f"   Response: {data}")
        else:
            print("❌ STT endpoint failed!")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ STT test failed with exception: {e}")

def test_health_check():
    """Test the health check to verify deployment"""
    print("\n🏥 Testing health check...")
    
    url = f"{BACKEND_URL}/api/health"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Services: {data.get('services', {})}")
        else:
            print("❌ Health check failed!")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check failed with exception: {e}")

def test_cors():
    """Test CORS configuration"""
    print("\n🌐 Testing CORS configuration...")
    
    url = f"{BACKEND_URL}/api/health"
    
    headers = {
        "Origin": "https://ttsai.netlify.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        # Send OPTIONS request (preflight)
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"OPTIONS Status Code: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS preflight working!")
        else:
            print("❌ CORS preflight failed!")
            
    except Exception as e:
        print(f"❌ CORS test failed with exception: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing TTSAI Backend Endpoints")
    print("=" * 50)
    
    test_health_check()
    test_text_to_speech()
    test_speech_to_text()
    test_cors()
    
    print("\n" + "=" * 50)
    print("✨ Testing complete!")

if __name__ == "__main__":
    main() 