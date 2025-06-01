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
import re

# Import database service
from models import create_tables
from db_service import db_service

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
    logger.warning("GEMINI_API_KEY not found in environment variables")
    logger.warning("Translation services will be limited. Set GEMINI_API_KEY for full functionality.")
    model = None
else:
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
    """Enhanced health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'gemini': bool(genai.api_key),
                'speech_client': bool(speech_client),
                'tts_client': bool(tts_client)
            }
        }
        return jsonify(health_status)
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/debug/data-status', methods=['GET'])
def debug_data_status():
    """Debug endpoint to check data files status"""
    try:
        import os
        
        data_files_status = {
            'data_directory_exists': os.path.exists(DATA_DIR),
            'current_working_directory': os.getcwd(),
            'data_directory_path': os.path.abspath(DATA_DIR),
            'files': {}
        }
        
        # Check each data file
        data_files = {
            'word_of_day': WORD_OF_DAY_FILE,
            'common_phrases': PHRASES_FILE,
            'user_progress': USER_PROGRESS_FILE,
            'user_preferences': USER_PREFERENCES_FILE,
            'learning_analytics': LEARNING_ANALYTICS_FILE,
            'quizzes': QUIZZES_FILE
        }
        
        for name, file_path in data_files.items():
            file_exists = os.path.exists(file_path)
            file_size = os.path.getsize(file_path) if file_exists else 0
            
            status = {
                'exists': file_exists,
                'path': os.path.abspath(file_path),
                'size_bytes': file_size
            }
            
            # Try to load the file if it exists
            if file_exists and name == 'word_of_day':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        status['languages'] = list(data.get('words', {}).keys())
                        status['total_words'] = sum(len(words) for words in data.get('words', {}).values())
                except Exception as e:
                    status['load_error'] = str(e)
            
            data_files_status['files'][name] = status
        
        # List directory contents
        if os.path.exists(DATA_DIR):
            data_files_status['directory_contents'] = os.listdir(DATA_DIR)
        
        return jsonify(data_files_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
@rate_limit
def basic_translate():
    """
    Basic translation endpoint for simple translation requests.
    
    Returns:
        dict: Translation result with romanization for non-Latin scripts
    """
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
        
        # Input validation
        if len(text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
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
        
        # Generate basic translation prompt with romanization
        non_latin_languages = ['ar', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'hi', 'ru', 'th', 'he', 'ur', 'fa', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'pa', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am', 'ti', 'dv']
        needs_romanization = any(lang in target_lang.lower() for lang in non_latin_languages)
        
        if needs_romanization:
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. Return only a clean translation without any formatting. Also provide romanization for non-Latin scripts.

Text to translate: "{text}"

Return your response as a JSON object with this exact structure:
{{
    "translation": "the translated text",
    "romanization": "romanized version using standard system",
    "romanization_system": "name of romanization system used (e.g., Pinyin, Hepburn, IAST)",
    "source_lang": "{source_lang}",
    "target_lang": "{target_lang}"
}}"""
        else:
            prompt = f"""Translate the following text from {source_lang} to {target_lang}. Return only a clean translation without any formatting.

Text to translate: "{text}"

Return your response as a JSON object with this exact structure:
{{
    "translation": "the translated text",
    "source_lang": "{source_lang}",
    "target_lang": "{target_lang}"
}}"""
        
        logger.info(f"Basic translating: '{text}' from {source_lang} to {target_lang}")
        
        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            # Clean up response text - remove markdown formatting if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            try:
                translation_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: extract translation from plain text
                translation_data = {
                    "translation": response_text,
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }
            
            # Add timestamp
            translation_data['timestamp'] = datetime.now().isoformat()
            
            # Cache the result
            cache_result(translation_cache, cache_key, translation_data)
            
            logger.info(f"Basic translation completed successfully for: {text[:50]}...")
            return jsonify(translation_data)
            
        except Exception as e:
            logger.error(f"Gemini API error in basic translate: {e}")
            return jsonify({
                'error': 'Translation service error',
                'details': 'Please try again later'
            }), 503
            
    except Exception as e:
        logger.error(f"Basic translation error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': 'An unexpected error occurred'
        }), 500

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
QUIZZES_FILE = os.path.join(DATA_DIR, 'quizzes.json')

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
        
        logger.info(f"Getting word of day for language: {language}")
        
        # Use database service to get word of day
        word_data = db_service.get_word_of_day(language)
        
        if not word_data:
            logger.error(f"No words available for language: {language}")
            return jsonify({'error': f'No words available for language: {language}'}), 404
        
        logger.info(f"Successfully retrieved word of day for {language}")
        return jsonify(word_data)
        
    except Exception as e:
        logger.error(f"Error getting word of day: {e}")
        return jsonify({'error': 'Failed to get word of the day'}), 500

