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
    def get_flashcards(self, user_id: str, language: str = None, difficulty: str = None, category: str = None) -> List[Dict]:
        """Get user's flashcards with optional filtering"""
        try:
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
            
            # Apply filters
            if language:
                query = query.filter(Flashcard.target_lang == language)
            if difficulty and difficulty != 'all':
                query = query.filter(Flashcard.difficulty == difficulty)
            if category and category != 'all':
                query = query.filter(Flashcard.category == category)
            
            flashcards = query.order_by(desc(Flashcard.created_at)).all()
            
            return [{
                'id': flashcard.id,
                'original_text': flashcard.original_text,
                'translated_text': flashcard.translated_text,
                'source_lang': flashcard.source_lang,
                'target_lang': flashcard.target_lang,
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
    
    def get_user_progress_summary(self, user_id: str, time_range: str = 'all') -> Dict:
        """Get comprehensive user progress summary for Learning Hub dashboard"""
        try:
            import math
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            # Calculate time filter if needed
            time_filter = None
            if time_range == 'week':
                time_filter = datetime.now() - timedelta(days=7)
            elif time_range == 'month':
                time_filter = datetime.now() - timedelta(days=30)
            
            # Get user preferences for daily goal
            prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            daily_goal = prefs.daily_goal if prefs else 10
            
            # Calculate total XP from quiz scores
            quiz_query = db.query(func.sum(QuizScore.score)).filter(QuizScore.user_id == user_id)
            if time_filter:
                quiz_query = quiz_query.filter(QuizScore.timestamp >= time_filter)
            total_quiz_xp = quiz_query.scalar() or 0
            
            # TODO: Add XP from flashcard reviews and practice sessions
            # For now, add a basic calculation for flashcard mastery
            flashcard_xp_query = db.query(func.count(Flashcard.id)).filter(
                and_(Flashcard.user_id == user_id, Flashcard.mastery_level >= 3)
            )
            if time_filter:
                flashcard_xp_query = flashcard_xp_query.filter(Flashcard.updated_at >= time_filter)
            flashcard_xp = (flashcard_xp_query.scalar() or 0) * 10  # 10 XP per mastered word
            
            total_xp = int(total_quiz_xp + flashcard_xp)
            
            # Calculate level (simple formula: level = floor(log2(xp/1000 + 1)) + 1)
            level = max(1, int(math.log2(total_xp/1000 + 1)) + 1)
            
            # TODO: Calculate current streak from Analytics events
            # For now, use a placeholder calculation based on recent activity
            recent_activity_days = db.query(func.count(func.distinct(func.date(FlashcardReview.timestamp)))).join(
                Flashcard
            ).filter(
                and_(
                    Flashcard.user_id == user_id,
                    FlashcardReview.timestamp >= datetime.now() - timedelta(days=7)
                )
            ).scalar() or 0
            current_streak = min(recent_activity_days, 7)  # Max 7 days for now
            
            # Count words learned (mastered flashcards)
            words_learned = db.query(func.count(Flashcard.id)).filter(
                and_(Flashcard.user_id == user_id, Flashcard.mastery_level >= 3)
            ).scalar() or 0
            
            # Get flashcard stats
            total_flashcards = db.query(func.count(Flashcard.id)).filter(Flashcard.user_id == user_id).scalar() or 0
            due_for_review = db.query(func.count(Flashcard.id)).filter(
                and_(
                    Flashcard.user_id == user_id,
                    Flashcard.next_review <= datetime.now()
                )
            ).scalar() or 0
            mastered_flashcards = words_learned
            avg_success_rate = db.query(func.avg(Flashcard.success_rate)).filter(
                Flashcard.user_id == user_id
            ).scalar() or 0.0
            
            # Get quiz stats
            quizzes_completed = db.query(func.count(QuizScore.id)).filter(QuizScore.user_id == user_id).scalar() or 0
            avg_quiz_score = db.query(func.avg(QuizScore.score)).filter(QuizScore.user_id == user_id).scalar() or 0.0
            
            # Get conversation stats
            conversation_sessions = db.query(func.count(PracticeSession.id)).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            ).scalar() or 0
            
            avg_conversation_duration = db.query(func.avg(PracticeSession.duration)).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            ).scalar() or 0
            
            # Get last conversation topic
            last_conversation = db.query(PracticeSession).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            ).order_by(desc(PracticeSession.timestamp)).first()
            
            last_topic = None
            if last_conversation and last_conversation.data:
                last_topic = last_conversation.data.get('topic', 'General Conversation')
            
            return {
                'total_xp': total_xp,
                'current_streak': current_streak,
                'words_learned': words_learned,
                'level': level,
                'quizzes_completed': quizzes_completed,
                'flashcard_stats': {
                    'total': total_flashcards,
                    'due_for_review': due_for_review,
                    'mastered': mastered_flashcards,
                    'avg_success_rate': float(avg_success_rate)
                },
                'quiz_stats': {
                    'completed': quizzes_completed,
                    'avg_score': float(avg_quiz_score)
                },
                'conversation_stats': {
                    'total': conversation_sessions,
                    'avg_duration': float(avg_conversation_duration) if avg_conversation_duration else 0,
                    'last_topic': last_topic
                },
                'daily_goal': daily_goal
            }
            
        except Exception as e:
            print(f"Error getting user progress summary: {e}")
            return {}
    
    def get_detailed_word(self, language: str, difficulty: str = None, category: str = None, search_term: str = None) -> Optional[Dict]:
        """Fetch a single word from WordOfDay based on criteria"""
        try:
            db = self.get_session()
            
            # Build query
            query = db.query(WordOfDay).filter(WordOfDay.language == language)
            
            # Apply filters
            if difficulty and difficulty != 'all':
                query = query.filter(WordOfDay.difficulty == difficulty)
            
            # Note: Category filtering would require adding a category field to WordOfDay model
            # For now, we'll skip category filtering since it's not in the current model
            
            # Apply search if provided
            if search_term and search_term.strip():
                search_pattern = f"%{search_term.strip()}%"
                query = query.filter(
                    or_(
                        WordOfDay.word.ilike(search_pattern),
                        WordOfDay.translation.ilike(search_pattern),
                        WordOfDay.example_sentence.ilike(search_pattern)
                    )
                )
                
                # Get first match for search
                word = query.first()
            else:
                # Get random word
                words = query.all()
                if words:
                    word = random.choice(words)
                else:
                    word = None
            
            if not word:
                return None
            
            # Format response including romanization support
            word_data = {
                'word': word.word,
                'translation': word.translation,
                'pronunciation': word.pronunciation,
                'part_of_speech': word.part_of_speech,
                'difficulty': word.difficulty,
                'example_sentence': word.example_sentence,
                'example_translation': word.example_translation,
                'etymology': word.etymology,
                'related_words': word.related_words or [],
                'cultural_note': word.cultural_note
            }
            
            # Add romanization data if available
            # Note: The current WordOfDay model doesn't have romanization fields
            # This is a placeholder for future enhancement
            # TODO: Add romanization and romanization_system fields to WordOfDay model
            word_data['romanization'] = None
            word_data['romanization_system'] = None
            
            return word_data
            
        except Exception as e:
            print(f"Error getting detailed word: {e}")
            return None
    
    def get_comprehensive_progress(self, user_id: str, time_range: str = 'all', language: str = None) -> Dict:
        """Get comprehensive progress data for ProgressTracker component with enhanced calculations"""
        try:
            import math
            from collections import defaultdict
            self.ensure_user_exists(user_id)
            db = self.get_session()
            
            # Calculate time filter based on time_range
            time_filter = None
            if time_range == 'week':
                time_filter = datetime.now() - timedelta(days=7)
            elif time_range == 'month':
                time_filter = datetime.now() - timedelta(days=30)
            
            # Get user preferences
            prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            daily_goal = prefs.daily_goal if prefs else 10
            
            # === Enhanced XP Calculation ===
            
            # 1. XP from Quiz Scores
            quiz_xp_query = db.query(func.sum(QuizScore.score)).filter(QuizScore.user_id == user_id)
            if time_filter:
                quiz_xp_query = quiz_xp_query.filter(QuizScore.timestamp >= time_filter)
            quiz_xp = quiz_xp_query.scalar() or 0
            
            # 2. XP from Flashcard Reviews (more sophisticated calculation)
            flashcard_reviews_query = db.query(FlashcardReview).join(Flashcard).filter(
                Flashcard.user_id == user_id
            )
            if time_filter:
                flashcard_reviews_query = flashcard_reviews_query.filter(FlashcardReview.timestamp >= time_filter)
            
            flashcard_reviews = flashcard_reviews_query.all()
            flashcard_xp = 0
            for review in flashcard_reviews:
                # Base XP for any review
                base_xp = 2 if review.correct else 1
                # Bonus XP for mastery progression (check if this review increased mastery level)
                flashcard = review.flashcard
                if review.correct and flashcard.mastery_level >= 1:
                    # Additional XP based on current mastery level
                    mastery_bonus = flashcard.mastery_level * 2
                    base_xp += mastery_bonus
                flashcard_xp += base_xp
            
            # 3. XP from Practice Sessions (conversations)
            practice_xp_query = db.query(func.count(PracticeSession.id)).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            )
            if time_filter:
                practice_xp_query = practice_xp_query.filter(PracticeSession.timestamp >= time_filter)
            
            practice_sessions = practice_xp_query.scalar() or 0
            practice_xp = practice_sessions * 15  # 15 XP per conversation session
            
            # 4. Bonus XP for streaks
            streak_bonus = 0
            current_streak = self._calculate_streak(user_id, time_filter)
            if current_streak >= 7:
                streak_bonus = (current_streak // 7) * 50  # 50 XP per week of streak
            
            total_xp = int(quiz_xp + flashcard_xp + practice_xp + streak_bonus)
            
            # === Level Calculation ===
            level = max(1, int(math.log2(total_xp/1000 + 1)) + 1)
            
            # === Enhanced Streak Calculation ===
            current_streak = self._calculate_streak(user_id, None)  # Calculate full streak, not filtered
            
            # === Words Learned (Enhanced) ===
            words_learned_query = db.query(func.count(Flashcard.id)).filter(
                and_(Flashcard.user_id == user_id, Flashcard.mastery_level >= 3)
            )
            if language:
                words_learned_query = words_learned_query.filter(Flashcard.target_lang == language)
            words_learned = words_learned_query.scalar() or 0
            
            # === Flashcard Stats (Enhanced) ===
            flashcard_query = db.query(Flashcard).filter(Flashcard.user_id == user_id)
            if language:
                flashcard_query = flashcard_query.filter(Flashcard.target_lang == language)
            if time_filter:
                flashcard_query = flashcard_query.filter(Flashcard.created_at >= time_filter)
            
            all_flashcards = flashcard_query.all()
            total_flashcards = len(all_flashcards)
            
            due_for_review = len([f for f in all_flashcards if f.next_review and f.next_review <= datetime.now()])
            mastered_flashcards = len([f for f in all_flashcards if f.mastery_level >= 5])
            
            avg_success_rate = 0.0
            if all_flashcards:
                total_rate = sum(f.success_rate for f in all_flashcards if f.success_rate)
                avg_success_rate = total_rate / len([f for f in all_flashcards if f.success_rate])
            
            # === Quiz Stats (Enhanced) ===
            quiz_query = db.query(QuizScore).filter(QuizScore.user_id == user_id)
            if language:
                quiz_query = quiz_query.filter(QuizScore.language == language)
            if time_filter:
                quiz_query = quiz_query.filter(QuizScore.timestamp >= time_filter)
            
            quiz_scores = quiz_query.all()
            quizzes_completed = len(quiz_scores)
            avg_quiz_score = 0.0
            if quiz_scores:
                avg_quiz_score = sum(q.score for q in quiz_scores) / len(quiz_scores)
            
            # === Conversation Stats (Enhanced) ===
            conversation_query = db.query(PracticeSession).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            )
            if language:
                conversation_query = conversation_query.filter(PracticeSession.language == language)
            if time_filter:
                conversation_query = conversation_query.filter(PracticeSession.timestamp >= time_filter)
            
            conversations = conversation_query.all()
            conversation_count = len(conversations)
            
            avg_conversation_duration = 0
            if conversations:
                total_duration = sum(c.duration for c in conversations if c.duration)
                avg_conversation_duration = total_duration / len(conversations) if total_duration else 0
            
            # Get last conversation topic
            last_conversation = db.query(PracticeSession).filter(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.session_type == 'avatar_conversation'
                )
            ).order_by(desc(PracticeSession.timestamp)).first()
            
            last_topic = None
            if last_conversation and last_conversation.data:
                last_topic = last_conversation.data.get('topic', 'General Conversation')
            elif last_conversation:
                last_topic = 'General Conversation'
            
            # === Activity Data for Graphs (Placeholder) ===
            activity_data = self._get_activity_data(user_id, time_filter)
            
            return {
                'total_xp': total_xp,
                'current_streak': current_streak,
                'words_learned': words_learned,
                'level': level,
                'flashcard_stats': {
                    'total': total_flashcards,
                    'due_for_review': due_for_review,
                    'mastered': mastered_flashcards,
                    'avg_success_rate': avg_success_rate
                },
                'quiz_stats': {
                    'completed': quizzes_completed,
                    'avg_score': avg_quiz_score
                },
                'conversation_stats': {
                    'total': conversation_count,
                    'avg_duration': avg_conversation_duration,
                    'last_topic': last_topic
                },
                'daily_goal': daily_goal,
                'activity_data': activity_data,
                'xp_breakdown': {
                    'quiz_xp': int(quiz_xp),
                    'flashcard_xp': int(flashcard_xp),
                    'practice_xp': int(practice_xp),
                    'streak_bonus': int(streak_bonus)
                }
            }
            
        except Exception as e:
            print(f"Error getting comprehensive progress: {e}")
            return {}
    
    def _calculate_streak(self, user_id: str, time_filter: datetime = None) -> int:
        """Calculate current streak based on Analytics events and recent activity"""
        try:
            db = self.get_session()
            
            # Get analytics events for streak calculation
            analytics_query = db.query(Analytics).filter(
                and_(
                    Analytics.user_id == user_id,
                    Analytics.event_type.in_([
                        'translation_completed',
                        'flashcard_review',
                        'avatar_conversation',
                        'quiz_completed'
                    ])
                )
            ).order_by(desc(Analytics.timestamp))
            
            if time_filter:
                analytics_query = analytics_query.filter(Analytics.timestamp >= time_filter)
            
            analytics_events = analytics_query.all()
            
            if not analytics_events:
                # Fallback: calculate based on recent flashcard reviews and quiz activity
                return self._calculate_streak_fallback(user_id)
            
            # Group events by date
            daily_activity = defaultdict(bool)
            for event in analytics_events:
                date_key = event.timestamp.date()
                daily_activity[date_key] = True
            
            # Calculate consecutive days from today backwards
            current_date = datetime.now().date()
            streak = 0
            
            while current_date in daily_activity:
                streak += 1
                current_date -= timedelta(days=1)
                if streak > 365:  # Safety limit
                    break
            
            return streak
            
        except Exception as e:
            print(f"Error calculating streak: {e}")
            return self._calculate_streak_fallback(user_id)
    
    def _calculate_streak_fallback(self, user_id: str) -> int:
        """Fallback streak calculation based on flashcard reviews and quiz activity"""
        try:
            db = self.get_session()
            
            # Get recent activity dates from flashcard reviews
            recent_reviews = db.query(func.date(FlashcardReview.timestamp)).join(Flashcard).filter(
                Flashcard.user_id == user_id
            ).filter(
                FlashcardReview.timestamp >= datetime.now() - timedelta(days=30)
            ).distinct().all()
            
            # Get recent quiz dates
            recent_quizzes = db.query(func.date(QuizScore.timestamp)).filter(
                QuizScore.user_id == user_id
            ).filter(
                QuizScore.timestamp >= datetime.now() - timedelta(days=30)
            ).distinct().all()
            
            # Combine all activity dates
            activity_dates = set()
            for date_tuple in recent_reviews:
                activity_dates.add(date_tuple[0])
            for date_tuple in recent_quizzes:
                activity_dates.add(date_tuple[0])
            
            if not activity_dates:
                return 0
            
            # Calculate streak from today backwards
            current_date = datetime.now().date()
            streak = 0
            
            while current_date in activity_dates:
                streak += 1
                current_date -= timedelta(days=1)
                if streak > 30:  # Reasonable limit for fallback
                    break
            
            return streak
            
        except Exception as e:
            print(f"Error in streak fallback calculation: {e}")
            return 0
    
    def _get_activity_data(self, user_id: str, time_filter: datetime = None) -> List[Dict]:
        """Get activity data for graph visualization (placeholder implementation)"""
        try:
            db = self.get_session()
            
            # Get daily activity counts for the past period
            days_back = 30 if time_filter else 7
            if time_filter is None:
                time_filter = datetime.now() - timedelta(days=days_back)
            
            activity_data = []
            current_date = time_filter.date()
            end_date = datetime.now().date()
            
            while current_date <= end_date:
                # Count activities for this date
                date_start = datetime.combine(current_date, datetime.min.time())
                date_end = date_start + timedelta(days=1)
                
                # Count flashcard reviews
                review_count = db.query(FlashcardReview).join(Flashcard).filter(
                    and_(
                        Flashcard.user_id == user_id,
                        FlashcardReview.timestamp >= date_start,
                        FlashcardReview.timestamp < date_end
                    )
                ).count()
                
                # Count quizzes
                quiz_count = db.query(QuizScore).filter(
                    and_(
                        QuizScore.user_id == user_id,
                        QuizScore.timestamp >= date_start,
                        QuizScore.timestamp < date_end
                    )
                ).count()
                
                activity_data.append({
                    'date': current_date.isoformat(),
                    'reviews': review_count,
                    'quizzes': quiz_count,
                    'total_activities': review_count + quiz_count
                })
                
                current_date += timedelta(days=1)
            
            return activity_data
            
        except Exception as e:
            print(f"Error getting activity data: {e}")
            return []

# Global service instance
db_service = DatabaseService() 