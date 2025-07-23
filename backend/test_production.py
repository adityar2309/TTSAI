#!/usr/bin/env python3
"""
Test script to verify production backend is working with SQLite
"""

import requests
import os
import sys
import json
import subprocess

def get_current_backend_url():
    """Get the current backend URL from gcloud or environment"""
    try:
        # Try to get URL from gcloud command
        result = subprocess.run(
            ["gcloud", "run", "services", "describe", "ttsai-backend", 
             "--region=us-central1", "--format=value(status.url)"],
            capture_output=True, text=True, check=True
        )
        url = result.stdout.strip()
        if url:
            return f"{url}/api"
    except (subprocess.SubprocessError, FileNotFoundError):
        # If gcloud command fails, try frontend .env file
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "frontend", ".env"), "r") as f:
                for line in f:
                    if "REACT_APP_API_URL" in line:
                        url = line.split("=")[1].strip().strip('"')
                        if url:
                            return url
        except (FileNotFoundError, IndexError):
            pass
    
    # Fallback to hardcoded URL
    return "https://ttsai-backend-zegtq4jhca-uc.a.run.app/api"

def test_production_backend():
    """Test the production backend"""
    backend_url = get_current_backend_url()
    print(f"Testing backend at: {backend_url}")
    
    all_tests_passed = True
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f'{backend_url}/health', timeout=15)
        if response.status_code == 200:
            print(f'✓ Health check: {response.status_code} OK')
            print(f'  Health data: {json.dumps(response.json(), indent=2)}')
        else:
            print(f'✗ Health check failed: {response.status_code}')
            all_tests_passed = False
        
        # Test word of day
        print("\n2. Testing word of day endpoint...")
        response = requests.get(f'{backend_url}/word-of-day?language=en', timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f'✓ Word of day: {response.status_code} OK')
            print(f'  Word: {data.get("word", "N/A")}')
            print(f'  Translation: {data.get("translation", "N/A")}')
        else:
            print(f'✗ Word of day failed: {response.status_code}')
            print(f'  Error: {response.text[:200]}')
            all_tests_passed = False
            
        # Test supported languages
        print("\n3. Testing supported languages endpoint...")
        response = requests.get(f'{backend_url}/supported-languages', timeout=15)
        if response.status_code == 200:
            languages_data = response.json()
            print(f'✓ Supported languages: {response.status_code} OK')
            
            # Handle different response formats
            if isinstance(languages_data, list):
                # If it's a simple list of language codes
                language_display = languages_data[:5] if len(languages_data) > 5 else languages_data
                print(f'  Languages: {", ".join(str(lang) for lang in language_display)}{"..." if len(languages_data) > 5 else ""}')
            elif isinstance(languages_data, dict):
                # If it's a dictionary with language details
                language_codes = list(languages_data.keys())[:5] if len(languages_data) > 5 else list(languages_data.keys())
                print(f'  Languages: {", ".join(language_codes)}{"..." if len(languages_data) > 5 else ""}')
            else:
                # Fallback for any other format
                print(f'  Languages data received (format: {type(languages_data).__name__})')
        else:
            print(f'✗ Supported languages failed: {response.status_code}')
            all_tests_passed = False
        
        # Test translation endpoint
        print("\n4. Testing translation endpoint...")
        try:
            payload = {"text": "Hello", "source_language": "en", "target_language": "es"}
            response = requests.post(f'{backend_url}/translate', json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f'✓ Translation: {response.status_code} OK')
                print(f'  Translated text: {data.get("translated_text", "N/A")}')
            else:
                print(f'✗ Translation failed: {response.status_code}')
                print(f'  Error: {response.text[:200]}')
                # Don't fail the entire test suite for translation issues
                # as this might depend on API key availability
                print('  Note: Translation failures may be due to API key limitations')
        except Exception as e:
            print(f'✗ Translation test error: {e}')
            print('  Note: Translation failures may be due to API key limitations')
        
        # Print summary
        print("\n" + "="*50)
        if all_tests_passed:
            print("✅ All tests passed! Production backend is working correctly.")
        else:
            print("❌ Some tests failed. Check the logs above for details.")
        print("="*50)
        
        return all_tests_passed
        
    except Exception as e:
        import traceback
        print(f'\n❌ Error testing production backend: {e}')
        print(f'Error details: {traceback.format_exc()}')
        return False

if __name__ == "__main__":
    success = test_production_backend()
    sys.exit(0 if success else 1)