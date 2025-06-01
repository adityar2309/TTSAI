#!/usr/bin/env python3
"""
Test script for learning tools endpoints on the deployed backend
"""
import requests
import json

# Use the deployed backend URL instead of localhost
API_BASE = 'https://ttsai-backend-321805997355.us-central1.run.app/api'

def test_word_of_day():
    """Test word of the day endpoint"""
    print("Testing word of the day...")
    try:
        response = requests.get(f'{API_BASE}/word-of-day', params={'language': 'en'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Word of day: {data.get('word', 'N/A')}")
            return True
        else:
            print(f"❌ Word of day failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Word of day error: {e}")
        return False

def test_flashcards():
    """Test flashcards endpoints"""
    print("Testing flashcards...")
    try:
        # Test GET flashcards
        response = requests.get(f'{API_BASE}/flashcards', params={'userId': 'user123'})
        if response.status_code == 200:
            data = response.json()
            
            # Handle both response formats: dict with total or direct list
            if isinstance(data, dict):
                # New format: {"flashcards": [...], "total": N}
                total = data.get('total', 0)
                flashcards = data.get('flashcards', [])
            else:
                # Legacy format: [flashcard1, flashcard2, ...]
                total = len(data)
                flashcards = data
                
            print(f"✅ Fetched {total} flashcards")
            
            # Test POST new flashcard
            new_flashcard = {
                'userId': 'user123',
                'translation': {
                    'originalText': 'Good morning',
                    'translatedText': 'Buenos días',
                    'sourceLang': 'en',
                    'targetLang': 'es'
                },
                'difficulty': 'beginner',
                'category': 'greetings'
            }
            
            response = requests.post(f'{API_BASE}/flashcards', json=new_flashcard)
            if response.status_code == 200:
                print("✅ Created new flashcard")
                return True
            else:
                print(f"❌ Create flashcard failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Get flashcards failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Flashcards error: {e}")
        return False

def test_quiz_generation():
    """Test quiz generation endpoint"""
    print("Testing quiz generation...")
    try:
        quiz_data = {
            'userId': 'user123',
            'language': 'en',
            'difficulty': 'beginner',
            'type': 'mixed'
        }
        
        response = requests.post(f'{API_BASE}/quiz/generate', json=quiz_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated quiz with {data.get('total_questions', 0)} questions")
            return True
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Quiz generation error: {e}")
        return False

def test_progress():
    """Test progress endpoint"""
    print("Testing progress...")
    try:
        response = requests.get(f'{API_BASE}/progress', params={'userId': 'user123'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Progress: {data.get('total_xp', 0)} XP, {data.get('words_learned', 0)} words learned")
            return True
        else:
            print(f"❌ Progress failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Progress error: {e}")
        return False

def test_conversation():
    """Test conversation endpoint"""
    print("Testing conversation...")
    try:
        conv_data = {
            'text': 'Hello, how are you?',
            'language': 'es',
            'userId': 'user123',
            'context': 'general',
            'proficiency': 'beginner'
        }
        
        response = requests.post(f'{API_BASE}/conversation', json=conv_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation response: {data.get('ai_response', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Conversation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Conversation error: {e}")
        return False

def test_basic_translate():
    """Test the new basic translate endpoint"""
    print("Testing basic translate...")
    try:
        translate_data = {
            'text': 'Hello, world!',
            'sourceLang': 'en',
            'targetLang': 'fr'
        }
        
        response = requests.post(f'{API_BASE}/translate', json=translate_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic translation: {data.get('translation', 'N/A')}")
            return True
        else:
            print(f"❌ Basic translate failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Basic translate error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Learning Tools on Deployed Backend\n")
    print(f"🌐 Testing against: {API_BASE}\n")
    
    tests = [
        test_word_of_day,
        test_flashcards,
        test_quiz_generation,
        test_progress,
        test_conversation,
        test_basic_translate
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All learning tools tests passed on deployed backend!")
    else:
        print("⚠️ Some tests failed. Check the results above.")

if __name__ == '__main__':
    main() 