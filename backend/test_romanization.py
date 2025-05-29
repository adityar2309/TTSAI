#!/usr/bin/env python3
"""
Test script for romanization functionality in TTSAI backend
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:5000/api"

def test_basic_translation_with_romanization():
    """Test basic translation endpoint with languages that should include romanization"""
    
    test_cases = [
        {
            "text": "Hello, how are you?",
            "sourceLang": "en",
            "targetLang": "ja",
            "description": "English to Japanese (should include romanization)"
        },
        {
            "text": "Good morning",
            "sourceLang": "en", 
            "targetLang": "zh",
            "description": "English to Chinese (should include romanization)"
        },
        {
            "text": "Thank you",
            "sourceLang": "en",
            "targetLang": "hi",
            "description": "English to Hindi (should include romanization)"
        },
        {
            "text": "How much does this cost?",
            "sourceLang": "en",
            "targetLang": "ar",
            "description": "English to Arabic (should include romanization)"
        },
        {
            "text": "Where is the station?",
            "sourceLang": "en",
            "targetLang": "ko",
            "description": "English to Korean (should include romanization)"
        },
        {
            "text": "Nice to meet you",
            "sourceLang": "en",
            "targetLang": "es",
            "description": "English to Spanish (should NOT include romanization)"
        }
    ]
    
    print("Testing Basic Translation with Romanization")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: '{test_case['text']}' ({test_case['sourceLang']} -> {test_case['targetLang']})")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/translate",
                json={
                    "text": test_case["text"],
                    "sourceLang": test_case["sourceLang"],
                    "targetLang": test_case["targetLang"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Translation: {data.get('translation', 'N/A')}")
                
                if data.get('romanization'):
                    print(f"✅ Romanization: {data['romanization']}")
                    if data.get('romanization_system'):
                        print(f"   System: {data['romanization_system']}")
                else:
                    print("ℹ️  No romanization provided")
                    
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

def test_advanced_translation_with_romanization():
    """Test advanced translation endpoint with romanization"""
    
    test_case = {
        "text": "I love learning new languages",
        "sourceLang": "en",
        "targetLang": "ja",
        "formality": "neutral"
    }
    
    print("\n\nTesting Advanced Translation with Romanization")
    print("=" * 50)
    print(f"Input: '{test_case['text']}' ({test_case['sourceLang']} -> {test_case['targetLang']})")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/advanced-translate",
            json=test_case,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main Translation: {data.get('main_translation', 'N/A')}")
            
            pronunciation = data.get('pronunciation', {})
            if pronunciation.get('romanization'):
                print(f"✅ Romanization: {pronunciation['romanization']}")
                if pronunciation.get('romanization_system'):
                    print(f"   System: {pronunciation['romanization_system']}")
            else:
                print("ℹ️  No romanization in advanced translation")
                
            # Show other pronunciation info
            if pronunciation.get('ipa'):
                print(f"📝 IPA: {pronunciation['ipa']}")
            if pronunciation.get('phonetic'):
                print(f"📝 Phonetic: {pronunciation['phonetic']}")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health Check Passed")
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {service}: {'Available' if status else 'Unavailable'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("TTSAI Romanization Test Suite")
    print("============================")
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ API is not available. Please make sure the backend is running on localhost:5000")
        sys.exit(1)
    
    # Run tests
    test_basic_translation_with_romanization()
    test_advanced_translation_with_romanization()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nNote: Results depend on the Gemini AI model's responses.")
    print("Romanization quality may vary based on the AI model's capabilities.") 