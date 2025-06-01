#!/usr/bin/env python3
"""
Quick script to populate word-of-day data in production
"""
import requests

API_BASE = 'https://ttsai-backend-321805997355.us-central1.run.app/api'

def populate_words():
    """Call the debug endpoint to populate word-of-day data"""
    print("🔧 Fixing Word of Day data...")
    
    try:
        # Call the debug endpoint
        response = requests.post(f'{API_BASE}/debug/populate-words')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! {data.get('message')}")
            print(f"📊 Added: {data.get('added_count')} words")
            print(f"❌ Failed: {data.get('failed_count')} words")
            print(f"🎯 Verification: {data.get('verification')}")
            if data.get('test_word'):
                print(f"📝 Sample word: {data.get('test_word')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_word_of_day():
    """Test the word-of-day endpoint"""
    print("\n🧪 Testing word-of-day endpoint...")
    
    try:
        response = requests.get(f'{API_BASE}/word-of-day', params={'language': 'en'})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Word of day working!")
            print(f"📝 Word: {data.get('word')}")
            print(f"📖 Definition: {data.get('translation')}")
            return True
        else:
            print(f"❌ Still failing: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🛠️  Word of Day Fix Script")
    print("=" * 40)
    
    # Step 1: Populate the data
    if populate_words():
        print("\n" + "=" * 40)
        
        # Step 2: Test the endpoint
        if test_word_of_day():
            print("\n🎉 Word of Day is now working!")
        else:
            print("\n⚠️  Word of Day still has issues")
    else:
        print("\n❌ Failed to populate word data") 