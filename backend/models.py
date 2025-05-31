from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class WordOfDay(Base):
    __tablename__ = 'words_of_day'
    
    id = Column(Integer, primary_key=True)
    language = Column(String(10), nullable=False, index=True)
    word = Column(String(200), nullable=False)
    translation = Column(Text)
    pronunciation = Column(String(500))
    part_of_speech = Column(String(50))
    difficulty = Column(String(20), default='beginner')
    example_sentence = Column(Text)
    example_translation = Column(Text)
    etymology = Column(Text)
    related_words = Column(JSON)  # Store as JSON array
    cultural_note = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class CommonPhrase(Base):
    __tablename__ = 'common_phrases'
    
    id = Column(Integer, primary_key=True)
    language = Column(String(10), nullable=False, index=True)
    phrase = Column(Text, nullable=False)
    translation = Column(Text, nullable=False)
    category = Column(String(50), default='general', index=True)
    difficulty = Column(String(20), default='beginner', index=True)
    pronunciation = Column(String(500))
    usage_context = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(50), primary_key=True)  # user_id from frontend
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_active = Column(DateTime)
    
    # Relationships
    flashcards = relationship("Flashcard", back_populates="user")
    quiz_scores = relationship("QuizScore", back_populates="user")
    practice_sessions = relationship("PracticeSession", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)

class Flashcard(Base):
    __tablename__ = 'flashcards'
    
    id = Column(String(50), primary_key=True)  # UUID
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    difficulty = Column(String(20), default='beginner')
    category = Column(String(50), default='general')
    notes = Column(Text)
    
    # Spaced repetition fields
    review_count = Column(Integer, default=0)
    mastery_level = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    next_review = Column(DateTime, default=datetime.now)
    last_review = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="flashcards")
    reviews = relationship("FlashcardReview", back_populates="flashcard")

class FlashcardReview(Base):
    __tablename__ = 'flashcard_reviews'
    
    id = Column(Integer, primary_key=True)
    flashcard_id = Column(String(50), ForeignKey('flashcards.id'), nullable=False)
    correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer)  # seconds
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationship
    flashcard = relationship("Flashcard", back_populates="reviews")

class Quiz(Base):
    __tablename__ = 'quizzes'
    
    id = Column(String(50), primary_key=True)  # UUID
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    language = Column(String(10), nullable=False)
    quiz_type = Column(String(30), default='mixed')
    difficulty = Column(String(20), default='beginner')
    questions = Column(JSON)  # Store questions as JSON
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    scores = relationship("QuizScore", back_populates="quiz")

class QuizScore(Base):
    __tablename__ = 'quiz_scores'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    quiz_id = Column(String(50), ForeignKey('quizzes.id'), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    language = Column(String(10), nullable=False)
    difficulty = Column(String(20), nullable=False)
    answers = Column(JSON)  # Store user answers as JSON
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="quiz_scores")
    quiz = relationship("Quiz", back_populates="scores")

class PracticeSession(Base):
    __tablename__ = 'practice_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    session_type = Column(String(30), nullable=False)  # conversation, flashcard, quiz
    language = Column(String(10), nullable=False)
    context = Column(String(50))
    proficiency = Column(String(20))
    duration = Column(Integer)  # seconds
    performance = Column(Float)
    data = Column(JSON)  # Store session-specific data
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationship
    user = relationship("User", back_populates="practice_sessions")

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False, unique=True)
    default_source_lang = Column(String(10), default='en')
    default_target_lang = Column(String(10), default='es')
    voice_gender = Column(String(20), default='NEUTRAL')
    speech_speed = Column(Float, default=1.0)
    auto_play_translations = Column(Boolean, default=True)
    save_history = Column(Boolean, default=True)
    theme = Column(String(20), default='light')
    notifications_enabled = Column(Boolean, default=True)
    study_reminders = Column(Boolean, default=True)
    daily_goal = Column(Integer, default=10)
    preferred_difficulty = Column(String(20), default='beginner')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    user = relationship("User", back_populates="preferences")

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(String(50), primary_key=True)  # UUID
    user_id = Column(String(50), ForeignKey('users.id'))
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON)
    session_id = Column(String(100))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.now, index=True)

# Create indexes for better performance
Index('idx_flashcards_user_lang', Flashcard.user_id, Flashcard.target_lang)
Index('idx_quiz_scores_user_lang', QuizScore.user_id, QuizScore.language)
Index('idx_practice_sessions_user', PracticeSession.user_id, PracticeSession.timestamp)
Index('idx_analytics_user_event', Analytics.user_id, Analytics.event_type)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ttsai.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session for non-generator usage"""
    return SessionLocal() 