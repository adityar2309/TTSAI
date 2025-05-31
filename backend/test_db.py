#!/usr/bin/env python3
"""
Test script to verify SQLite database functionality
"""

from db_service import db_service

def test_word_of_day():
    """Test word of day functionality"""
    print("Testing word of day...")
    
    # Try to get a word for English
    word = db_service.get_word_of_day('en')
    if word:
        print(f"✓ Word of day for 'en': {word['word']}")
        return True
    else:
        print("✗ No word found for 'en'")
        return False

def test_flashcards():
    """Test flashcard functionality"""
    print("\nTesting flashcards...")
    
    test_user_id = "test_user_123"
    
    # Test saving a flashcard
    flashcard_data = {
        'id': 'test_flashcard_1',
        'translation': {
            'originalText': 'Hello',
            'translatedText': 'Hola',
            'sourceLang': 'en',
            'targetLang': 'es'
        },
        'difficulty': 'beginner',
        'category': 'greetings',
        'notes': 'Test flashcard'
    }
    
    if db_service.save_flashcard(test_user_id, flashcard_data):
        print("✓ Flashcard saved successfully")
        
        # Test retrieving flashcards
        flashcards = db_service.get_flashcards(test_user_id)
        if flashcards:
            print(f"✓ Retrieved {len(flashcards)} flashcards")
            return True
        else:
            print("✗ No flashcards retrieved")
            return False
    else:
        print("✗ Failed to save flashcard")
        return False

def test_user_preferences():
    """Test user preferences functionality"""
    print("\nTesting user preferences...")
    
    test_user_id = "test_user_123"
    
    # Test saving preferences
    preferences = {
        'default_source_lang': 'en',
        'default_target_lang': 'fr',
        'theme': 'dark',
        'daily_goal': 20
    }
    
    if db_service.save_user_preferences(test_user_id, preferences):
        print("✓ Preferences saved successfully")
        
        # Test retrieving preferences
        retrieved_prefs = db_service.get_user_preferences(test_user_id)
        if retrieved_prefs and retrieved_prefs.get('default_target_lang') == 'fr':
            print("✓ Preferences retrieved successfully")
            return True
        else:
            print("✗ Failed to retrieve correct preferences")
            return False
    else:
        print("✗ Failed to save preferences")
        return False

def test_analytics():
    """Test analytics functionality"""
    print("\nTesting analytics...")
    
    event_data = {
        'user_id': 'test_user_123',
        'event_type': 'test_event',
        'event_data': {'test': 'data'},
        'session_id': 'test_session'
    }
    
    if db_service.track_event(event_data):
        print("✓ Analytics event tracked successfully")
        return True
    else:
        print("✗ Failed to track analytics event")
        return False

def main():
    """Run all tests"""
    print("Running SQLite database tests...\n")
    
    tests = [
        test_word_of_day,
        test_flashcards,
        test_user_preferences,
        test_analytics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
    
    print(f"\n--- Results ---")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Database is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the database setup.")
    
    # Close database connection
    db_service.close_session()

if __name__ == "__main__":
    main() 