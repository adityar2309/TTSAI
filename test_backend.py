#!/usr/bin/env python3
import requests
import json

# Test the backend API
API_URL = "https://ttsai-backend-321805997355.us-central1.run.app/api"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_translation():
    """Test translation endpoint"""
    print("\nTesting translation endpoint (English to Hindi)...")
    try:
        data = {
            "text": "hello",
            "sourceLang": "en", 
            "targetLang": "hi"
        }
        
        response = requests.post(f"{API_URL}/translate", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Translation successful!")
            print(f"Translation: {result.get('translation', 'N/A')}")
            print(f"Romanization: {result.get('romanization', 'N/A')}")
            print(f"Romanization System: {result.get('romanization_system', 'N/A')}")
            print(f"Source Language: {result.get('source_lang', 'N/A')}")
            print(f"Target Language: {result.get('target_lang', 'N/A')}")
            
            # Check if we're getting proper JSON structure vs raw JSON text
            translation = result.get('translation', '')
            if translation.startswith('```json') or translation.startswith('{'):
                print("❌ Still receiving raw JSON - fix not working properly")
                return False
            else:
                print("✅ Receiving clean translation text - fix working correctly!")
                return True
        else:
            print(f"❌ Translation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Translation test failed: {e}")
        return False

def test_spanish_translation():
    """Test translation to a Latin script language (no romanization)"""
    print("\nTesting translation endpoint (English to Spanish)...")
    try:
        data = {
            "text": "hello",
            "sourceLang": "en", 
            "targetLang": "es"
        }
        
        response = requests.post(f"{API_URL}/translate", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Spanish translation successful!")
            print(f"Translation: {result.get('translation', 'N/A')}")
            print(f"Has romanization: {'romanization' in result}")
            return True
        else:
            print(f"❌ Spanish translation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Spanish translation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TTSAI Backend API")
    print("=" * 50)
    
    # Run tests
    health_ok = test_health()
    hindi_ok = test_translation()
    spanish_ok = test_spanish_translation()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Hindi Translation: {'✅ PASS' if hindi_ok else '❌ FAIL'}")
    print(f"Spanish Translation: {'✅ PASS' if spanish_ok else '❌ FAIL'}")
    
    if all([health_ok, hindi_ok, spanish_ok]):
        print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.") 