@app.route('/api/flashcards', methods=['POST'])
@rate_limit
def create_flashcard():
    """
    Enhanced flashcard creation with comprehensive validation.
    
    Accepts both nested and flat data structures:
    - Nested: {"userId": "...", "flashcard": {...}}
    - Flat: {"userId": "...", "translation": {...}, "difficulty": "..."}
    """
    try:
        if not request.json:
            return jsonify({'error': 'No data provided'}), 400

        user_id = request.json.get('userId')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Support both nested and flat data structures
        flashcard_data = request.json.get('flashcard')
        if not flashcard_data:
            # Try flat structure - extract flashcard data from root level
            flashcard_data = {k: v for k, v in request.json.items() if k != 'userId'}
            
        if not flashcard_data:
            return jsonify({'error': 'Flashcard data required'}), 400

        # Validate required flashcard fields
        translation = flashcard_data.get('translation', {})
        if not translation or not isinstance(translation, dict):
            return jsonify({'error': 'Translation data required'}), 400
            
        required_translation_fields = ['originalText', 'translatedText']
        missing_fields = [field for field in required_translation_fields 
                         if not translation.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing translation fields: {", ".join(missing_fields)}'
            }), 400

        # Use database service to save flashcard
        if db_service.save_flashcard(user_id, flashcard_data):
            return jsonify({'success': True, 'message': 'Flashcard saved successfully'})
        else:
            return jsonify({'error': 'Failed to save flashcard'}), 500

    except Exception as e:
        logger.error(f"Error creating flashcard: {e}")
        return jsonify({'error': 'Failed to create flashcard'}), 500

@app.route('/api/flashcards', methods=['GET'])
@rate_limit
def get_flashcards():
    """Enhanced flashcard retrieval with comprehensive filtering"""
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        language = request.args.get('language')
        
        # Use database service to get flashcards
        flashcards = db_service.get_flashcards(user_id, language)
        
        return jsonify({
            'flashcards': flashcards,
            'total': len(flashcards),
            'language': language
        })

    except Exception as e:
        logger.error(f"Error getting flashcards: {e}")
        return jsonify({'error': 'Failed to get flashcards'}), 500

