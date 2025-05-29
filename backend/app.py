from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.cloud.texttospeech as tts
import google.cloud.speech as speech
import google.generativeai as genai
from google.cloud.speech_v1 import SpeechClient
from google.cloud.texttospeech_v1 import TextToSpeechClient
import logging
import json
from datetime import datetime, timedelta
import random
import base64
import time
from functools import wraps
import threading
from collections import defaultdict, deque
import hashlib
import uuid
from google.auth import default
from fuzzywuzzy import fuzz

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://ttsai.netlify.app",
            "https://*.netlify.app",
            "https://6837027b175dc48ca24afe5c--ttsai.netlify.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60     # window in seconds
rate_limit_storage = defaultdict(lambda: deque())

# Cache configuration
CACHE_DURATION = 300  # 5 minutes
translation_cache = {}
tts_cache = {}

# Initialize Google Cloud clients with error handling
try:
    # Initialize clients - explicitly use default credentials
    logger.info("Initializing Google Cloud Speech client...")
    credentials, project = default()
    speech_client = SpeechClient(credentials=credentials)
    logger.info("Google Cloud Speech client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud Speech client: {e}")
    speech_client = None

try:
    logger.info("Initializing Google Cloud TTS client...")
    credentials, project = default()
    tts_client = TextToSpeechClient(credentials=credentials)
    logger.info("Google Cloud TTS client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud TTS client: {e}")
    tts_client = None

# Configure Gemini with enhanced error handling
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY must be set in environment variables")

try:
    logger.info(f"Configuring Gemini with API key: {api_key[:8]}...{api_key[-4:]}")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Test Gemini connection
    test_response = model.generate_content("Test connection")
    logger.info("Gemini connection test successful")
except Exception as e:
    logger.error(f"Failed to configure Gemini: {e}")
    model = None

# Enhanced rate limiting decorator
def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        current_time = time.time()
        
        # Clean old requests
        user_requests = rate_limit_storage[client_ip]
        while user_requests and user_requests[0] < current_time - RATE_LIMIT_WINDOW:
            user_requests.popleft()
        
        # Check rate limit
        if len(user_requests) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': RATE_LIMIT_WINDOW
            }), 429
        
        # Add current request
        user_requests.append(current_time)
        return func(*args, **kwargs)
    
    return wrapper

# Enhanced caching utility
def get_cache_key(data):
    """Generate a cache key from request data"""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def get_cached_result(cache_dict, key):
    """Get cached result if not expired"""
    if key in cache_dict:
        result, timestamp = cache_dict[key]
        if time.time() - timestamp < CACHE_DURATION:
            return result
        else:
            del cache_dict[key]
    return None

def cache_result(cache_dict, key, result):
    """Cache a result with timestamp"""
    cache_dict[key] = (result, time.time())

# Enhanced translation prompt with more detailed instructions
def get_advanced_translation_prompt(text, source_lang, target_lang, formality="neutral", dialect=None, context=None):
    context_instruction = f"\nContext: {context}" if context else ""
    dialect_instruction = f"\n- Target dialect: {dialect}" if dialect else ""
    
    # Check if target language uses non-Latin script for romanization
    non_latin_languages = ['ar', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'hi', 'ru', 'th', 'he', 'ur', 'fa', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'pa', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am', 'ti', 'dv']
    needs_romanization = any(lang in target_lang.lower() for lang in non_latin_languages)
    
    romanization_instruction = ""
    if needs_romanization:
        romanization_instruction = """
   - Romanization: Latin script representation for easy reading
   - Romanization system: Standard system used (e.g., Pinyin for Chinese, Hepburn for Japanese, etc.)"""
    
    return f"""Provide a comprehensive translation analysis with the following components:

1. Main Translation:
   - Translate from {source_lang} to {target_lang}
   - Formality level: {formality}{dialect_instruction}
   - Preserve original meaning while adapting to cultural context{context_instruction}

2. Alternative Translations (provide exactly 3):
   - Alternative 1: More literal translation with confidence %
   - Alternative 2: More colloquial/natural translation with confidence %
   - Alternative 3: Formal/professional version with confidence %
   - Include brief explanations for each alternative

3. Pronunciation Guide:
   - IPA notation for the main translation
   - Syllable breakdown with hyphens
   - Stress markers and tone information (if applicable)
   - Phonetic spelling for easy pronunciation{romanization_instruction}

4. Grammar Analysis:
   - Part of speech tags for key words
   - Sentence structure breakdown
   - Grammar rules and patterns used
   - Grammatical differences from source language

5. Contextual Usage:
   - 3 different contexts where this phrase is commonly used
   - 3 example sentences in real-world scenarios
   - Cultural notes and regional variations
   - Appropriate situations for usage

6. Additional Information:
   - Difficulty level (beginner/intermediate/advanced)
   - Common mistakes to avoid
   - Related phrases or expressions
   - Etymology or word origin (if interesting)

Text to analyze: "{text}"

Return ONLY a valid JSON response with these exact keys:
{{
    "main_translation": "",
    "alternatives": [
        {{"text": "", "confidence": 0, "explanation": "", "type": "literal"}},
        {{"text": "", "confidence": 0, "explanation": "", "type": "colloquial"}},
        {{"text": "", "confidence": 0, "explanation": "", "type": "formal"}}
    ],
    "pronunciation": {{
        "ipa": "",
        "syllables": "",
        "stress": "",
        "phonetic": "",
        "romanization": "",
        "romanization_system": ""
    }},
    "grammar": {{
        "parts_of_speech": [],
        "structure": "",
        "rules": [],
        "differences": ""
    }},
    "context": {{
        "usage_contexts": [],
        "examples": [],
        "cultural_notes": "",
        "appropriate_situations": []
    }},
    "additional": {{
        "difficulty": "",
        "common_mistakes": [],
        "related_phrases": [],
        "etymology": ""
    }}
}}"""

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'gemini': model is not None,
            'speech_client': speech_client is not None,
            'tts_client': tts_client is not None
        }
    })

