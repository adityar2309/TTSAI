#!/usr/bin/env python3
"""
Test script to verify production backend is working with SQLite
"""

import requests

def test_production_backend():
    """Test the production backend"""
    backend_url = "https://ttsai-backend-321805997355.us-central1.run.app/api"
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f'{backend_url}/health', timeout=10)
        print(f'Health check: {response.status_code}')
        if response.status_code == 200:
            print(f'Health data: {response.json()}')
        
        # Test word of day
        print("\nTesting word of day endpoint...")
        response = requests.get(f'{backend_url}/word-of-day?language=en', timeout=10)
        print(f'Word of day: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Word: {data.get("word", "N/A")}')
            print(f'Translation: {data.get("translation", "N/A")}')
        else:
            print(f'Error response: {response.text[:200]}')
            
        # Test supported languages
        print("\nTesting supported languages endpoint...")
        response = requests.get(f'{backend_url}/supported-languages', timeout=10)
        print(f'Supported languages: {response.status_code}')
        
        return True
        
    except Exception as e:
        print(f'Error testing production backend: {e}')
        return False

if __name__ == "__main__":
    test_production_backend() 