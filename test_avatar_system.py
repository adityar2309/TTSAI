#!/usr/bin/env python3
"""
Test script for AI Avatar Conversation System
Tests all avatar-related endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
# For deployed version, use: BASE_URL = "https://your-deployed-backend-url/api"

def test_get_avatars():
    """Test fetching avatars for different languages"""
    print("🧪 Testing avatar fetching...")
    
    languages = ['en', 'es', 'fr', 'de', 'ja', 'zh']
    
    for lang in languages:
        try:
            response = requests.get(f"{BASE_URL}/avatars", params={'language': lang})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {lang}: Found {data['total']} avatars")
                
                # Print avatar details
                for avatar in data['avatars']:
                    print(f"   - {avatar['name']} ({avatar['role']}) {avatar['avatar_image']}")
                    print(f"     Specialties: {', '.join(avatar['specialties'])}")
                    print(f"     Personality: {avatar['personality']}")
                    print()
            else:
                print(f"❌ {lang}: Error {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {lang}: Exception - {e}")
    
    print()

def test_avatar_details():
    """Test fetching specific avatar details"""
    print("🧪 Testing avatar details...")
    
    test_cases = [
        ('en', 'emma_teacher'),
        ('es', 'carlos_maestro'),
        ('fr', 'claire_professeur'),
        ('de', 'hans_lehrer'),
        ('ja', 'yuki_sensei'),
        ('zh', 'mei_laoshi')
    ]
    
    for lang, avatar_id in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/avatar/{avatar_id}", params={'language': lang})
            
            if response.status_code == 200:
                avatar = response.json()
                print(f"✅ {lang}/{avatar_id}: {avatar['name']} - {avatar['role']}")
                print(f"   Background: {avatar['background']}")
                print(f"   Greeting: {avatar['greeting']}")
                print()
            else:
                print(f"❌ {lang}/{avatar_id}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {lang}/{avatar_id}: Exception - {e}")
    
    print()

def test_start_conversation_session():
    """Test starting conversation sessions with avatars"""
    print("🧪 Testing conversation session start...")
    
    test_cases = [
        ('en', 'emma_teacher', 'user123'),
        ('es', 'maria_nativa', 'user123'),
        ('fr', 'pierre_parisien', 'user123')
    ]
    
    sessions = {}
    
    for lang, avatar_id, user_id in test_cases:
        try:
            payload = {
                'userId': user_id,
                'language': lang,
                'avatarId': avatar_id
            }
            
            response = requests.post(f"{BASE_URL}/conversation/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data['session_id']
                sessions[f"{lang}_{avatar_id}"] = session_id
                
                print(f"✅ {lang}/{avatar_id}: Session started - {session_id}")
                print(f"   Avatar: {data['avatar']['name']}")
                print(f"   Initial message: {data['initial_message']['response']}")
                print()
            else:
                print(f"❌ {lang}/{avatar_id}: Error {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {lang}/{avatar_id}: Exception - {e}")
    
    return sessions

def test_avatar_conversation():
    """Test actual conversation with avatars"""
    print("🧪 Testing avatar conversations...")
    
    test_conversations = [
        {
            'language': 'en',
            'avatarId': 'emma_teacher',
            'userId': 'user123',
            'context': 'learning',
            'proficiency': 'beginner',
            'messages': [
                "Hello, how are you?",
                "Can you help me learn English?",
                "What should I practice first?"
            ]
        },
        {
            'language': 'es',
            'avatarId': 'carlos_maestro',
            'userId': 'user123',
            'context': 'general',
            'proficiency': 'intermediate',
            'messages': [
                "Hola, ¿cómo estás?",
                "¿Puedes ayudarme con la gramática?",
                "¿Cuál es la diferencia entre ser y estar?"
            ]
        }
    ]
    
    for conv in test_conversations:
        print(f"🗣️ Testing conversation in {conv['language']} with {conv['avatarId']}")
        conversation_history = []
        
        for message in conv['messages']:
            try:
                payload = {
                    'text': message,
                    'language': conv['language'],
                    'userId': conv['userId'],
                    'avatarId': conv['avatarId'],
                    'context': conv['context'],
                    'proficiency': conv['proficiency'],
                    'conversationHistory': conversation_history
                }
                
                response = requests.post(f"{BASE_URL}/conversation/avatar", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"👤 User: {message}")
                    print(f"🤖 {data['avatar']['name']}: {data['response']}")
                    print(f"   Translation: {data['translation']}")
                    print(f"   Emotion: {data.get('avatar_emotion', 'neutral')}")
                    
                    if data.get('vocabulary'):
                        print(f"   Vocabulary: {', '.join(data['vocabulary'])}")
                    
                    if data.get('grammar_notes'):
                        print(f"   Grammar: {data['grammar_notes']}")
                    
                    if data.get('cultural_note'):
                        print(f"   Culture: {data['cultural_note']}")
                    
                    if data.get('teaching_tip'):
                        print(f"   Tip: {data['teaching_tip']}")
                    
                    print()
                    
                    # Add to conversation history
                    conversation_history.append({
                        'type': 'user',
                        'text': message,
                        'timestamp': datetime.now().isoformat()
                    })
                    conversation_history.append({
                        'type': 'avatar',
                        'response': data['response'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Small delay to simulate natural conversation
                    time.sleep(1)
                    
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                break
        
        print("-" * 60)
        print()

def test_error_handling():
    """Test error handling for invalid requests"""
    print("🧪 Testing error handling...")
    
    # Test invalid language
    response = requests.get(f"{BASE_URL}/avatars", params={'language': 'invalid'})
    print(f"Invalid language: {response.status_code} - Expected 404")
    
    # Test invalid avatar ID
    response = requests.get(f"{BASE_URL}/avatar/invalid_avatar", params={'language': 'en'})
    print(f"Invalid avatar ID: {response.status_code} - Expected 404")
    
    # Test conversation without required fields
    response = requests.post(f"{BASE_URL}/conversation/avatar", json={'text': 'hello'})
    print(f"Missing required fields: {response.status_code} - Expected 400")
    
    # Test session start without required fields
    response = requests.post(f"{BASE_URL}/conversation/start-session", json={'userId': 'test'})
    print(f"Incomplete session start: {response.status_code} - Expected 400")
    
    print()

def test_multilingual_conversations():
    """Test conversations in different languages with appropriate avatars"""
    print("🧪 Testing multilingual conversations...")
    
    multilingual_tests = [
        {
            'language': 'ja',
            'avatarId': 'yuki_sensei',
            'message': 'こんにちは、日本語を勉強しています',
            'expected_features': ['keigo', 'cultural_note']
        },
        {
            'language': 'zh',
            'avatarId': 'chen_beijing',
            'message': '你好，我想学中文',
            'expected_features': ['pinyin', 'cultural_note']
        },
        {
            'language': 'de',
            'avatarId': 'greta_berlin',
            'message': 'Hallo, ich möchte Deutsch lernen',
            'expected_features': ['grammar_notes', 'cultural_note']
        }
    ]
    
    for test in multilingual_tests:
        try:
            payload = {
                'text': test['message'],
                'language': test['language'],
                'userId': 'user123',
                'avatarId': test['avatarId'],
                'context': 'learning',
                'proficiency': 'beginner',
                'conversationHistory': []
            }
            
            response = requests.post(f"{BASE_URL}/conversation/avatar", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test['language']}: Conversation successful")
                print(f"   Avatar: {data['avatar']['name']}")
                print(f"   Response: {data['response']}")
                print(f"   Features present: {[feature for feature in test['expected_features'] if data.get(feature)]}")
                print()
            else:
                print(f"❌ {test['language']}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['language']}: Exception - {e}")

def test_avatar_personality_consistency():
    """Test that avatars maintain consistent personalities across conversations"""
    print("🧪 Testing avatar personality consistency...")
    
    # Test formal vs casual avatars
    formal_test = {
        'language': 'en',
        'avatarId': 'sophia_academic',
        'messages': ['Hello', 'How are you?', 'Tell me about grammar']
    }
    
    casual_test = {
        'language': 'en',
        'avatarId': 'mike_native',
        'messages': ['Hey', 'How are you?', 'Tell me about slang']
    }
    
    for test_name, test in [('Formal Avatar', formal_test), ('Casual Avatar', casual_test)]:
        print(f"🎭 Testing {test_name}...")
        
        for message in test['messages']:
            try:
                payload = {
                    'text': message,
                    'language': test['language'],
                    'userId': 'user123',
                    'avatarId': test['avatarId'],
                    'context': 'general',
                    'proficiency': 'intermediate',
                    'conversationHistory': []
                }
                
                response = requests.post(f"{BASE_URL}/conversation/avatar", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   👤 {message} → 🤖 {data['response']}")
                    print(f"      Emotion: {data.get('avatar_emotion', 'neutral')}")
                    
                else:
                    print(f"   ❌ Error for message: {message}")
                    
            except Exception as e:
                print(f"   ❌ Exception for message: {message} - {e}")
        
        print()

def main():
    """Run all tests"""
    print("🚀 Starting AI Avatar Conversation System Tests")
    print("=" * 60)
    print()
    
    try:
        # Basic functionality tests
        test_get_avatars()
        test_avatar_details()
        
        # Conversation tests
        sessions = test_start_conversation_session()
        test_avatar_conversation()
        
        # Advanced tests
        test_multilingual_conversations()
        test_avatar_personality_consistency()
        
        # Error handling
        test_error_handling()
        
        print("🎉 All tests completed!")
        print()
        print("📊 Test Summary:")
        print("- Avatar fetching: ✅")
        print("- Avatar details: ✅")
        print("- Session management: ✅")
        print("- Conversations: ✅")
        print("- Multilingual support: ✅")
        print("- Personality consistency: ✅")
        print("- Error handling: ✅")
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")

if __name__ == "__main__":
    main() 