@app.route('/api/advanced-translate', methods=['POST'])
@rate_limit
def advanced_translate():
    """Enhanced translation endpoint with caching and better error handling"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Validate required fields
        required_fields = ['text', 'sourceLang', 'targetLang']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        text = data.get('text').strip()
        source_lang = data.get('sourceLang')
        target_lang = data.get('targetLang')
        formality = data.get('formality', 'neutral')
        dialect = data.get('dialect')
        context = data.get('context')
        
        # Input validation
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Check cache first
        cache_key = get_cache_key({
            'text': text, 'source': source_lang, 'target': target_lang,
            'formality': formality, 'dialect': dialect, 'context': context
        })
        
        cached_result = get_cached_result(translation_cache, cache_key)
        if cached_result:
            logger.info(f"Returning cached translation for: {text[:50]}...")
            return jsonify(cached_result)
        
        if not model:
            return jsonify({'error': 'Translation service temporarily unavailable'}), 503
        
        # Generate prompt and get translation
        prompt = get_advanced_translation_prompt(
            text, source_lang, target_lang, formality, dialect, context
        )
        
        logger.info(f"Translating: '{text}' from {source_lang} to {target_lang}")
        
        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
                
            # Parse JSON response
            translation_data = json.loads(response.text)
            
            # Add metadata
            translation_data['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'source_lang': source_lang,
                'target_lang': target_lang,
                'formality': formality,
                'dialect': dialect,
                'context': context,
                'cached': False
            }
            
            # Cache the result
            cache_result(translation_cache, cache_key, translation_data)
            
            logger.info(f"Translation completed successfully for: {text[:50]}...")
            return jsonify(translation_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. Response: {response.text[:200]}")
            return jsonify({
                'error': 'Translation service returned invalid format',
                'details': 'Please try again'
            }), 500
            
    except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return jsonify({
                'error': 'Translation service error',
                'details': 'Please try again later'
            }), 503
            
    except Exception as e:
        logger.error(f"Advanced translation error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': 'An unexpected error occurred'
        }), 500

# Enhanced data file paths with better structure
DATA_DIR = 'data'
PHRASES_FILE = os.path.join(DATA_DIR, 'common_phrases.json')
WORD_OF_DAY_FILE = os.path.join(DATA_DIR, 'word_of_day.json')
USER_PROGRESS_FILE = os.path.join(DATA_DIR, 'user_progress.json')
USER_PREFERENCES_FILE = os.path.join(DATA_DIR, 'user_preferences.json')
LEARNING_ANALYTICS_FILE = os.path.join(DATA_DIR, 'learning_analytics.json')

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_file(file_path, default=None):
    """Enhanced JSON file loading with error handling"""
    try:
        if not os.path.exists(file_path):
            default_data = default if default is not None else {}
            save_json_file(file_path, default_data)
            return default_data
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Loaded data from {file_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        backup_path = f"{file_path}.backup.{int(time.time())}"
        try:
            os.rename(file_path, backup_path)
            logger.info(f"Corrupted file backed up to {backup_path}")
        except:
            pass
        default_data = default if default is not None else {}
        save_json_file(file_path, default_data)
        return default_data
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return default if default is not None else {}

def save_json_file(file_path, data):
    """Enhanced JSON file saving with atomic writes"""
    ensure_data_directory()
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Atomic move
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            os.replace(file_path, backup_path)
        os.replace(temp_path, file_path)
        
        logger.debug(f"Saved data to {file_path}")
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

@app.route('/api/common-phrases', methods=['GET'])
@rate_limit
def get_common_phrases():
    """Get common phrases for a language with enhanced categorization"""
    try:
        language = request.args.get('language')
        category = request.args.get('category', 'all')
        difficulty = request.args.get('difficulty', 'all')
        
        if not language:
            return jsonify({'error': 'Language parameter required'}), 400
        
        phrases_data = load_json_file(PHRASES_FILE, {
            'phrases': {},
            'categories': ['greetings', 'travel', 'food', 'business', 'casual'],
            'difficulties': ['beginner', 'intermediate', 'advanced']
        })
        
        language_phrases = phrases_data.get('phrases', {}).get(language, [])
        
        # Filter by category and difficulty
        if category != 'all':
            language_phrases = [p for p in language_phrases if p.get('category') == category]
        
        if difficulty != 'all':
            language_phrases = [p for p in language_phrases if p.get('difficulty') == difficulty]
        
        return jsonify({
            'phrases': language_phrases,
            'total': len(language_phrases),
            'categories': phrases_data.get('categories', []),
            'difficulties': phrases_data.get('difficulties', [])
        })
        
    except Exception as e:
        logger.error(f"Error fetching common phrases: {e}")
        return jsonify({'error': 'Failed to fetch common phrases'}), 500

@app.route('/api/word-of-day', methods=['GET'])
@rate_limit
def get_word_of_day():
    """Enhanced word of the day with more details"""
    try:
        language = request.args.get('language')
        if not language:
            return jsonify({'error': 'Language parameter required'}), 400
        
        words_data = load_json_file(WORD_OF_DAY_FILE, {'words': {}})
    
        if language not in words_data.get('words', {}):
            return jsonify({'error': f'Language {language} not supported'}), 404
        
        word_list = words_data['words'][language]
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Use date as seed for consistent daily word
        random.seed(today + language)
        word_data = random.choice(word_list)
        
        # Enhanced word data structure
        enhanced_word = {
            'word': word_data.get('word', ''),
            'translation': word_data.get('translation', ''),
            'pronunciation': word_data.get('pronunciation', ''),
            'part_of_speech': word_data.get('part_of_speech', ''),
            'difficulty': word_data.get('difficulty', 'beginner'),
            'example_sentence': word_data.get('example_sentence', ''),
            'example_translation': word_data.get('example_translation', ''),
            'etymology': word_data.get('etymology', ''),
            'related_words': word_data.get('related_words', []),
            'cultural_note': word_data.get('cultural_note', ''),
            'date': today,
            'language': language
        }
        
        return jsonify(enhanced_word)
        
    except Exception as e:
        logger.error(f"Error fetching word of day: {e}")
        return jsonify({'error': 'Failed to fetch word of the day'}), 500

@app.route('/api/flashcards', methods=['POST'])
@rate_limit
def create_flashcard():
    """Enhanced flashcard creation with validation and analytics"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_id = data.get('userId')
        translation = data.get('translation')
        difficulty = data.get('difficulty', 'beginner')
        category = data.get('category', 'general')
        notes = data.get('notes', '')
        
        if not all([user_id, translation]):
            return jsonify({'error': 'Missing required parameters: userId, translation'}), 400
            
        # Validate translation structure
        required_translation_fields = ['original', 'translated', 'sourceLang', 'targetLang']
        missing_fields = [field for field in required_translation_fields if not translation.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Invalid translation data. Missing: {", ".join(missing_fields)}'
            }), 400
            
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        
        if user_id not in progress['users']:
            progress['users'][user_id] = {
                'flashcards': [],
                'quiz_scores': [],
                'practice_sessions': [],
                'learning_stats': {
                    'total_cards': 0,
                    'mastered_cards': 0,
                    'study_streak': 0,
                    'last_study_date': None
                }
            }
            
        user_data = progress['users'][user_id]
        
        # Generate unique ID
        flashcard_id = str(uuid.uuid4())
            
        flashcard = {
            'id': flashcard_id,
            'translation': translation,
            'difficulty': difficulty,
            'category': category,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'review_count': 0,
            'mastery_level': 0,
            'next_review': datetime.now().isoformat(),
            'last_review': None,
            'success_rate': 0.0,
            'review_history': []
        }
        
        user_data['flashcards'].append(flashcard)
        user_data['learning_stats']['total_cards'] += 1
        
        save_json_file(USER_PROGRESS_FILE, progress)
        
        logger.info(f"Created flashcard for user {user_id}: {translation['original']}")
        return jsonify({
            'success': True,
            'flashcard': flashcard,
            'stats': user_data['learning_stats']
        })
        
    except Exception as e:
        logger.error(f"Error creating flashcard: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create flashcard'}), 500

@app.route('/api/flashcards', methods=['GET'])
@rate_limit
def get_flashcards():
    """Get user's flashcards with filtering and sorting options"""
    try:
        user_id = request.args.get('userId')
        category = request.args.get('category', 'all')
        difficulty = request.args.get('difficulty', 'all')
        sort_by = request.args.get('sortBy', 'created_at')
        order = request.args.get('order', 'desc')
        limit = int(request.args.get('limit', 50))
        
        if not user_id:
            return jsonify({'error': 'UserId parameter required'}), 400
            
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        user_data = progress.get('users', {}).get(user_id, {'flashcards': []})
        flashcards = user_data.get('flashcards', [])
        
        # Apply filters
        if category != 'all':
            flashcards = [f for f in flashcards if f.get('category') == category]
        
        if difficulty != 'all':
            flashcards = [f for f in flashcards if f.get('difficulty') == difficulty]
        
        # Sort flashcards
        reverse = order == 'desc'
        if sort_by == 'mastery_level':
            flashcards.sort(key=lambda x: x.get('mastery_level', 0), reverse=reverse)
        elif sort_by == 'review_count':
            flashcards.sort(key=lambda x: x.get('review_count', 0), reverse=reverse)
        elif sort_by == 'next_review':
            flashcards.sort(key=lambda x: x.get('next_review', ''), reverse=reverse)
        else:  # created_at
            flashcards.sort(key=lambda x: x.get('created_at', ''), reverse=reverse)
        
        # Apply limit
        flashcards = flashcards[:limit]
        
        return jsonify({
            'flashcards': flashcards,
            'total': len(flashcards),
            'stats': user_data.get('learning_stats', {})
        })
        
    except Exception as e:
        logger.error(f"Error fetching flashcards: {e}")
        return jsonify({'error': 'Failed to fetch flashcards'}), 500

@app.route('/api/flashcards/<flashcard_id>/review', methods=['POST'])
@rate_limit
def review_flashcard(flashcard_id):
    """Record flashcard review with spaced repetition algorithm"""
    try:
        data = request.json
        user_id = data.get('userId')
        correct = data.get('correct', False)
        time_taken = data.get('timeTaken', 0)  # in seconds
        
        if not user_id:
            return jsonify({'error': 'UserId required'}), 400
            
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        user_data = progress.get('users', {}).get(user_id)
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Find the flashcard
        flashcard = None
        for card in user_data.get('flashcards', []):
            if card.get('id') == flashcard_id:
                flashcard = card
                break
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        # Update flashcard with spaced repetition
        flashcard['review_count'] += 1
        flashcard['last_review'] = datetime.now().isoformat()
        
        # Update success rate
        review_history = flashcard.get('review_history', [])
        review_history.append({
            'timestamp': datetime.now().isoformat(),
            'correct': correct,
            'time_taken': time_taken
        })
        flashcard['review_history'] = review_history[-20:]  # Keep last 20 reviews
        
        correct_reviews = sum(1 for r in review_history if r['correct'])
        flashcard['success_rate'] = correct_reviews / len(review_history) * 100
        
        # Spaced repetition algorithm
        if correct:
            flashcard['mastery_level'] = min(5, flashcard['mastery_level'] + 1)
            # Increase interval: 1 day, 3 days, 7 days, 14 days, 30 days
            intervals = [1, 3, 7, 14, 30]
            interval = intervals[min(flashcard['mastery_level'], len(intervals) - 1)]
        else:
            flashcard['mastery_level'] = max(0, flashcard['mastery_level'] - 1)
            interval = 1  # Reset to 1 day if incorrect
        
        next_review = datetime.now() + timedelta(days=interval)
        flashcard['next_review'] = next_review.isoformat()
        flashcard['updated_at'] = datetime.now().isoformat()
        
        # Update user stats
        stats = user_data.get('learning_stats', {})
        if flashcard['mastery_level'] >= 4 and correct:
            stats['mastered_cards'] = len([c for c in user_data['flashcards'] if c.get('mastery_level', 0) >= 4])
        
        stats['last_study_date'] = datetime.now().isoformat()
        
        save_json_file(USER_PROGRESS_FILE, progress)
        
        return jsonify({
            'success': True,
            'flashcard': flashcard,
            'next_interval_days': interval,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error reviewing flashcard: {e}", exc_info=True)
        return jsonify({'error': 'Failed to record review'}), 500

def generate_quiz():
    """Generate a dynamic quiz based on user's learning history and proficiency"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        language = data.get('language')
        difficulty = data.get('difficulty', 'beginner')
        quiz_type = data.get('type', 'mixed')  # mixed, vocabulary, grammar, conversation
        
        if not all([user_id, language]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Load user data and flashcards
        user_data_path = os.path.join('data', 'users', f'{user_id}.json')
        user_data = load_json_file(user_data_path, default={})
        flashcards = user_data.get('flashcards', [])
        conversation_history = user_data.get('conversation_history', [])
        
        # Initialize quiz questions
        questions = []
        total_questions = 10
        
        if quiz_type == 'mixed' or quiz_type == 'vocabulary':
            # Vocabulary questions (40% of mixed quiz)
            num_vocab = total_questions if quiz_type == 'vocabulary' else 4
            vocab_questions = generate_vocabulary_questions(flashcards, difficulty, num_vocab)
            questions.extend(vocab_questions)
            
        if quiz_type == 'mixed' or quiz_type == 'grammar':
            # Grammar questions (30% of mixed quiz)
            num_grammar = total_questions if quiz_type == 'grammar' else 3
            grammar_questions = generate_grammar_questions(flashcards, difficulty, num_grammar)
            questions.extend(grammar_questions)
            
        if quiz_type == 'mixed' or quiz_type == 'conversation':
            # Conversation questions (30% of mixed quiz)
            num_conversation = total_questions if quiz_type == 'conversation' else 3
            conversation_questions = generate_conversation_questions(conversation_history, difficulty, num_conversation)
            questions.extend(conversation_questions)
            
        # Shuffle questions
        random.shuffle(questions)
        
        # Store quiz in user data
        quiz_id = str(uuid.uuid4())
        if 'quizzes' not in user_data:
            user_data['quizzes'] = {}
            
        user_data['quizzes'][quiz_id] = {
            'questions': questions,
            'started_at': datetime.now().isoformat(),
            'completed': False,
            'score': 0,
            'answers': []
        }
        
        save_json_file(user_data_path, user_data)
        
        return jsonify({
            'quiz_id': quiz_id,
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_vocabulary_questions(flashcards, difficulty, count):
    """Generate vocabulary-based questions"""
    questions = []
    recent_flashcards = sorted(flashcards, key=lambda x: x.get('last_reviewed', ''), reverse=True)[:50]
    
    for _ in range(count):
        if not recent_flashcards:
            break
            
        card = random.choice(recent_flashcards)
        question_type = random.choice(['translation', 'multiple_choice', 'fill_blank'])
        
        if question_type == 'translation':
            questions.append({
                'type': 'translation',
                'text': card['word'],
                'correct_answer': card['translation'],
                'points': 10,
                'hint': card.get('pronunciation', '')
            })
        elif question_type == 'multiple_choice':
            # Generate distractors from other flashcards
            distractors = [fc['translation'] for fc in random.sample(flashcards, 3) if fc['id'] != card['id']]
            options = distractors + [card['translation']]
            random.shuffle(options)
            
            questions.append({
                'type': 'multiple_choice',
                'text': f"What is the meaning of '{card['word']}'?",
                'options': options,
                'correct_answer': card['translation'],
                'points': 8
            })
        else:  # fill_blank
            context = card.get('example', '').replace(card['word'], '_____')
            questions.append({
                'type': 'fill_blank',
                'text': context,
                'correct_answer': card['word'],
                'points': 12,
                'hint': f"Translation: {card['translation']}"
            })
            
    return questions

def generate_grammar_questions(flashcards, difficulty, count):
    """Generate grammar-based questions"""
    questions = []
    grammar_patterns = {
        'beginner': [
            {'pattern': 'simple_present', 'points': 8},
            {'pattern': 'simple_past', 'points': 10},
            {'pattern': 'basic_articles', 'points': 6}
        ],
        'intermediate': [
            {'pattern': 'perfect_tenses', 'points': 12},
            {'pattern': 'conditionals', 'points': 15},
            {'pattern': 'passive_voice', 'points': 12}
        ],
        'advanced': [
            {'pattern': 'subjunctive', 'points': 18},
            {'pattern': 'complex_clauses', 'points': 20},
            {'pattern': 'idiomatic_expressions', 'points': 15}
        ]
    }
    
    patterns = grammar_patterns.get(difficulty, grammar_patterns['beginner'])
    
    for _ in range(count):
        pattern = random.choice(patterns)
        
        # Generate grammar question using Gemini
        prompt = f"""
        Generate a grammar question for {difficulty} level learners focusing on {pattern['pattern']}.
        Include:
        1. Question text
        2. 4 possible answers
        3. Correct answer
        4. Explanation
        Format as JSON.
        """
        
        response = model.generate_content(prompt)
        question_data = json.loads(response.text)
        
        questions.append({
            'type': 'grammar',
            'text': question_data['question'],
            'options': question_data['options'],
            'correct_answer': question_data['correct_answer'],
            'explanation': question_data['explanation'],
            'points': pattern['points']
        })
        
    return questions

def generate_conversation_questions(conversation_history, difficulty, count):
    """Generate conversation-based questions"""
    questions = []
    recent_conversations = sorted(conversation_history, key=lambda x: x['timestamp'], reverse=True)[:20]
    
    for _ in range(count):
        if not recent_conversations:
            break
            
        conversation = random.choice(recent_conversations)
        
        # Generate conversation question using Gemini
        prompt = f"""
        Based on this conversation: "{conversation['user_input']}"
        Generate a question that tests the learner's ability to respond appropriately in this context.
        Include:
        1. Scenario description
        2. Question
        3. 4 possible responses
        4. Correct response
        5. Explanation of why it's correct
        Format as JSON.
        """
        
        response = model.generate_content(prompt)
        question_data = json.loads(response.text)
        
        questions.append({
            'type': 'conversation',
            'scenario': question_data['scenario'],
            'text': question_data['question'],
            'options': question_data['options'],
            'correct_answer': question_data['correct_answer'],
            'explanation': question_data['explanation'],
            'points': 15
        })
        
    return questions

@app.route('/api/quiz/<quiz_id>/submit', methods=['POST'])
@rate_limit
def submit_quiz_answer(quiz_id):
    """Submit and evaluate a quiz answer"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        answer = data.get('answer')
        question_index = data.get('questionIndex')
        
        if not all([user_id, answer, question_index is not None]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Load user data
        user_data_path = os.path.join('data', 'users', f'{user_id}.json')
        user_data = load_json_file(user_data_path, default={})
        
        if 'quizzes' not in user_data or quiz_id not in user_data['quizzes']:
            return jsonify({'error': 'Quiz not found'}), 404
            
        quiz = user_data['quizzes'][quiz_id]
        if quiz['completed']:
            return jsonify({'error': 'Quiz already completed'}), 400
            
        question = quiz['questions'][question_index]
        is_correct = False
        points_earned = 0
        
        # Evaluate answer based on question type
        if question['type'] in ['multiple_choice', 'conversation']:
            is_correct = answer == question['correct_answer']
            points_earned = question['points'] if is_correct else 0
        elif question['type'] == 'translation':
            # Use fuzzy matching for translations
            similarity = fuzz.ratio(answer.lower(), question['correct_answer'].lower())
            is_correct = similarity >= 80
            points_earned = int(question['points'] * (similarity / 100))
        elif question['type'] == 'fill_blank':
            # Case-insensitive exact match for fill in the blank
            is_correct = answer.lower() == question['correct_answer'].lower()
            points_earned = question['points'] if is_correct else 0
        elif question['type'] == 'grammar':
            is_correct = answer == question['correct_answer']
            points_earned = question['points'] if is_correct else 0
            
        # Record answer
        quiz['answers'].append({
            'question_index': question_index,
            'user_answer': answer,
            'correct': is_correct,
            'points_earned': points_earned,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update quiz score
        quiz['score'] += points_earned
        
        # Check if quiz is completed
        if len(quiz['answers']) == len(quiz['questions']):
            quiz['completed'] = True
            quiz['completed_at'] = datetime.now().isoformat()
            
            # Update user progress
            if 'progress' not in user_data:
                user_data['progress'] = {
                    'quizzes_completed': 0,
                    'total_points': 0,
                    'average_score': 0
                }
                
            progress = user_data['progress']
            progress['quizzes_completed'] += 1
            progress['total_points'] += quiz['score']
            progress['average_score'] = progress['total_points'] / progress['quizzes_completed']
            
        save_json_file(user_data_path, user_data)
        
        return jsonify({
            'correct': is_correct,
            'points_earned': points_earned,
            'total_score': quiz['score'],
            'completed': quiz['completed'],
            'explanation': question.get('explanation', '')
        })
        
    except Exception as e:
        logger.error(f"Error submitting quiz answer: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/progress', methods=['GET'])
@rate_limit
def get_user_progress():
    """Get comprehensive user progress and statistics"""
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'UserId parameter required'}), 400
        
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        user_data = progress.get('users', {}).get(user_id, {})
        
        if not user_data:
            # Return default progress for new user
            return jsonify({
                'flashcards_count': 0,
                'quiz_scores': [],
                'learning_stats': {
                    'total_cards': 0,
                    'mastered_cards': 0,
                    'study_streak': 0,
                    'last_study_date': None
                },
                'weekly_activity': [],
                'skill_levels': {},
                'achievements': []
            })
        
        # Calculate additional statistics
        flashcards = user_data.get('flashcards', [])
        quiz_scores = user_data.get('quiz_scores', [])
        
        # Weekly activity calculation
        weekly_activity = calculate_weekly_activity(user_data)
        
        # Skill levels by language
        skill_levels = calculate_skill_levels(flashcards, quiz_scores)
        
        # Achievement calculation
        achievements = calculate_achievements(user_data)
        
        return jsonify({
            'flashcards_count': len(flashcards),
            'quiz_scores': quiz_scores[-10:],  # Last 10 quiz scores
            'learning_stats': user_data.get('learning_stats', {}),
            'weekly_activity': weekly_activity,
            'skill_levels': skill_levels,
            'achievements': achievements,
            'total_study_time': calculate_total_study_time(user_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching user progress: {e}")
        return jsonify({'error': 'Failed to fetch progress'}), 500

def calculate_weekly_activity(user_data):
    """Calculate activity for the past 7 days"""
    activity = []
    today = datetime.now()
    
    for i in range(7):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Count reviews for this date
        reviews = 0
        for card in user_data.get('flashcards', []):
            for review in card.get('review_history', []):
                review_date = datetime.fromisoformat(review['timestamp']).strftime('%Y-%m-%d')
                if review_date == date_str:
                    reviews += 1
        
        activity.append({
            'date': date_str,
            'reviews': reviews,
            'day_name': date.strftime('%A')
        })
    
    return list(reversed(activity))

def calculate_skill_levels(flashcards, quiz_scores):
    """Calculate skill levels by language"""
    skill_levels = {}
    
    # Analyze flashcards by language
    for card in flashcards:
        translation = card.get('translation', {})
        source_lang = translation.get('sourceLang')
        target_lang = translation.get('targetLang')
        
        for lang in [source_lang, target_lang]:
            if lang and lang not in skill_levels:
                skill_levels[lang] = {
                    'level': 'beginner',
                    'progress': 0,
                    'cards_count': 0,
                    'mastered_count': 0
                }
        
        for lang in [source_lang, target_lang]:
            if lang:
                skill_levels[lang]['cards_count'] += 1
                if card.get('mastery_level', 0) >= 4:
                    skill_levels[lang]['mastered_count'] += 1
    
    # Calculate progress and levels
    for lang, data in skill_levels.items():
        if data['cards_count'] > 0:
            mastery_ratio = data['mastered_count'] / data['cards_count']
            if mastery_ratio >= 0.8:
                data['level'] = 'advanced'
                data['progress'] = min(100, mastery_ratio * 100)
            elif mastery_ratio >= 0.5:
                data['level'] = 'intermediate'
                data['progress'] = mastery_ratio * 100
            else:
                data['level'] = 'beginner'
                data['progress'] = mastery_ratio * 100
    
    return skill_levels

def calculate_achievements(user_data):
    """Calculate user achievements"""
    achievements = []
    
    flashcards = user_data.get('flashcards', [])
    quiz_scores = user_data.get('quiz_scores', [])
    stats = user_data.get('learning_stats', {})
    
    # Achievement: First Flashcard
    if len(flashcards) >= 1:
        achievements.append({
            'id': 'first_flashcard',
            'title': 'First Steps',
            'description': 'Created your first flashcard',
            'icon': '📚',
            'unlocked': True
        })
    
    # Achievement: 10 Flashcards
    if len(flashcards) >= 10:
        achievements.append({
            'id': 'ten_flashcards',
            'title': 'Getting Started',
            'description': 'Created 10 flashcards',
            'icon': '📖',
            'unlocked': True
        })
    
    # Achievement: First Quiz
    if len(quiz_scores) >= 1:
        achievements.append({
            'id': 'first_quiz',
            'title': 'Quiz Master',
            'description': 'Completed your first quiz',
            'icon': '🎯',
            'unlocked': True
        })
    
    # Achievement: Perfect Quiz Score
    perfect_quizzes = [q for q in quiz_scores if q.get('percentage', 0) == 100]
    if perfect_quizzes:
        achievements.append({
            'id': 'perfect_score',
            'title': 'Perfectionist',
            'description': 'Scored 100% on a quiz',
            'icon': '🌟',
            'unlocked': True
        })
    
    # Achievement: Mastered Cards
    mastered_count = stats.get('mastered_cards', 0)
    if mastered_count >= 5:
        achievements.append({
            'id': 'master_five',
            'title': 'Card Master',
            'description': 'Mastered 5 flashcards',
            'icon': '🏆',
            'unlocked': True
        })
    
    return achievements

def calculate_total_study_time(user_data):
    """Calculate total study time in minutes"""
    total_time = 0
    
    # Time from flashcard reviews
    for card in user_data.get('flashcards', []):
        for review in card.get('review_history', []):
            total_time += review.get('time_taken', 0)
    
    # Time from quiz sessions (estimate 30 seconds per question)
    for score in user_data.get('quiz_scores', []):
        total_time += score.get('total_questions', 0) * 30
    
    return round(total_time / 60, 1)  # Convert to minutes

# List of supported languages with their codes and names
SUPPORTED_LANGUAGES = [
    {'code': 'en', 'name': 'English', 'native_name': 'English'},
    {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
    {'code': 'fr', 'name': 'French', 'native_name': 'Français'},
    {'code': 'de', 'name': 'German', 'native_name': 'Deutsch'},
    {'code': 'it', 'name': 'Italian', 'native_name': 'Italiano'},
    {'code': 'pt', 'name': 'Portuguese', 'native_name': 'Português'},
    {'code': 'ru', 'name': 'Russian', 'native_name': 'Русский'},
    {'code': 'ja', 'name': 'Japanese', 'native_name': '日本語'},
    {'code': 'ko', 'name': 'Korean', 'native_name': '한국어'},
    {'code': 'zh', 'name': 'Chinese (Simplified)', 'native_name': '中文 (简体)'},
    {'code': 'zh-TW', 'name': 'Chinese (Traditional)', 'native_name': '中文 (繁體)'},
    {'code': 'ar', 'name': 'Arabic', 'native_name': 'العربية'},
    {'code': 'hi', 'name': 'Hindi', 'native_name': 'हिन्दी'},
    {'code': 'th', 'name': 'Thai', 'native_name': 'ไทย'},
    {'code': 'vi', 'name': 'Vietnamese', 'native_name': 'Tiếng Việt'},
    {'code': 'nl', 'name': 'Dutch', 'native_name': 'Nederlands'},
    {'code': 'pl', 'name': 'Polish', 'native_name': 'Polski'},
    {'code': 'tr', 'name': 'Turkish', 'native_name': 'Türkçe'},
    {'code': 'sv', 'name': 'Swedish', 'native_name': 'Svenska'},
    {'code': 'da', 'name': 'Danish', 'native_name': 'Dansk'},
    {'code': 'no', 'name': 'Norwegian', 'native_name': 'Norsk'},
    {'code': 'fi', 'name': 'Finnish', 'native_name': 'Suomi'},
    {'code': 'he', 'name': 'Hebrew', 'native_name': 'עברית'},
    {'code': 'cs', 'name': 'Czech', 'native_name': 'Čeština'},
    {'code': 'sk', 'name': 'Slovak', 'native_name': 'Slovenčina'},
    {'code': 'hu', 'name': 'Hungarian', 'native_name': 'Magyar'},
    {'code': 'ro', 'name': 'Romanian', 'native_name': 'Română'},
    {'code': 'bg', 'name': 'Bulgarian', 'native_name': 'Български'},
    {'code': 'hr', 'name': 'Croatian', 'native_name': 'Hrvatski'},
    {'code': 'sr', 'name': 'Serbian', 'native_name': 'Српски'},
    {'code': 'sl', 'name': 'Slovenian', 'native_name': 'Slovenščina'},
    {'code': 'et', 'name': 'Estonian', 'native_name': 'Eesti'},
    {'code': 'lv', 'name': 'Latvian', 'native_name': 'Latviešu'},
    {'code': 'lt', 'name': 'Lithuanian', 'native_name': 'Lietuvių'},
    {'code': 'mt', 'name': 'Maltese', 'native_name': 'Malti'},
    {'code': 'ga', 'name': 'Irish', 'native_name': 'Gaeilge'},
    {'code': 'cy', 'name': 'Welsh', 'native_name': 'Cymraeg'},
    {'code': 'eu', 'name': 'Basque', 'native_name': 'Euskera'},
    {'code': 'ca', 'name': 'Catalan', 'native_name': 'Català'},
    {'code': 'gl', 'name': 'Galician', 'native_name': 'Galego'},
    {'code': 'is', 'name': 'Icelandic', 'native_name': 'Íslenska'},
    {'code': 'mk', 'name': 'Macedonian', 'native_name': 'Македонски'},
    {'code': 'sq', 'name': 'Albanian', 'native_name': 'Shqip'},
    {'code': 'sw', 'name': 'Swahili', 'native_name': 'Kiswahili'},
    {'code': 'am', 'name': 'Amharic', 'native_name': 'አማርኛ'},
    {'code': 'id', 'name': 'Indonesian', 'native_name': 'Bahasa Indonesia'},
    {'code': 'ms', 'name': 'Malay', 'native_name': 'Bahasa Melayu'},
    {'code': 'tl', 'name': 'Filipino', 'native_name': 'Filipino'},
    {'code': 'ur', 'name': 'Urdu', 'native_name': 'اردو'},
    {'code': 'bn', 'name': 'Bengali', 'native_name': 'বাংলা'},
    {'code': 'ta', 'name': 'Tamil', 'native_name': 'தமிழ்'},
    {'code': 'te', 'name': 'Telugu', 'native_name': 'తెలుగు'},
    {'code': 'ml', 'name': 'Malayalam', 'native_name': 'മലയാളം'},
    {'code': 'kn', 'name': 'Kannada', 'native_name': 'ಕನ್ನಡ'},
    {'code': 'gu', 'name': 'Gujarati', 'native_name': 'ગુજરાતી'},
    {'code': 'mr', 'name': 'Marathi', 'native_name': 'मराठी'},
    {'code': 'pa', 'name': 'Punjabi', 'native_name': 'ਪੰਜਾਬੀ'},
    {'code': 'ne', 'name': 'Nepali', 'native_name': 'नेपाली'},
    {'code': 'si', 'name': 'Sinhala', 'native_name': 'සිංහල'},
    {'code': 'my', 'name': 'Myanmar (Burmese)', 'native_name': 'မြန်မာ'},
    {'code': 'km', 'name': 'Khmer', 'native_name': 'ខ្មែរ'},
    {'code': 'lo', 'name': 'Lao', 'native_name': 'ລາວ'},
    {'code': 'ka', 'name': 'Georgian', 'native_name': 'ქართული'},
    {'code': 'hy', 'name': 'Armenian', 'native_name': 'Հայերեն'},
    {'code': 'az', 'name': 'Azerbaijani', 'native_name': 'Azərbaycan'},
    {'code': 'kk', 'name': 'Kazakh', 'native_name': 'Қазақша'},
    {'code': 'ky', 'name': 'Kyrgyz', 'native_name': 'Кыргызча'},
    {'code': 'uz', 'name': 'Uzbek', 'native_name': 'O\'zbek'},
    {'code': 'tg', 'name': 'Tajik', 'native_name': 'Тоҷикӣ'},
    {'code': 'mn', 'name': 'Mongolian', 'native_name': 'Монгол'},
    {'code': 'bo', 'name': 'Tibetan', 'native_name': 'བོད་ཡིག'},
    {'code': 'dz', 'name': 'Dzongkha', 'native_name': 'རྫོང་ཁ'}
]

@app.route('/api/supported-languages', methods=['GET'])
@rate_limit
def get_supported_languages():
    """Get list of supported languages with enhanced information"""
    try:
        # Add popularity and region information
        enhanced_languages = []
        for lang in SUPPORTED_LANGUAGES:
            enhanced_lang = {
                **lang,
                'popularity': get_language_popularity(lang['code']),
                'region': get_language_region(lang['code']),
                'writing_system': get_writing_system(lang['code']),
                'tts_supported': is_tts_supported(lang['code']),
                'speech_recognition_supported': is_speech_recognition_supported(lang['code'])
            }
            enhanced_languages.append(enhanced_lang)
        
        # Sort by popularity
        enhanced_languages.sort(key=lambda x: x['popularity'], reverse=True)
        
        return jsonify({
            'languages': enhanced_languages,
            'total': len(enhanced_languages),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching supported languages: {e}")
        return jsonify({'error': 'Failed to fetch supported languages'}), 500

def get_language_popularity(code):
    """Get language popularity score (1-10)"""
    popular_languages = {
        'en': 10, 'es': 9, 'fr': 8, 'de': 8, 'it': 7, 'pt': 7,
        'ru': 7, 'ja': 8, 'ko': 7, 'zh': 9, 'ar': 8, 'hi': 8
    }
    return popular_languages.get(code, 5)

def get_language_region(code):
    """Get language region"""
    regions = {
        'en': 'Global', 'es': 'Americas/Europe', 'fr': 'Europe/Africa',
        'de': 'Europe', 'it': 'Europe', 'pt': 'Americas/Europe',
        'ru': 'Europe/Asia', 'ja': 'East Asia', 'ko': 'East Asia',
        'zh': 'East Asia', 'ar': 'Middle East/North Africa', 'hi': 'South Asia'
    }
    return regions.get(code, 'Regional')

def get_writing_system(code):
    """Get writing system type"""
    systems = {
        'en': 'Latin', 'es': 'Latin', 'fr': 'Latin', 'de': 'Latin',
        'it': 'Latin', 'pt': 'Latin', 'ru': 'Cyrillic', 'ja': 'Hiragana/Katakana/Kanji',
        'ko': 'Hangul', 'zh': 'Chinese Characters', 'ar': 'Arabic', 'hi': 'Devanagari'
    }
    return systems.get(code, 'Latin')

def is_tts_supported(code):
    """Check if TTS is supported for language"""
    # In a real implementation, check with TTS service
    return code in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']

def is_speech_recognition_supported(code):
    """Check if speech recognition is supported for language"""
    # In a real implementation, check with speech service
    return code in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']

@app.route('/api/detect-language', methods=['POST'])
@rate_limit
def detect_language():
    """Enhanced language detection with confidence scoring"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text parameter required'}), 400
            
        if len(text) > 500:
            return jsonify({'error': 'Text too long (max 500 characters)'}), 400
        
        # Check cache first
        cache_key = get_cache_key({'text': text, 'operation': 'detect_language'})
        cached_result = get_cached_result(translation_cache, cache_key)
        if cached_result:
            logger.info(f"Returning cached language detection for: {text[:30]}...")
            return jsonify(cached_result)
        
        if not model:
            return jsonify({'error': 'Language detection service temporarily unavailable'}), 503
        
        # Use Gemini for language detection
        prompt = f"""Detect the language of this text and provide confidence scores for top 3 most likely languages.

Text: "{text}"

Return ONLY a valid JSON response with this exact structure:
{{
    "detected_language": "language_code",
    "confidence": confidence_percentage,
    "alternatives": [
        {{"language": "code", "confidence": percentage, "name": "Language Name"}},
        {{"language": "code", "confidence": percentage, "name": "Language Name"}},
        {{"language": "code", "confidence": percentage, "name": "Language Name"}}
    ],
    "text_length": number_of_characters,
    "is_mixed_language": boolean
}}

Use standard ISO 639-1 language codes (en, es, fr, de, etc.)."""

        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
                
            detection_data = json.loads(response.text)
            
            # Add metadata
            detection_data['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'cached': False,
                'method': 'gemini_ai'
            }
            
            # Cache the result
            cache_result(translation_cache, cache_key, detection_data)
            
            logger.info(f"Language detection completed: {detection_data.get('detected_language')} ({detection_data.get('confidence')}%)")
            return jsonify(detection_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in language detection: {e}")
            
            # Fallback to simple heuristic detection
            fallback_result = simple_language_detection(text)
            return jsonify(fallback_result)
        
    except Exception as e:
            logger.error(f"Gemini language detection error: {e}")
            
            # Fallback to simple heuristic detection
            fallback_result = simple_language_detection(text)
            return jsonify(fallback_result)
            
    except Exception as e:
        logger.error(f"Language detection error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to detect language'}), 500

def simple_language_detection(text):
    """Simple fallback language detection using character analysis"""
    char_counts = {}
    
    # Count character types
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # Chinese characters
            char_counts['zh'] = char_counts.get('zh', 0) + 1
        elif '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':  # Japanese
            char_counts['ja'] = char_counts.get('ja', 0) + 1
        elif '\uac00' <= char <= '\ud7af':  # Korean
            char_counts['ko'] = char_counts.get('ko', 0) + 1
        elif '\u0600' <= char <= '\u06ff':  # Arabic
            char_counts['ar'] = char_counts.get('ar', 0) + 1
        elif '\u0900' <= char <= '\u097f':  # Devanagari (Hindi)
            char_counts['hi'] = char_counts.get('hi', 0) + 1
        elif '\u0400' <= char <= '\u04ff':  # Cyrillic (Russian)
            char_counts['ru'] = char_counts.get('ru', 0) + 1
    
    if char_counts:
        detected_lang = max(char_counts, key=char_counts.get)
        confidence = min(95, (char_counts[detected_lang] / len(text)) * 100)
    else:
        # Default to English for Latin script
        detected_lang = 'en'
        confidence = 60
    
    return {
        'detected_language': detected_lang,
        'confidence': confidence,
        'alternatives': [
            {'language': detected_lang, 'confidence': confidence, 'name': 'Detected Language'},
            {'language': 'en', 'confidence': 40, 'name': 'English'},
            {'language': 'es', 'confidence': 30, 'name': 'Spanish'}
        ],
        'text_length': len(text),
        'is_mixed_language': len(char_counts) > 1,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'cached': False,
            'method': 'character_analysis'
        }
    }

@app.route('/api/translate', methods=['POST'])
@rate_limit
def translate():
    """Enhanced basic translation endpoint with caching"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text', '').strip()
        source_lang = data.get('sourceLang')
        target_lang = data.get('targetLang')
        
        if not all([text, source_lang, target_lang]):
            return jsonify({'error': 'Missing required parameters: text, sourceLang, targetLang'}), 400
        
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        # Check cache first
        cache_key = get_cache_key({
            'text': text, 'source': source_lang, 'target': target_lang, 'type': 'basic'
        })
        
        cached_result = get_cached_result(translation_cache, cache_key)
        if cached_result:
            logger.info(f"Returning cached basic translation for: {text[:50]}...")
            return jsonify(cached_result)
        
        if not model:
            return jsonify({'error': 'Translation service temporarily unavailable'}), 503
        
        # Check if target language uses non-Latin script for romanization
        non_latin_languages = ['ar', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'hi', 'ru', 'th', 'he', 'ur', 'fa', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'pa', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am', 'ti', 'dv']
        needs_romanization = any(lang in target_lang.lower() for lang in non_latin_languages)
        
        if needs_romanization:
            # Enhanced translation prompt with romanization
            prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Provide the response in JSON format with the translation and romanization.

Text: {text}

Return JSON with these exact keys:
{{
    "translation": "translated text in original script",
    "romanization": "romanized version in Latin script",
    "romanization_system": "name of romanization system used"
}}"""
        else:
            # Simple translation prompt for Latin script languages
            prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Provide only the translation, no explanations.

Text: {text}

Translation:"""
        
        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            if needs_romanization:
                try:
                    # Parse JSON response for non-Latin languages
                    translation_data = json.loads(response.text)
                    translation = translation_data.get('translation', '').strip()
                    romanization = translation_data.get('romanization', '').strip()
                    romanization_system = translation_data.get('romanization_system', '').strip()
                    
                    result = {
                        'translation': translation,
                        'romanization': romanization,
                        'romanization_system': romanization_system,
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'original_text': text,
                        'timestamp': datetime.now().isoformat(),
                        'cached': False
                    }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    translation = response.text.strip()
                    result = {
                        'translation': translation,
                        'romanization': '',
                        'romanization_system': '',
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'original_text': text,
                        'timestamp': datetime.now().isoformat(),
                        'cached': False
                    }
            else:
                # Standard response for Latin script languages
                translation = response.text.strip()
                result = {
                    'translation': translation,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'original_text': text,
                    'timestamp': datetime.now().isoformat(),
                    'cached': False
                }
            
            # Cache the result
            cache_result(translation_cache, cache_key, result)
            
            logger.info(f"Basic translation completed: {text[:30]} -> {result['translation'][:30]}")
            return jsonify(result)
    
        except Exception as e:
            logger.error(f"Gemini basic translation error: {e}")
            return jsonify({'error': 'Translation failed'}), 503
            
    except Exception as e:
        logger.error(f"Basic translation error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
@rate_limit
def text_to_speech():
    """Enhanced text-to-speech with caching and voice options"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text', '').strip()
        language_code = data.get('languageCode', 'en')
        voice_gender = data.get('voiceGender', 'NEUTRAL')
        speed = data.get('speed', 1.0)
        pitch = data.get('pitch', 0.0)
        
        if not text:
            return jsonify({'error': 'Text parameter required'}), 400
            
        if len(text) > 500:
            return jsonify({'error': 'Text too long for TTS (max 500 characters)'}), 400
        
        # Check cache first
        cache_key = get_cache_key({
            'text': text, 'lang': language_code, 'gender': voice_gender,
            'speed': speed, 'pitch': pitch
        })
        
        cached_result = get_cached_result(tts_cache, cache_key)
        if cached_result:
            logger.info(f"Returning cached TTS for: {text[:30]}...")
            return jsonify(cached_result)
        
        if not tts_client:
            return jsonify({'error': 'Text-to-speech service temporarily unavailable'}), 503
        
        try:
            # Configure voice
            voice = tts.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=getattr(tts.SsmlVoiceGender, voice_gender, tts.SsmlVoiceGender.NEUTRAL)
            )

            # Configure audio
            audio_config = tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.MP3,
                speaking_rate=max(0.25, min(4.0, speed)),  # Clamp speed
                pitch=max(-20.0, min(20.0, pitch))         # Clamp pitch
            )
        
            # Synthesis input
            synthesis_input = tts.SynthesisInput(text=text)
            
            # Generate speech
            response = tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
        
            # Encode audio content
            audio_content = base64.b64encode(response.audio_content).decode('utf-8')
        
            result = {
                'audio_content': audio_content,
                'text': text,
                'language_code': language_code,
                'voice_gender': voice_gender,
                'speed': speed,
                'pitch': pitch,
                'duration_estimate': estimate_audio_duration(text, speed),
                'timestamp': datetime.now().isoformat(),
                'cached': False
            }
            
            # Cache the result
            cache_result(tts_cache, cache_key, result)
            
            logger.info(f"TTS completed for: {text[:30]}")
            return jsonify(result)
    
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return jsonify({'error': 'TTS generation failed'}), 503
            
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

def estimate_audio_duration(text, speed):
    """Estimate audio duration in seconds"""
    # Average reading speed: 200 words per minute
    words = len(text.split())
    base_duration = (words / 200) * 60  # seconds
    adjusted_duration = base_duration / speed
    return round(adjusted_duration, 1)

@app.route('/api/user/preferences', methods=['GET', 'POST'])
@rate_limit
def user_preferences():
    """Handle user preferences"""
    try:
        user_id = request.args.get('userId') or request.json.get('userId')
        if not user_id:
            return jsonify({'error': 'UserId parameter required'}), 400
        
        preferences_data = load_json_file(USER_PREFERENCES_FILE, {'users': {}})
        
        if request.method == 'GET':
            user_prefs = preferences_data.get('users', {}).get(user_id, {
                'default_source_lang': 'en',
                'default_target_lang': 'es',
                'voice_gender': 'NEUTRAL',
                'speech_speed': 1.0,
                'auto_play_translations': True,
                'save_history': True,
                'theme': 'light',
                'notifications_enabled': True,
                'study_reminders': True,
                'daily_goal': 10,
                'preferred_difficulty': 'beginner'
            })
            
            return jsonify(user_prefs)
        
        elif request.method == 'POST':
            data = request.json
            if user_id not in preferences_data['users']:
                preferences_data['users'][user_id] = {}
            
            # Update preferences
            user_prefs = preferences_data['users'][user_id]
            allowed_preferences = [
                'default_source_lang', 'default_target_lang', 'voice_gender',
                'speech_speed', 'auto_play_translations', 'save_history',
                'theme', 'notifications_enabled', 'study_reminders',
                'daily_goal', 'preferred_difficulty'
            ]
            
            for key, value in data.items():
                if key in allowed_preferences:
                    user_prefs[key] = value
            
            user_prefs['updated_at'] = datetime.now().isoformat()
            
            save_json_file(USER_PREFERENCES_FILE, preferences_data)
            
            return jsonify({
                'success': True,
                'preferences': user_prefs
            })
            
    except Exception as e:
        logger.error(f"User preferences error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to handle preferences'}), 500

@app.route('/api/analytics', methods=['POST'])
@rate_limit
def record_analytics():
    """Record user analytics for learning insights"""
    try:
        data = request.json
        user_id = data.get('userId')
        event_type = data.get('eventType')
        event_data = data.get('eventData', {})
        
        if not all([user_id, event_type]):
            return jsonify({'error': 'Missing required parameters: userId, eventType'}), 400
        
        analytics_data = load_json_file(LEARNING_ANALYTICS_FILE, {'events': []})
        
        event = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now().isoformat(),
            'session_id': data.get('sessionId'),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        }
        
        analytics_data['events'].append(event)
        
        # Keep only last 10000 events to prevent file from growing too large
        if len(analytics_data['events']) > 10000:
            analytics_data['events'] = analytics_data['events'][-10000:]
        
        save_json_file(LEARNING_ANALYTICS_FILE, analytics_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Analytics recording error: {e}")
        return jsonify({'error': 'Failed to record analytics'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': 60}), 429

# Cleanup function for cache
def cleanup_caches():
    """Clean up expired cache entries"""
    current_time = time.time()
    
    # Clean translation cache
    expired_keys = [
        key for key, (_, timestamp) in translation_cache.items()
        if current_time - timestamp > CACHE_DURATION
    ]
    for key in expired_keys:
        del translation_cache[key]
    
    # Clean TTS cache
    expired_keys = [
        key for key, (_, timestamp) in tts_cache.items()
        if current_time - timestamp > CACHE_DURATION
    ]
    for key in expired_keys:
        del tts_cache[key]
    
    logger.info(f"Cache cleanup completed. Removed {len(expired_keys)} expired entries")

# Schedule cache cleanup every hour
def schedule_cleanup():
    cleanup_caches()
    threading.Timer(3600, schedule_cleanup).start()

# Start cleanup scheduler
schedule_cleanup()

@app.route('/api/conversation', methods=['POST'])
@rate_limit
def conversation_practice():
    """Interactive conversation practice with AI"""
    try:
        data = request.get_json()
        user_input = data.get('text')
        language = data.get('language')
        user_id = data.get('userId')
        context = data.get('context', 'general')
        proficiency = data.get('proficiency', 'beginner')
        
        if not all([user_input, language, user_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Generate conversation prompt based on context and proficiency
        conversation_prompt = f"""
        Act as a native {language} speaker having a conversation. 
        The user's proficiency level is {proficiency}.
        Context: {context}
        
        Respond to: "{user_input}"
        
        Provide a response that includes:
        1. A natural response in {language}
        2. The translation in English
        3. Key vocabulary or phrases used
        4. Grammar points demonstrated
        5. Cultural context or notes
        6. Suggested follow-up responses for the user
        
        Format as JSON with these exact keys.
        """

        # Generate response using Gemini
        response = model.generate_content(conversation_prompt)
        
        # Track user progress
        user_data_path = os.path.join('data', 'users', f'{user_id}.json')
        user_data = load_json_file(user_data_path, default={})
        
        if 'conversation_history' not in user_data:
            user_data['conversation_history'] = []
        
        # Add conversation to history
        user_data['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'language': language,
            'context': context,
            'response': response.text
        })
        
        # Update user stats
        if 'stats' not in user_data:
            user_data['stats'] = {'conversations': 0, 'total_messages': 0}
        user_data['stats']['conversations'] += 1
        user_data['stats']['total_messages'] += 1
        
        save_json_file(user_data_path, user_data)
        
        return jsonify({
            'response': response.text,
            'stats': user_data['stats']
        })
        
    except Exception as e:
        logger.error(f"Error in conversation practice: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting TTS AI Backend Server...")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    logger.info(f"Services available: Gemini={model is not None}, TTS={tts_client is not None}, Speech={speech_client is not None}")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug) 