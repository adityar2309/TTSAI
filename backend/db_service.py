"""
Database service layer for SQLite operations
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from models import (
    get_db_session, User, WordOfDay, CommonPhrase, Flashcard, FlashcardReview,
    QuizScore, Quiz, PracticeSession, UserPreference, Analytics
)

class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self):
        self.db = None
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self.db:
            self.db = get_db_session()
        return self.db
    
    def close_session(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    # Word of Day operations
    def get_word_of_day(self, language: str) -> Optional[Dict]:
        """Get a random word of the day for the specified language"""
        try:
            db = self.get_session()
            words = db.query(WordOfDay).filter(WordOfDay.language == language).all()
            
            if not words:
                return None
            
            word = random.choice(words)
            return {
                'word': word.word,
                'translation': word.translation,
                'pronunciation': word.pronunciation,
                'part_of_speech': word.part_of_speech,
                'difficulty': word.difficulty,
                'example_sentence': word.example_sentence,
                'example_translation': word.example_translation,
                'etymology': word.etymology,
                'related_words': word.related_words,
                'cultural_note': word.cultural_note
            }
        except Exception as e:
            print(f"Error getting word of day: {e}")
            return None
    
    def add_word_of_day(self, language: str, word_data: Dict) -> bool:
        """Add a new word of the day"""
        try:
            db = self.get_session()
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
            return True
        except Exception as e:
            print(f"Error adding word of day: {e}")
            if db:
                db.rollback()
            return False
    
    # Common Phrases operations
    def get_common_phrases(self, language: str, category: str = None, difficulty: str = None) -> List[Dict]:
        """Get common phrases for a language"""
        try:
            db = self.get_session()
            query = db.query(CommonPhrase).filter(CommonPhrase.language == language)
            
            if category:
                query = query.filter(CommonPhrase.category == category)
            if difficulty:
                query = query.filter(CommonPhrase.difficulty == difficulty)
            
            phrases = query.all()
            return [{
                'phrase': phrase.phrase,
                'translation': phrase.translation,
                'category': phrase.category,
                'difficulty': phrase.difficulty,
                'pronunciation': phrase.pronunciation,
                'usage_context': phrase.usage_context
            } for phrase in phrases]
        except Exception as e:
            print(f"Error getting common phrases: {e}")
            return []
    
    def add_common_phrase(self, language: str, phrase_data: Dict) -> bool:
        """Add a new common phrase"""
        try:
            db = self.get_session()
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
            return True
        except Exception as e:
            print(f"Error adding common phrase: {e}")
            if db:
                db.rollback()
            return False
    
    # User operations
    def ensure_user_exists(self, user_id: str) -> User:
        """Ensure user exists in database"""
        db = self.get_session()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, last_active=datetime.now())
            db.add(user)
            db.commit()
        else:
            user.last_active = datetime.now()
            db.commit()
        return user
    
    # Flashcard operations
    def get_flashcards(self, user_id: str, language: str = None) -> List[Dict]:
        """Get user's flashcards"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
            if language:
                query = query.filter(Flashcard.target_lang == language)
            
            flashcards = query.order_by(desc(Flashcard.created_at)).all()
            
            return [{
                'id': flashcard.id,
                'translation': {
                    'originalText': flashcard.original_text,
                    'translatedText': flashcard.translated_text,
                    'sourceLang': flashcard.source_lang,
                    'targetLang': flashcard.target_lang
                },
                'difficulty': flashcard.difficulty,
                'category': flashcard.category,
                'notes': flashcard.notes,
                'review_count': flashcard.review_count,
                'mastery_level': flashcard.mastery_level,
                'success_rate': flashcard.success_rate,
                'next_review': flashcard.next_review.isoformat() if flashcard.next_review else None,
                'last_review': flashcard.last_review.isoformat() if flashcard.last_review else None,
                'created_at': flashcard.created_at.isoformat(),
                'updated_at': flashcard.updated_at.isoformat()
            } for flashcard in flashcards]
        except Exception as e:
            print(f"Error getting flashcards: {e}")
            return []
    
    def save_flashcard(self, user_id: str, flashcard_data: Dict) -> bool:
        """Save a flashcard"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            translation = flashcard_data.get('translation', {})
            flashcard_id = flashcard_data.get('id', str(uuid.uuid4()))
            
            # Check if flashcard exists
            existing = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
            
            if existing:
                # Update existing flashcard
                existing.original_text = translation.get('originalText', '')
                existing.translated_text = translation.get('translatedText', '')
                existing.source_lang = translation.get('sourceLang', 'en')
                existing.target_lang = translation.get('targetLang', 'es')
                existing.difficulty = flashcard_data.get('difficulty', 'beginner')
                existing.category = flashcard_data.get('category', 'general')
                existing.notes = flashcard_data.get('notes', '')
                existing.updated_at = datetime.now()
            else:
                # Create new flashcard
                flashcard = Flashcard(
                    id=flashcard_id,
                    user_id=user_id,
                    original_text=translation.get('originalText', ''),
                    translated_text=translation.get('translatedText', ''),
                    source_lang=translation.get('sourceLang', 'en'),
                    target_lang=translation.get('targetLang', 'es'),
                    difficulty=flashcard_data.get('difficulty', 'beginner'),
                    category=flashcard_data.get('category', 'general'),
                    notes=flashcard_data.get('notes', ''),
                    next_review=datetime.now() + timedelta(days=1)  # First review tomorrow
                )
                db.add(flashcard)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving flashcard: {e}")
            if db:
                db.rollback()
            return False
    
    def delete_flashcard(self, user_id: str, flashcard_id: str) -> bool:
        """Delete a flashcard"""
        try:
            db = self.get_session()
            flashcard = db.query(Flashcard).filter(
                and_(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
            ).first()
            
            if flashcard:
                # Delete associated reviews first
                db.query(FlashcardReview).filter(FlashcardReview.flashcard_id == flashcard_id).delete()
                db.delete(flashcard)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting flashcard: {e}")
            if db:
                db.rollback()
            return False
    
    def review_flashcard(self, user_id: str, flashcard_id: str, correct: bool, time_taken: int = 0) -> bool:
        """Record a flashcard review"""
        try:
            db = self.get_session()
            flashcard = db.query(Flashcard).filter(
                and_(Flashcard.id == flashcard_id, Flashcard.user_id == user_id)
            ).first()
            
            if not flashcard:
                return False
            
            # Record the review
            review = FlashcardReview(
                flashcard_id=flashcard_id,
                correct=correct,
                time_taken=time_taken,
                timestamp=datetime.now()
            )
            db.add(review)
            
            # Update flashcard stats
            flashcard.review_count += 1
            flashcard.last_review = datetime.now()
            
            # Calculate success rate
            total_reviews = db.query(FlashcardReview).filter(FlashcardReview.flashcard_id == flashcard_id).count()
            correct_reviews = db.query(FlashcardReview).filter(
                and_(FlashcardReview.flashcard_id == flashcard_id, FlashcardReview.correct == True)
            ).count()
            flashcard.success_rate = correct_reviews / total_reviews if total_reviews > 0 else 0
            
            # Update mastery level and next review (spaced repetition)
            if correct:
                flashcard.mastery_level = min(flashcard.mastery_level + 1, 5)
                days_to_add = [1, 3, 7, 14, 30][flashcard.mastery_level]
            else:
                flashcard.mastery_level = max(flashcard.mastery_level - 1, 0)
                days_to_add = 1
            
            flashcard.next_review = datetime.now() + timedelta(days=days_to_add)
            flashcard.updated_at = datetime.now()
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error reviewing flashcard: {e}")
            if db:
                db.rollback()
            return False
    
    # Quiz operations
    def save_quiz_score(self, user_id: str, quiz_data: Dict) -> bool:
        """Save quiz score"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            quiz_score = QuizScore(
                user_id=user_id,
                quiz_id=quiz_data.get('quiz_id', str(uuid.uuid4())),
                score=quiz_data.get('score', 0),
                total_questions=quiz_data.get('total_questions', 0),
                correct_answers=quiz_data.get('correct_answers', 0),
                language=quiz_data.get('language', 'en'),
                difficulty=quiz_data.get('difficulty', 'beginner'),
                answers=quiz_data.get('answers', {}),
                timestamp=datetime.now()
            )
            db.add(quiz_score)
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz score: {e}")
            if db:
                db.rollback()
            return False
    
    def get_quiz_scores(self, user_id: str, language: str = None) -> List[Dict]:
        """Get user's quiz scores"""
        try:
            db = self.get_session()
            query = db.query(QuizScore).filter(QuizScore.user_id == user_id)
            
            if language:
                query = query.filter(QuizScore.language == language)
            
            scores = query.order_by(desc(QuizScore.timestamp)).limit(50).all()
            
            return [{
                'quiz_id': score.quiz_id,
                'score': score.score,
                'total_questions': score.total_questions,
                'correct_answers': score.correct_answers,
                'language': score.language,
                'difficulty': score.difficulty,
                'answers': score.answers,
                'timestamp': score.timestamp.isoformat()
            } for score in scores]
        except Exception as e:
            print(f"Error getting quiz scores: {e}")
            return []
    
    # User preferences operations
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            
            if not prefs:
                # Create default preferences
                prefs = UserPreference(user_id=user_id)
                db.add(prefs)
                db.commit()
            
            return {
                'default_source_lang': prefs.default_source_lang,
                'default_target_lang': prefs.default_target_lang,
                'voice_gender': prefs.voice_gender,
                'speech_speed': prefs.speech_speed,
                'auto_play_translations': prefs.auto_play_translations,
                'save_history': prefs.save_history,
                'theme': prefs.theme,
                'notifications_enabled': prefs.notifications_enabled,
                'study_reminders': prefs.study_reminders,
                'daily_goal': prefs.daily_goal,
                'preferred_difficulty': prefs.preferred_difficulty,
                'updated_at': prefs.updated_at.isoformat()
            }
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return {}
    
    def save_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Save user preferences"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            
            if not prefs:
                prefs = UserPreference(user_id=user_id)
                db.add(prefs)
            
            # Update preferences
            prefs.default_source_lang = preferences.get('default_source_lang', prefs.default_source_lang)
            prefs.default_target_lang = preferences.get('default_target_lang', prefs.default_target_lang)
            prefs.voice_gender = preferences.get('voice_gender', prefs.voice_gender)
            prefs.speech_speed = preferences.get('speech_speed', prefs.speech_speed)
            prefs.auto_play_translations = preferences.get('auto_play_translations', prefs.auto_play_translations)
            prefs.save_history = preferences.get('save_history', prefs.save_history)
            prefs.theme = preferences.get('theme', prefs.theme)
            prefs.notifications_enabled = preferences.get('notifications_enabled', prefs.notifications_enabled)
            prefs.study_reminders = preferences.get('study_reminders', prefs.study_reminders)
            prefs.daily_goal = preferences.get('daily_goal', prefs.daily_goal)
            prefs.preferred_difficulty = preferences.get('preferred_difficulty', prefs.preferred_difficulty)
            prefs.updated_at = datetime.now()
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving user preferences: {e}")
            if db:
                db.rollback()
            return False
    
    # Analytics operations
    def track_event(self, event_data: Dict) -> bool:
        """Track an analytics event"""
        try:
            db = self.get_session()
            
            analytics = Analytics(
                id=str(uuid.uuid4()),
                user_id=event_data.get('user_id'),
                event_type=event_data.get('event_type', ''),
                event_data=event_data.get('event_data', {}),
                session_id=event_data.get('session_id'),
                user_agent=event_data.get('user_agent', ''),
                ip_address=event_data.get('ip_address', ''),
                timestamp=datetime.now()
            )
            db.add(analytics)
            db.commit()
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            if db:
                db.rollback()
            return False
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get comprehensive user progress"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            # Get flashcard stats
            flashcard_count = db.query(Flashcard).filter(Flashcard.user_id == user_id).count()
            avg_success_rate = db.query(func.avg(Flashcard.success_rate)).filter(Flashcard.user_id == user_id).scalar() or 0
            
            # Get quiz stats
            quiz_count = db.query(QuizScore).filter(QuizScore.user_id == user_id).count()
            avg_quiz_score = db.query(func.avg(QuizScore.score)).filter(QuizScore.user_id == user_id).scalar() or 0
            
            # Get recent activity
            recent_reviews = db.query(FlashcardReview).join(Flashcard).filter(
                Flashcard.user_id == user_id
            ).filter(FlashcardReview.timestamp >= datetime.now() - timedelta(days=7)).count()
            
            return {
                'flashcard_count': flashcard_count,
                'avg_success_rate': round(float(avg_success_rate), 2),
                'quiz_count': quiz_count,
                'avg_quiz_score': round(float(avg_quiz_score), 2),
                'recent_reviews': recent_reviews,
                'last_activity': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {}

# Global service instance
db_service = DatabaseService() 