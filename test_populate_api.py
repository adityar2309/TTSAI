#!/usr/bin/env python3
"""
Test script to populate multilingual words via API
"""
import requests
import json

def test_populate_words():
    """Test the populate-words API endpoint"""
    url = "https://ttsai-backend-321805997355.us-central1.run.app/api/debug/populate-words"
    
    try:
        print("🌍 Testing word population API...")
        
        # Make POST request
        response = requests.post(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"💥 Request failed: {e}")

if __name__ == "__main__":
    test_populate_words() 