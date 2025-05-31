#!/usr/bin/env python3
"""
Migration script to convert JSON data to SQLite database
"""

import json
import os
import uuid
from datetime import datetime
from models import (
    create_tables, get_db_session, 
    WordOfDay, CommonPhrase, User, Flashcard, FlashcardReview,
    QuizScore, PracticeSession, UserPreference, Analytics
)

def load_json_safe(file_path):
    """Safely load JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return {}

def migrate_word_of_day():
    """Migrate word of day data"""
    print("Migrating word of day data...")
    data = load_json_safe('data/word_of_day.json')
    
    db = get_db_session()
    try:
        words_data = data.get('words', {})
        for language, words in words_data.items():
            for word_data in words:
                word = WordOfDay(
                    language=language,
                    word=word_data.get('word', ''),
                    translation=word_data.get('translation', ''),
                    pronunciation=word_data.get('pronunciation', ''),
                    part_of_speech=word_data.get('part_of_speech', ''),
                    difficulty=word_data.get('difficulty', 'beginner'),
                    example_sentence=word_data.get('example_sentence', ''),
                    example_translation=word_data.get('example_translation', ''),
                    etymology=word_data.get('etymology', ''),
                    related_words=word_data.get('related_words', []),
                    cultural_note=word_data.get('cultural_note', '')
                )
                db.add(word)
        
        db.commit()
        print(f"Migrated {db.query(WordOfDay).count()} words")
    
    except Exception as e:
        print(f"Error migrating word of day: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_common_phrases():
    """Migrate common phrases data"""
    print("Migrating common phrases data...")
    data = load_json_safe('data/common_phrases.json')
    
    db = get_db_session()
    try:
        phrases_data = data.get('phrases', {})
        for language, phrases in phrases_data.items():
            for phrase_data in phrases:
                phrase = CommonPhrase(
                    language=language,
                    phrase=phrase_data.get('phrase', ''),
                    translation=phrase_data.get('translation', ''),
                    category=phrase_data.get('category', 'general'),
                    difficulty=phrase_data.get('difficulty', 'beginner'),
                    pronunciation=phrase_data.get('pronunciation', ''),
                    usage_context=phrase_data.get('usage_context', '')
                )
                db.add(phrase)
        
        db.commit()
        print(f"Migrated {db.query(CommonPhrase).count()} phrases")
    
    except Exception as e:
        print(f"Error migrating common phrases: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_user_progress():
    """Migrate user progress data"""
    print("Migrating user progress data...")
    data = load_json_safe('data/user_progress.json')
    
    db = get_db_session()
    try:
        users_data = data.get('users', {})
        
        for user_id, user_data in users_data.items():
            # Create user if not exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id)
                db.add(user)
                db.flush()  # Get the user ID
            
            # Migrate flashcards
            flashcards_data = user_data.get('flashcards', [])
            for flashcard_data in flashcards_data:
                translation = flashcard_data.get('translation', {})
                
                flashcard = Flashcard(
                    id=flashcard_data.get('id', str(uuid.uuid4())),
                    user_id=user_id,
                    original_text=translation.get('originalText', ''),
                    translated_text=translation.get('translatedText', ''),
                    source_lang=translation.get('sourceLang', 'en'),
                    target_lang=translation.get('targetLang', 'es'),
                    difficulty=flashcard_data.get('difficulty', 'beginner'),
                    category=flashcard_data.get('category', 'general'),
                    notes=flashcard_data.get('notes', ''),
                    review_count=flashcard_data.get('review_count', 0),
                    mastery_level=flashcard_data.get('mastery_level', 0),
                    success_rate=flashcard_data.get('success_rate', 0.0),
                    next_review=datetime.fromisoformat(flashcard_data.get('next_review', datetime.now().isoformat())),
                    last_review=datetime.fromisoformat(flashcard_data['last_review']) if flashcard_data.get('last_review') else None,
                    created_at=datetime.fromisoformat(flashcard_data.get('created_at', datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(flashcard_data.get('updated_at', datetime.now().isoformat()))
                )
                db.add(flashcard)
                
                # Migrate flashcard reviews
                review_history = flashcard_data.get('review_history', [])
                for review_data in review_history:
                    review = FlashcardReview(
                        flashcard_id=flashcard.id,
                        correct=review_data.get('correct', False),
                        time_taken=review_data.get('time_taken', 0),
                        timestamp=datetime.fromisoformat(review_data.get('timestamp', datetime.now().isoformat()))
                    )
                    db.add(review)
            
            # Migrate quiz scores
            quiz_scores_data = user_data.get('quiz_scores', [])
            for score_data in quiz_scores_data:
                quiz_score = QuizScore(
                    user_id=user_id,
                    quiz_id=score_data.get('quiz_id', str(uuid.uuid4())),
                    score=score_data.get('score', 0),
                    total_questions=score_data.get('total_questions', 0),
                    correct_answers=score_data.get('correct_answers', 0),
                    language=score_data.get('language', 'en'),
                    difficulty=score_data.get('difficulty', 'beginner'),
                    answers=score_data.get('answers', {}),
                    timestamp=datetime.fromisoformat(score_data.get('timestamp', datetime.now().isoformat()))
                )
                db.add(quiz_score)
            
            # Migrate practice sessions
            practice_sessions_data = user_data.get('practice_sessions', [])
            for session_data in practice_sessions_data:
                practice_session = PracticeSession(
                    user_id=user_id,
                    session_type=session_data.get('type', 'conversation'),
                    language=session_data.get('language', 'en'),
                    context=session_data.get('context', ''),
                    proficiency=session_data.get('proficiency', 'beginner'),
                    duration=session_data.get('duration', 0),
                    performance=session_data.get('performance', 0.0),
                    data=session_data,  # Store entire session data as JSON
                    timestamp=datetime.fromisoformat(session_data.get('timestamp', datetime.now().isoformat()))
                )
                db.add(practice_session)
        
        db.commit()
        print(f"Migrated {db.query(User).count()} users with their data")
    
    except Exception as e:
        print(f"Error migrating user progress: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_user_preferences():
    """Migrate user preferences data"""
    print("Migrating user preferences data...")
    data = load_json_safe('data/user_preferences.json')
    
    db = get_db_session()
    try:
        users_data = data.get('users', {})
        
        for user_id, prefs_data in users_data.items():
            # Ensure user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id)
                db.add(user)
                db.flush()
            
            # Create preferences
            preferences = UserPreference(
                user_id=user_id,
                default_source_lang=prefs_data.get('default_source_lang', 'en'),
                default_target_lang=prefs_data.get('default_target_lang', 'es'),
                voice_gender=prefs_data.get('voice_gender', 'NEUTRAL'),
                speech_speed=prefs_data.get('speech_speed', 1.0),
                auto_play_translations=prefs_data.get('auto_play_translations', True),
                save_history=prefs_data.get('save_history', True),
                theme=prefs_data.get('theme', 'light'),
                notifications_enabled=prefs_data.get('notifications_enabled', True),
                study_reminders=prefs_data.get('study_reminders', True),
                daily_goal=prefs_data.get('daily_goal', 10),
                preferred_difficulty=prefs_data.get('preferred_difficulty', 'beginner'),
                updated_at=datetime.fromisoformat(prefs_data.get('updated_at', datetime.now().isoformat()))
            )
            db.add(preferences)
        
        db.commit()
        print(f"Migrated {db.query(UserPreference).count()} user preferences")
    
    except Exception as e:
        print(f"Error migrating user preferences: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_analytics():
    """Migrate analytics data"""
    print("Migrating analytics data...")
    data = load_json_safe('data/learning_analytics.json')
    
    db = get_db_session()
    try:
        events_data = data.get('events', [])
        
        for event_data in events_data:
            analytics = Analytics(
                id=event_data.get('id', str(uuid.uuid4())),
                user_id=event_data.get('user_id'),
                event_type=event_data.get('event_type', ''),
                event_data=event_data.get('event_data', {}),
                session_id=event_data.get('session_id'),
                user_agent=event_data.get('user_agent', ''),
                ip_address=event_data.get('ip_address', ''),
                timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat()))
            )
            db.add(analytics)
        
        db.commit()
        print(f"Migrated {db.query(Analytics).count()} analytics events")
    
    except Exception as e:
        print(f"Error migrating analytics: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main migration function"""
    print("Starting migration from JSON to SQLite...")
    
    # Create tables
    print("Creating database tables...")
    create_tables()
    
    # Run migrations
    migrate_word_of_day()
    migrate_common_phrases()
    migrate_user_progress()
    migrate_user_preferences()
    migrate_analytics()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    main() 