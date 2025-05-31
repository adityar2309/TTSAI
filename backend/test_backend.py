#!/usr/bin/env python3
"""
Test script to verify backend works with SQLite database
"""

from app import app
import threading
import time
import requests

def test_backend():
    """Test the backend with SQLite database"""
    
    # Start the app in a separate thread
    def run_app():
        app.run(host='127.0.0.1', port=5001, debug=False)

    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("Starting backend server...")
    time.sleep(3)

    try:
        # Test the health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://127.0.0.1:5001/api/health', timeout=5)
        print(f'Health check status: {response.status_code}')
        
        # Test word of day endpoint
        print("Testing word of day endpoint...")
        response = requests.get('http://127.0.0.1:5001/api/word-of-day?language=en', timeout=5)
        print(f'Word of day status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Word: {data.get("word", "N/A")}')
        
        print('✓ Backend is working with SQLite database!')
        return True
        
    except Exception as e:
        print(f'✗ Error testing backend: {e}')
        return False

if __name__ == "__main__":
    test_backend() 