@app.route('/api/flashcards/<flashcard_id>/review', methods=['POST'])
@rate_limit
def review_flashcard(flashcard_id):
    """Enhanced flashcard review with spaced repetition"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        user_id = data.get('userId')
        correct = data.get('correct', False)
        time_taken = data.get('timeTaken', 0)

        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Use database service to record review
        if db_service.review_flashcard(user_id, flashcard_id, correct, time_taken):
            return jsonify({'success': True, 'message': 'Review recorded successfully'})
        else:
            return jsonify({'error': 'Failed to record review or flashcard not found'}), 404

    except Exception as e:
        logger.error(f"Error reviewing flashcard: {e}")
        return jsonify({'error': 'Failed to review flashcard'}), 500

@app.route('/api/quiz/generate', methods=['POST'])
@rate_limit
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
            
        # Load user progress data
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        user_data = progress.get('users', {}).get(user_id, {'flashcards': []})
        flashcards = user_data.get('flashcards', [])
        
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
            grammar_questions = generate_grammar_questions(language, difficulty, num_grammar)
            questions.extend(grammar_questions)
            
        if quiz_type == 'mixed' or quiz_type == 'conversation':
            # Conversation questions (30% of mixed quiz)
            num_conversation = total_questions if quiz_type == 'conversation' else 3
            conversation_questions = generate_conversation_questions(language, difficulty, num_conversation)
            questions.extend(conversation_questions)
            
        # Shuffle questions and ensure we have enough
        random.shuffle(questions)
        questions = questions[:total_questions]
        
        # If we don't have enough questions, generate basic ones
        while len(questions) < total_questions:
            questions.append(generate_basic_question(language, difficulty))
        
        # Store quiz in user data
        quiz_id = str(uuid.uuid4())
        if 'quizzes' not in user_data:
            user_data['quizzes'] = {}
            
        user_data['quizzes'][quiz_id] = {
            'questions': questions,
            'started_at': datetime.now().isoformat(),
            'completed': False,
            'score': 0,
            'answers': [],
            'current_question': 0
        }
        
        # Save updated user data
        if user_id not in progress['users']:
            progress['users'][user_id] = user_data
        else:
            progress['users'][user_id].update(user_data)
        save_json_file(USER_PROGRESS_FILE, progress)
        
        return jsonify({
            'quiz_id': quiz_id,
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({'error': 'Failed to generate quiz'}), 500

def generate_vocabulary_questions(flashcards, difficulty, count):
    """Generate vocabulary-based questions"""
    questions = []
    
    if not flashcards or len(flashcards) < 4:
        return questions
    
    recent_flashcards = flashcards[:min(50, len(flashcards))]
    
    for _ in range(min(count, len(recent_flashcards))):
        card = random.choice(recent_flashcards)
        question_type = random.choice(['multiple_choice', 'translation'])
        
        if question_type == 'translation':
            questions.append({
                'id': str(uuid.uuid4()),
                'type': 'translation',
                'text': f"Translate: {card['translation']['originalText']}",
                'correct_answer': card['translation']['translatedText'],
                'points': 10,
                'hint': f"This is a {card.get('difficulty', 'beginner')} level word"
            })
        else:  # multiple_choice
            # Generate distractors from other flashcards
            other_cards = [fc for fc in flashcards if fc['id'] != card['id']]
            if len(other_cards) >= 3:
                distractors = random.sample(other_cards, 3)
                options = [d['translation']['translatedText'] for d in distractors]
                options.append(card['translation']['translatedText'])
                random.shuffle(options)
                
                questions.append({
                    'id': str(uuid.uuid4()),
                    'type': 'multiple_choice',
                    'text': f"What is the translation of '{card['translation']['originalText']}'?",
                    'options': options,
                    'correct_answer': card['translation']['translatedText'],
                    'points': 8
                })
            
    return questions

def generate_grammar_questions(language, difficulty, count):
    """Generate grammar-based questions using Gemini AI"""
    questions = []
    
    try:
        for _ in range(count):
            prompt = f"""
            Generate a {difficulty} level grammar question for {language} language learning.
            Return a JSON object with this exact structure:
            {{
                "question": "The grammar question text",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_answer": "the correct option",
                "explanation": "brief explanation of why this is correct"
            }}
            """
            
            response = model.generate_content(prompt)
            try:
                question_data = json.loads(response.text)
                questions.append({
                    'id': str(uuid.uuid4()),
                    'type': 'multiple_choice',
                    'text': question_data['question'],
                    'options': question_data['options'],
                    'correct_answer': question_data['correct_answer'],
                    'explanation': question_data['explanation'],
                    'points': 12
                })
            except json.JSONDecodeError:
                # Fallback to basic question if AI response is invalid
                questions.append(generate_basic_question(language, difficulty))
                
    except Exception as e:
        logger.error(f"Error generating grammar questions: {e}")
        # Generate fallback questions
        for _ in range(count):
            questions.append(generate_basic_question(language, difficulty))
        
    return questions

def generate_conversation_questions(language, difficulty, count):
    """Generate conversation-based questions using Gemini AI"""
    questions = []
    
    try:
        for _ in range(count):
            prompt = f"""
            Generate a {difficulty} level conversation question for {language} language learning.
            Create a realistic scenario and ask how to respond appropriately.
            Return a JSON object with this exact structure:
            {{
                "scenario": "Brief scenario description",
                "question": "The question asking how to respond",
                "options": ["response1", "response2", "response3", "response4"],
                "correct_answer": "the most appropriate response",
                "explanation": "why this response is most appropriate"
            }}
            """
            
            response = model.generate_content(prompt)
            try:
                question_data = json.loads(response.text)
                questions.append({
                    'id': str(uuid.uuid4()),
                    'type': 'conversation',
                    'scenario': question_data['scenario'],
                    'text': question_data['question'],
                    'options': question_data['options'],
                    'correct_answer': question_data['correct_answer'],
                    'explanation': question_data['explanation'],
                    'points': 15
                })
            except json.JSONDecodeError:
                # Fallback to basic question if AI response is invalid
                questions.append(generate_basic_question(language, difficulty))
                
    except Exception as e:
        logger.error(f"Error generating conversation questions: {e}")
        # Generate fallback questions
        for _ in range(count):
            questions.append(generate_basic_question(language, difficulty))
        
    return questions

def generate_basic_question(language, difficulty):
    """Generate a basic fallback question"""
    basic_questions = {
        'en': {
            'beginner': {
                'question': 'Which greeting is most appropriate in formal situations?',
                'options': ['Hey!', 'Hello', 'Yo!', 'What\'s up?'],
                'correct_answer': 'Hello'
            },
            'intermediate': {
                'question': 'Which sentence uses the present perfect correctly?',
                'options': ['I have saw that movie', 'I have seen that movie', 'I has seen that movie', 'I seen that movie'],
                'correct_answer': 'I have seen that movie'
            },
            'advanced': {
                'question': 'Which sentence demonstrates proper use of the subjunctive mood?',
                'options': ['If I was rich, I would travel', 'If I were rich, I would travel', 'If I am rich, I will travel', 'If I will be rich, I would travel'],
                'correct_answer': 'If I were rich, I would travel'
            }
        }
    }
    
    lang_questions = basic_questions.get(language, basic_questions['en'])
    question_data = lang_questions.get(difficulty, lang_questions['beginner'])
    
    return {
        'id': str(uuid.uuid4()),
        'type': 'multiple_choice',
        'text': question_data['question'],
        'options': question_data['options'],
        'correct_answer': question_data['correct_answer'],
        'explanation': 'This is the grammatically correct option.',
        'points': 10
    }

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
    """Enhanced progress tracking with comprehensive analytics"""
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Use database service to get comprehensive progress
        progress_data = db_service.get_user_progress(user_id)
        
        if not progress_data:
            return jsonify({'error': 'No progress data found'}), 404

        return jsonify(progress_data)

    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        return jsonify({'error': 'Failed to get progress data'}), 500

@app.route('/api/user/preferences', methods=['GET', 'POST'])
@rate_limit
def user_preferences():
    """Handle user preferences"""
    try:
        user_id = request.args.get('userId') or (request.json and request.json.get('userId'))
        if not user_id:
            return jsonify({'error': 'UserId parameter required'}), 400
        
        if request.method == 'GET':
            # Use database service to get preferences
            preferences = db_service.get_user_preferences(user_id)
            return jsonify(preferences)
        
        elif request.method == 'POST':
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Use database service to save preferences
            if db_service.save_user_preferences(user_id, data):
                updated_preferences = db_service.get_user_preferences(user_id)
                return jsonify({
                    'success': True,
                    'preferences': updated_preferences
                })
            else:
                return jsonify({'error': 'Failed to save preferences'}), 500
            
    except Exception as e:
        logger.error(f"User preferences error: {e}")
        return jsonify({'error': 'Failed to handle preferences'}), 500

@app.route('/api/analytics', methods=['POST'])
@rate_limit
def record_analytics():
    """Record user analytics for learning insights"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = data.get('userId')
        event_type = data.get('eventType')
        event_data = data.get('eventData', {})
        
        if not all([user_id, event_type]):
            return jsonify({'error': 'Missing required parameters: userId, eventType'}), 400
        
        # Prepare analytics event
        analytics_event = {
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data,
            'session_id': data.get('sessionId'),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        }
        
        # Use database service to track event
        if db_service.track_event(analytics_event):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to record analytics'}), 500
        
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
        Act as a helpful language tutor having a conversation in {language}. 
        The user's proficiency level is {proficiency}.
        Context: {context}
        
        User said: "{user_input}"
        
        Respond naturally in {language} and provide a JSON response with these exact keys:
        {{
            "response": "Your natural response in {language}",
            "translation": "English translation of your response",
            "vocabulary": ["key", "vocabulary", "words"],
            "grammar_notes": "Brief grammar explanation",
            "cultural_note": "Cultural context if relevant",
            "suggested_responses": ["suggestion1", "suggestion2", "suggestion3"]
        }}
        
        Keep responses appropriate for {proficiency} level learners.
        """

        # Generate response using Gemini
        response = model.generate_content(conversation_prompt)
        
        try:
            # Try to parse the JSON response
            conversation_data = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            conversation_data = {
                "response": "I understand. Can you tell me more?",
                "translation": "I understand. Can you tell me more?",
                "vocabulary": ["understand", "tell", "more"],
                "grammar_notes": "Simple present tense",
                "cultural_note": "This is a friendly way to continue conversation",
                "suggested_responses": ["Yes, I can explain more", "What would you like to know?", "That's interesting"]
            }
        
        # Track user progress
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
        
        # Add conversation to practice sessions
        practice_session = {
            'timestamp': datetime.now().isoformat(),
            'type': 'conversation',
            'user_input': user_input,
            'ai_response': conversation_data['response'],
            'language': language,
            'context': context,
            'proficiency': proficiency,
            'duration': 60,  # Estimate 1 minute per exchange
            'performance': 0.8  # Default performance score
        }
        
        user_data['practice_sessions'].append(practice_session)
        
        # Update learning stats
        user_data['learning_stats']['last_study_date'] = datetime.now().isoformat()
        
        save_json_file(USER_PROGRESS_FILE, progress)
        
        return jsonify({
            'ai_response': conversation_data['response'],
            'translation': conversation_data['translation'],
            'vocabulary': conversation_data['vocabulary'],
            'grammar_notes': conversation_data['grammar_notes'],
            'cultural_note': conversation_data['cultural_note'],
            'suggested_responses': conversation_data['suggested_responses'],
            'stats': {
                'total_conversations': len(user_data['practice_sessions']),
                'session_count': len([s for s in user_data['practice_sessions'] if s['type'] == 'conversation'])
            }
        })
        
    except Exception as e:
        logger.error(f"Error in conversation practice: {e}")
        return jsonify({'error': 'Failed to generate conversation response'}), 500

@app.route('/api/quizzes', methods=['GET'])
@rate_limit
def get_quizzes():
    """Get available quizzes for a language and difficulty level"""
    try:
        language = request.args.get('language')
        difficulty = request.args.get('difficulty', 'beginner')
        
        if not language:
            return jsonify({'error': 'Language parameter required'}), 400
            
        quizzes_data = load_json_file(QUIZZES_FILE, {'quizzes': {}})
        
        if language not in quizzes_data.get('quizzes', {}):
            return jsonify({'error': f'No quizzes available for language {language}'}), 404
            
        if difficulty not in quizzes_data['quizzes'][language]:
            return jsonify({'error': f'No quizzes available for difficulty {difficulty}'}), 404
            
        quizzes = quizzes_data['quizzes'][language][difficulty]
        
        # Add metadata
        response = {
            'quizzes': quizzes,
            'total_quizzes': len(quizzes),
            'difficulty': difficulty,
            'language': language,
            'categories': quizzes_data.get('categories', []),
            'available_difficulties': quizzes_data.get('difficulties', [])
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error fetching quizzes: {e}")
        return jsonify({'error': 'Failed to fetch quizzes'}), 500

@app.route('/api/quiz/<quiz_id>', methods=['GET'])
@rate_limit
def get_quiz(quiz_id):
    """Get a specific quiz by ID"""
    try:
        language = request.args.get('language')
        if not language:
            return jsonify({'error': 'Language parameter required'}), 400
            
        quizzes_data = load_json_file(QUIZZES_FILE, {'quizzes': {}})
        
        # Search for quiz in all difficulty levels
        quiz = None
        if language in quizzes_data.get('quizzes', {}):
            for difficulty in quizzes_data['quizzes'][language]:
                for q in quizzes_data['quizzes'][language][difficulty]:
                    if q['id'] == quiz_id:
                        quiz = q
                        break
                if quiz:
                    break
        
        if not quiz:
            return jsonify({'error': f'Quiz {quiz_id} not found'}), 404
            
        return jsonify(quiz)
        
    except Exception as e:
        logger.error(f"Error fetching quiz {quiz_id}: {e}")
        return jsonify({'error': f'Failed to fetch quiz {quiz_id}'}), 500

@app.route('/api/quiz/submit', methods=['POST'])
@rate_limit
def submit_quiz():
    """Submit quiz answers and get results"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        user_id = data.get('user_id')
        answers = data.get('answers', {})
        
        if not all([quiz_id, user_id, answers]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get quiz data
        quizzes_data = load_json_file(QUIZZES_FILE, {'quizzes': {}})
        quiz = None
        language = None
        difficulty = None
        
        # Find the quiz
        for lang in quizzes_data.get('quizzes', {}):
            for diff in quizzes_data['quizzes'][lang]:
                for q in quizzes_data['quizzes'][lang][diff]:
                    if q['id'] == quiz_id:
                        quiz = q
                        language = lang
                        difficulty = diff
                        break
                if quiz:
                    break
            if quiz:
                break
                
        if not quiz:
            return jsonify({'error': f'Quiz {quiz_id} not found'}), 404
            
        # Calculate results
        total_questions = len(quiz['questions'])
        correct_answers = 0
        question_results = []
        
        for i, question in enumerate(quiz['questions']):
            user_answer = answers.get(str(i))
            is_correct = user_answer == question['correct_answer']
            if is_correct:
                correct_answers += 1
                
            question_results.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
            
        score = (correct_answers / total_questions) * 100
        
        # Update user progress
        progress_data = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        if user_id not in progress_data['users']:
            progress_data['users'][user_id] = {'quiz_scores': []}
            
        quiz_result = {
            'timestamp': datetime.now().isoformat(),
            'quiz_id': quiz_id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'difficulty': difficulty,
            'language': language
        }
        
        progress_data['users'][user_id]['quiz_scores'].append(quiz_result)
        save_json_file(USER_PROGRESS_FILE, progress_data)
        
        # Prepare response
        response = {
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'question_results': question_results,
            'quiz_id': quiz_id,
            'difficulty': difficulty,
            'language': language
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        return jsonify({'error': 'Failed to submit quiz'}), 500

# Initialize data directory and files on startup
def initialize_data_files():
    """Initialize data directory and create default files if they don't exist"""
    logger.info("Initializing database...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created successfully")
    
    # Try to run migration but don't fail if it doesn't work
    try:
        logger.info("Attempting database migration...")
        import subprocess
        import sys
        result = subprocess.run([sys.executable, 'migrate_to_sqlite.py'], 
                              capture_output=True, text=True, timeout=30,
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            logger.info("Database migration completed successfully")
        else:
            logger.warning(f"Migration completed with warnings: {result.stderr}")
    except Exception as e:
        logger.warning(f"Migration script not found or failed, continuing without it: {e}")
    
    # Always ensure we have basic word-of-day data
    try:
        logger.info("Checking word-of-day data...")
        word_data = db_service.get_word_of_day('en')
        if not word_data:
            logger.info("No word data found for 'en', creating default entries...")
            # Add comprehensive default words for English
            default_words = [
                {
                    'word': 'hello',
                    'translation': 'a greeting or expression of goodwill',
                    'pronunciation': 'həˈloʊ',
                    'part_of_speech': 'interjection',
                    'difficulty': 'beginner',
                    'example_sentence': 'Hello, how are you?',
                    'example_translation': 'A common greeting used when meeting someone.',
                    'etymology': 'From Old English hæl (whole, healthy)',
                    'related_words': ['hi', 'greetings', 'salutation'],
                    'cultural_note': 'The most common greeting in English-speaking countries.'
                },
                {
                    'word': 'thank you',
                    'translation': 'expression of gratitude',
                    'pronunciation': 'θæŋk juː',
                    'part_of_speech': 'phrase',
                    'difficulty': 'beginner',
                    'example_sentence': 'Thank you for your help.',
                    'example_translation': 'Used to express appreciation.',
                    'etymology': 'From Old English þancian (to give thanks)',
                    'related_words': ['thanks', 'gratitude', 'appreciation'],
                    'cultural_note': 'Essential politeness expression in English.'
                },
                {
                    'word': 'wonderful',
                    'translation': 'inspiring delight, pleasure, or admiration; extremely good',
                    'pronunciation': 'ˈwʌn.də.fəl',
                    'part_of_speech': 'adjective',
                    'difficulty': 'intermediate',
                    'example_sentence': 'What a wonderful day!',
                    'example_translation': 'Used to express that something is very good or pleasant.',
                    'etymology': 'From wonder + -ful',
                    'related_words': ['amazing', 'fantastic', 'marvelous'],
                    'cultural_note': 'Often used to express enthusiasm and positivity.'
                },
                {
                    'word': 'serendipity',
                    'translation': 'the occurrence of events by chance in a happy way',
                    'pronunciation': 'ˌser.ənˈdɪp.ə.ti',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'It was pure serendipity that we met at the coffee shop.',
                    'example_translation': 'Describes pleasant surprises or fortunate accidents.',
                    'etymology': 'Coined by Horace Walpole in 1754',
                    'related_words': ['chance', 'fortune', 'luck'],
                    'cultural_note': 'A beloved word expressing life\'s pleasant surprises.'
                }
            ]
            
            for word_data in default_words:
                success = db_service.add_word_of_day('en', word_data)
                if success:
                    logger.info(f"Added word: {word_data['word']}")
                else:
                    logger.warning(f"Failed to add word: {word_data['word']}")
            
            # Verify words were added
            final_check = db_service.get_word_of_day('en')
            if final_check:
                logger.info("✅ Word-of-day data successfully created")
            else:
                logger.error("❌ Failed to create word-of-day data")
        else:
            logger.info(f"✅ Word-of-day data exists: {word_data.get('word', 'Unknown')}")
            
        # Check for other languages too
        for lang in ['es', 'fr', 'de', 'it', 'pt']:
            lang_word = db_service.get_word_of_day(lang)
            if not lang_word:
                logger.info(f"Adding basic word for {lang}...")
                basic_word = {
                    'word': 'hello' if lang == 'es' else 'bonjour' if lang == 'fr' else 'hallo' if lang == 'de' else 'ciao' if lang == 'it' else 'olá',
                    'translation': 'greeting',
                    'pronunciation': '',
                    'part_of_speech': 'interjection',
                    'difficulty': 'beginner',
                    'example_sentence': '',
                    'example_translation': '',
                    'etymology': '',
                    'related_words': [],
                    'cultural_note': 'Basic greeting'
                }
                db_service.add_word_of_day(lang, basic_word)
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Don't fail startup, just log the error

if __name__ == '__main__':
    try:
        logger.info("Starting TTSAI Backend Server...")
        
        # Initialize database
        initialize_data_files()
        
        # Get port from environment variable for production
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(f"Server starting on port {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
        raise 