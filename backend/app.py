from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import google.cloud.texttospeech as tts
import google.cloud.speech as speech
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
import requests
from google.auth import default
from fuzzywuzzy import fuzz
import re
import google.generativeai as genai

# Import centralized configuration
from config import get_llm_config, get_model_name, LLM_PROVIDER, GEMINI_API_KEY

# Configure comprehensive logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import database service
try:
    from models import create_tables
    from db_service import db_service
    logger.info("Successfully imported models and db_service")
except ImportError as e:
    logger.error(f"Failed to import models or db_service: {e}")
    logger.error("Current working directory and Python path:")
    import sys
    import os
    logger.error(f"Current directory: {os.getcwd()}")
    logger.error(f"Python path: {sys.path}")
    logger.error(f"Files in current directory: {os.listdir('.')}")
    raise

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

# Configure LLM API using centralized configuration
llm_config = get_llm_config()
model_name = get_model_name()
gemini_model = None

if not llm_config["api_key"]:
    logger.warning("LLM API key not found in environment variables")
    logger.warning("Translation services will be limited. Set GEMINI_API_KEY for full functionality.")
    gemini_model = None
else:
    try:
        if llm_config["provider"] == "google_ai_studio":
            logger.info(f"Configuring Google AI Studio with model: {model_name}")
            logger.info(f"API key: {llm_config['api_key'][:8]}...{llm_config['api_key'][-4:]}")
            
            # Configure the Google Generative AI library
            genai.configure(api_key=llm_config["api_key"])
            
            # Initialize the model
            gemini_model = genai.GenerativeModel(model_name)
            
            # Test connection
            test_response = gemini_model.generate_content("Test connection")
            logger.info("Gemini connection test successful")
            
        else:
            # Legacy OpenRouter support (fallback)
            logger.info(f"Using legacy OpenRouter with model: {model_name}")
            logger.info(f"API key: {llm_config['api_key'][:8]}...{llm_config['api_key'][-4:]}")
            
            # Test OpenRouter connection
            headers = {
                "Authorization": f"Bearer {llm_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Test connection"}]
            }
            
            test_response = requests.post(
                llm_config["base_url"],
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if test_response.status_code == 200:
                logger.info(f"OpenRouter connection test successful for {model_name}")
                gemini_model = "openrouter"  # Flag for OpenRouter usage
            else:
                logger.error(f"OpenRouter connection test failed: {test_response.status_code}")
                gemini_model = None
            
    except Exception as e:
        logger.error(f"Failed to configure LLM: {e}")
        gemini_model = None

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

# LLM API helper function
def call_llm_api(prompt, model=None, max_tokens=None):
    """Make a call to the configured LLM API"""
    llm_config = get_llm_config()
    
    if not gemini_model or not llm_config["api_key"]:
        raise Exception("LLM API not configured")
    
    try:
        if llm_config["provider"] == "google_ai_studio" and isinstance(gemini_model, genai.GenerativeModel):
            # Use Google AI Studio API directly
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens or llm_config["max_tokens"],
                temperature=llm_config["temperature"]
            )
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text.strip()
            else:
                raise Exception("Empty response from Gemini API")
                
        else:
            # OpenRouter fallback
            model = model or llm_config["model"]
            max_tokens = max_tokens or llm_config["max_tokens"]
            
            headers = {
                "Authorization": f"Bearer {llm_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": llm_config["temperature"]
            }
            
            response = requests.post(
                llm_config["base_url"],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"OpenRouter API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        raise Exception("LLM API timeout")
    except requests.exceptions.RequestException as e:
        raise Exception(f"LLM API request failed: {e}")
    except Exception as e:
        raise Exception(f"LLM API error: {e}")

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
@rate_limit
def health_check():
    """Health check endpoint with detailed service status"""
    try:
        service_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'gemini': bool(gemini_model),
                'speech_client': bool(speech_client),
                'tts_client': bool(tts_client)
            }
        }
        return jsonify(service_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/supported-languages', methods=['GET'])
@rate_limit
def get_supported_languages():
    """Get list of supported languages with their capabilities"""
    try:
        # Define supported languages with their capabilities
        supported_languages = [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "es", 
                "name": "Spanish",
                "native_name": "Español",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "fr",
                "name": "French", 
                "native_name": "Français",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "de",
                "name": "German",
                "native_name": "Deutsch", 
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "it",
                "name": "Italian",
                "native_name": "Italiano",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "pt",
                "name": "Portuguese",
                "native_name": "Português",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "ru",
                "name": "Russian",
                "native_name": "Русский",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "ja",
                "name": "Japanese",
                "native_name": "日本語",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "ko",
                "name": "Korean", 
                "native_name": "한국어",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "zh",
                "name": "Chinese (Simplified)",
                "native_name": "简体中文",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "zh-TW",
                "name": "Chinese (Traditional)", 
                "native_name": "繁體中文",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "ar",
                "name": "Arabic",
                "native_name": "العربية",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "hi",
                "name": "Hindi",
                "native_name": "हिन्दी", 
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "th",
                "name": "Thai",
                "native_name": "ไทย",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "vi",
                "name": "Vietnamese",
                "native_name": "Tiếng Việt",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "nl",
                "name": "Dutch",
                "native_name": "Nederlands",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "pl",
                "name": "Polish",
                "native_name": "Polski",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "tr",
                "name": "Turkish",
                "native_name": "Türkçe",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "sv",
                "name": "Swedish",
                "native_name": "Svenska",
                "tts_supported": True,
                "speech_recognition_supported": True
            },
            {
                "code": "da",
                "name": "Danish",
                "native_name": "Dansk",
                "tts_supported": True,
                "speech_recognition_supported": True
            }
        ]
        
        return jsonify({
            "languages": supported_languages,
            "total_languages": len(supported_languages),
            "tts_supported_count": sum(1 for lang in supported_languages if lang["tts_supported"]),
            "speech_recognition_supported_count": sum(1 for lang in supported_languages if lang["speech_recognition_supported"])
        })
        
    except Exception as e:
        logger.error(f"Error fetching supported languages: {e}")
        return jsonify({'error': 'Failed to fetch supported languages'}), 500

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
        
        if not gemini_model:
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
            response_text = call_llm_api(prompt)
            if not response_text:
                raise Exception("Empty response from LLM API")
            
            # Clean up response text - remove markdown formatting if present
            response_text = response_text.strip()
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
        
        if not gemini_model:
            return jsonify({'error': 'Translation service temporarily unavailable'}), 503
        
        # Generate prompt and get translation
        prompt = get_advanced_translation_prompt(
            text, source_lang, target_lang, formality, dialect, context
        )
        
        logger.info(f"Translating: '{text}' from {source_lang} to {target_lang}")
        
        try:
            response_text = call_llm_api(prompt)
            if not response_text:
                raise Exception("Empty response from LLM API")
                
            # Parse JSON response
            translation_data = json.loads(response_text)
            
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
            logger.error(f"JSON decode error: {e}. Response: {response_text[:200]}")
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

@app.route('/api/text-to-speech', methods=['POST'])
@rate_limit
def text_to_speech():
    """Enhanced Text-to-Speech endpoint with multiple language support"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Validate required fields
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        voice_gender = data.get('voiceGender', 'NEUTRAL')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        if len(text) > 500:
            return jsonify({'error': 'Text too long (max 500 characters)'}), 400
        
        # Check cache first
        cache_key = get_cache_key({
            'text': text, 'language': language, 'voice_gender': voice_gender
        })
        
        cached_result = get_cached_result(tts_cache, cache_key)
        if cached_result:
            logger.info(f"Returning cached TTS for: {text[:30]}...")
            return jsonify(cached_result)
        
        # Try Google Cloud TTS first
        if tts_client:
            try:
                # Map language codes to Google TTS format
                lang_mapping = {
                    'en': 'en-US',
                    'es': 'es-ES', 
                    'fr': 'fr-FR',
                    'de': 'de-DE',
                    'it': 'it-IT',
                    'pt': 'pt-BR',
                    'ja': 'ja-JP',
                    'ko': 'ko-KR',
                    'zh': 'zh-CN',
                    'zh-CN': 'zh-CN',
                    'zh-TW': 'zh-TW',
                    'ru': 'ru-RU',
                    'ar': 'ar-XA',
                    'hi': 'hi-IN',
                    'th': 'th-TH',
                    'vi': 'vi-VN',
                    'nl': 'nl-NL',
                    'pl': 'pl-PL',
                    'tr': 'tr-TR',
                    'sv': 'sv-SE',
                    'da': 'da-DK'
                }
                
                google_lang = lang_mapping.get(language, 'en-US')
                
                # Configure voice
                voice_gender_mapping = {
                    'MALE': tts.SsmlVoiceGender.MALE,
                    'FEMALE': tts.SsmlVoiceGender.FEMALE,
                    'NEUTRAL': tts.SsmlVoiceGender.NEUTRAL
                }
                
                voice = tts.VoiceSelectionParams(
                    language_code=google_lang,
                    ssml_gender=voice_gender_mapping.get(voice_gender.upper(), tts.SsmlVoiceGender.NEUTRAL)
                )
                
                # Configure audio
                audio_config = tts.AudioConfig(
                    audio_encoding=tts.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0
                )
                
                # Synthesize speech
                synthesis_input = tts.SynthesisInput(text=text)
                response = tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Encode audio to base64
                audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
                
                result = {
                    'audio': audio_base64,
                    'format': 'mp3',
                    'text': text,
                    'language': language,
                    'voice_gender': voice_gender,
                    'provider': 'google_cloud_tts',
                    'success': True
                }
                
                # Cache the result
                cache_result(tts_cache, cache_key, result)
                
                logger.info(f"TTS synthesis completed for: {text[:30]}...")
                return jsonify(result)
                
            except Exception as e:
                logger.warning(f"Google Cloud TTS failed: {e}")
                # Continue to fallback
        
        # Fallback: Return error if Google TTS fails
        logger.error("TTS service temporarily unavailable")
        return jsonify({
            'error': 'Text-to-speech service temporarily unavailable',
            'details': 'Please try again later or check your internet connection',
            'text': text,
            'language': language,
            'success': False
        }), 503
        
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        return jsonify({
            'error': 'Text-to-speech failed',
            'details': 'An unexpected error occurred',
            'success': False
                 }), 500

@app.route('/api/speech-to-text', methods=['POST'])
@rate_limit
def speech_to_text():
    """Enhanced Speech-to-Text endpoint for audio transcription"""
    try:
        # Check if audio data is provided
        if 'audio' not in request.files and 'audioData' not in request.form:
            return jsonify({'error': 'No audio data provided'}), 400
        
        language = request.form.get('language', 'en')
        
        # Get audio data (either from file upload or base64 data)
        audio_data = None
        if 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
        elif 'audioData' in request.form:
            try:
                # Decode base64 audio data
                audio_base64 = request.form.get('audioData')
                if audio_base64.startswith('data:audio'):
                    # Remove data URL prefix
                    audio_base64 = audio_base64.split(',')[1]
                audio_data = base64.b64decode(audio_base64)
            except Exception as e:
                return jsonify({'error': f'Invalid audio data format: {e}'}), 400
        
        if not audio_data:
            return jsonify({'error': 'No valid audio data found'}), 400
        
        # Try Google Cloud Speech-to-Text
        if speech_client:
            try:
                # Map language codes to Google Speech format
                lang_mapping = {
                    'en': 'en-US',
                    'es': 'es-ES',
                    'fr': 'fr-FR',
                    'de': 'de-DE',
                    'it': 'it-IT',
                    'pt': 'pt-BR',
                    'ja': 'ja-JP',
                    'ko': 'ko-KR',
                    'zh': 'zh-CN',
                    'zh-CN': 'zh-CN',
                    'zh-TW': 'zh-TW',
                    'ru': 'ru-RU',
                    'ar': 'ar-SA',
                    'hi': 'hi-IN',
                    'th': 'th-TH',
                    'vi': 'vi-VN',
                    'nl': 'nl-NL',
                    'pl': 'pl-PL',
                    'tr': 'tr-TR',
                    'sv': 'sv-SE',
                    'da': 'da-DK'
                }
                
                google_lang = lang_mapping.get(language, 'en-US')
                
                # Configure recognition
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                    sample_rate_hertz=48000,
                    language_code=google_lang,
                    enable_automatic_punctuation=True,
                    model='latest_long'
                )
                
                # Create audio object
                audio = speech.RecognitionAudio(content=audio_data)
                
                # Perform recognition
                response = speech_client.recognize(config=config, audio=audio)
                
                # Extract transcript
                transcript = ""
                confidence = 0.0
                
                for result in response.results:
                    transcript += result.alternatives[0].transcript + " "
                    confidence = max(confidence, result.alternatives[0].confidence)
                
                transcript = transcript.strip()
                
                if not transcript:
                    return jsonify({
                        'error': 'No speech detected in audio',
                        'transcript': '',
                        'confidence': 0.0,
                        'language': language,
                        'success': False
                    }), 400
                
                result = {
                    'transcript': transcript,
                    'confidence': confidence,
                    'language': language,
                    'provider': 'google_cloud_speech',
                    'success': True
                }
                
                logger.info(f"STT transcription completed: {transcript[:50]}...")
                return jsonify(result)
                
            except Exception as e:
                logger.warning(f"Google Cloud Speech-to-Text failed: {e}")
                # Continue to fallback
        
        # Fallback: Return error if Google Speech fails
        logger.error("Speech-to-text service temporarily unavailable")
        return jsonify({
            'error': 'Speech-to-text service temporarily unavailable',
            'details': 'Please try again later or check your internet connection',
            'language': language,
            'success': False
        }), 503
        
    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        return jsonify({
            'error': 'Speech-to-text failed',
            'details': 'An unexpected error occurred',
            'success': False
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
    """Get a random word of the day for the specified language"""
    try:
        language = request.args.get('language', 'en').lower()
        logger.info(f"Getting word of day for language: {language}")
        
        # Check if we have any words for this language
        word_data = db_service.get_word_of_day(language)
        
        if not word_data:
            logger.warning(f"No word-of-day data found for language: {language}")
            
            # Try to populate some default data if language is 'en'
            if language == 'en':
                logger.info("Attempting to populate default English words...")
                
                default_word = {
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
                }
                
                success = db_service.add_word_of_day('en', default_word)
                if success:
                    logger.info("Successfully added default English word")
                    # Try to get it again
                    word_data = db_service.get_word_of_day(language)
                else:
                    logger.error("Failed to add default English word")
            
            # If still no data, return error with more details
            if not word_data:
                return jsonify({
                    'error': f'Language {language} not supported',
                    'available_languages': ['en'],  # We know we should have at least English
                    'debug_info': {
                        'attempted_language': language,
                        'database_initialized': True,
                        'fallback_attempted': language == 'en'
                    }
                }), 404
        
        logger.info(f"Successfully retrieved word of day: {word_data.get('word', 'Unknown')}")
        return jsonify(word_data)
        
    except Exception as e:
        logger.error(f"Error getting word of day: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'debug_info': str(e)
        }), 500

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
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        
        # Use database service to get flashcards with filters
        flashcards = db_service.get_flashcards(user_id, language, difficulty, category)
        
        return jsonify({
            'flashcards': flashcards,
            'total': len(flashcards),
            'language': language,
            'filters': {
                'difficulty': difficulty,
                'category': category
            }
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
    """Generate grammar-based questions using LLM API"""
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
            
            response_text = call_llm_api(prompt)
            try:
                question_data = json.loads(response_text)
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
    """Generate conversation-based questions using LLM API"""
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
            
            response_text = call_llm_api(prompt)
            try:
                question_data = json.loads(response_text)
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

@app.route('/api/progress/summary', methods=['GET'])
@rate_limit
def get_progress_summary():
    """Provide high-level progress data for the Learning Hub dashboard"""
    try:
        user_id = request.args.get('userId')
        language = request.args.get('language')
        time_range = request.args.get('timeRange', 'all')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        logger.info(f"Fetching progress summary for user {user_id}, language {language}, timeRange {time_range}")
        
        # Use database service to get comprehensive progress summary
        progress_summary = db_service.get_user_progress_summary(user_id, time_range)
        
        if not progress_summary:
            # Return default progress summary for new users
            progress_summary = {
                'total_xp': 0,
                'current_streak': 0,
                'words_learned': 0,
                'level': 1,
                'quizzes_completed': 0,
                'flashcard_stats': {
                    'total': 0,
                    'due_for_review': 0,
                    'mastered': 0,
                    'avg_success_rate': 0.0
                },
                'quiz_stats': {
                    'completed': 0,
                    'avg_score': 0.0
                },
                'conversation_stats': {
                    'total': 0,
                    'avg_duration': 0,
                    'last_topic': None
                }
            }
        
        return jsonify(progress_summary)
        
    except Exception as e:
        logger.error(f"Error getting progress summary: {e}")
        return jsonify({'error': 'Failed to get progress summary'}), 500

@app.route('/api/word-explorer/get-word', methods=['GET'])
@rate_limit
def get_word_for_explorer():
    """Fetch a detailed word for WordExplorer, supporting filters/search"""
    try:
        language = request.args.get('language')
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        search_term = request.args.get('searchTerm')
        
        if not language:
            return jsonify({'error': 'Language parameter required'}), 400
        
        logger.info(f"Fetching word for language {language}, difficulty {difficulty}, category {category}, search {search_term}")
        
        # Use database service to get detailed word
        word_data = db_service.get_detailed_word(language, difficulty, category, search_term)
        
        if not word_data:
            return jsonify({'error': 'No words found matching criteria'}), 404
        
        return jsonify(word_data)
        
    except Exception as e:
        logger.error(f"Error getting word for explorer: {e}")
        return jsonify({'error': 'Failed to get word'}), 500

@app.route('/api/flashcards/<flashcard_id>', methods=['DELETE'])
@rate_limit
def delete_flashcard_endpoint(flashcard_id):
    """Delete a specific flashcard"""
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        if not flashcard_id:
            return jsonify({'error': 'Flashcard ID required'}), 400
        
        logger.info(f"Deleting flashcard {flashcard_id} for user {user_id}")
        
        # Use database service to delete flashcard
        success = db_service.delete_flashcard(user_id, flashcard_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Flashcard not found or not authorized'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting flashcard: {e}")
        return jsonify({'error': 'Failed to delete flashcard'}), 500

@app.route('/api/progress/comprehensive', methods=['GET'])
@rate_limit
def get_comprehensive_progress():
    """Get comprehensive progress data for ProgressTracker component"""
    try:
        user_id = request.args.get('userId')
        language = request.args.get('language')
        time_range = request.args.get('timeRange', 'all')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        logger.info(f"Fetching comprehensive progress for user {user_id}, language {language}, timeRange {time_range}")
        
        # Use database service to get comprehensive progress data
        progress_data = db_service.get_comprehensive_progress(user_id, time_range, language)
        
        if not progress_data:
            # Return default structure for new users
            progress_data = {
                'total_xp': 0,
                'current_streak': 0,
                'words_learned': 0,
                'level': 1,
                'flashcard_stats': {
                    'total': 0,
                    'due_for_review': 0,
                    'mastered': 0,
                    'avg_success_rate': 0.0
                },
                'quiz_stats': {
                    'completed': 0,
                    'avg_score': 0.0
                },
                'conversation_stats': {
                    'total': 0,
                    'avg_duration': 0,
                    'last_topic': None
                },
                'daily_goal': 10,
                'activity_data': [],
                'recent_achievements': []
            }
        
        return jsonify(progress_data)
        
    except Exception as e:
        logger.error(f"Error getting comprehensive progress: {e}")
        return jsonify({'error': 'Failed to get comprehensive progress'}), 500

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

# AI Avatar system configuration
AVATAR_DATA = {
    'en': [
        {
            'id': 'emma_teacher',
            'name': 'Emma',
            'role': 'English Teacher',
            'personality': 'Friendly, patient, encouraging',
            'specialties': ['grammar', 'pronunciation', 'business_english'],
            'avatar_image': '👩‍🏫',
            'background': 'Experienced English teacher from London with 10 years of teaching experience',
            'greeting': 'Hello! I\'m Emma, your English tutor. I\'m here to help you improve your English skills!',
            'style': 'supportive and detailed explanations'
        },
        {
            'id': 'mike_native',
            'name': 'Mike',
            'role': 'Native Speaker',
            'personality': 'Casual, humorous, authentic',
            'specialties': ['slang', 'idioms', 'casual_conversation'],
            'avatar_image': '👨‍💼',
            'background': 'American native speaker who loves helping people learn everyday English',
            'greeting': 'Hey there! I\'m Mike. Let\'s chat and make your English sound more natural!',
            'style': 'conversational and relaxed'
        },
        {
            'id': 'sophia_academic',
            'name': 'Dr. Sophia',
            'role': 'Academic English Expert',
            'personality': 'Professional, thorough, articulate',
            'specialties': ['academic_writing', 'formal_english', 'advanced_grammar'],
            'avatar_image': '👩‍🎓',
            'background': 'PhD in Linguistics, specializes in academic and formal English',
            'greeting': 'Good day! I\'m Dr. Sophia. I specialize in academic and formal English communication.',
            'style': 'formal and comprehensive'
        }
    ],
    'es': [
        {
            'id': 'carlos_maestro',
            'name': 'Carlos',
            'role': 'Profesor de Español',
            'personality': 'Entusiasta, paciente, cultural',
            'specialties': ['gramática', 'cultura', 'español_mexicano'],
            'avatar_image': '👨‍🏫',
            'background': 'Profesor de español de México con experiencia en enseñanza intercultural',
            'greeting': '¡Hola! Soy Carlos, tu profesor de español. ¡Vamos a aprender juntos!',
            'style': 'warm and culturally rich'
        },
        {
            'id': 'maria_nativa',
            'name': 'María',
            'role': 'Hablante Nativa',
            'personality': 'Amigable, expresiva, auténtica',
            'specialties': ['conversación', 'expresiones', 'español_cotidiano'],
            'avatar_image': '👩‍💃',
            'background': 'Española nativa que disfruta compartiendo su idioma y cultura',
            'greeting': '¡Hola, qué tal! Soy María. ¡Hablemos en español como lo hacemos en España!',
            'style': 'animated and authentic'
        },
        {
            'id': 'alejandro_formal',
            'name': 'Dr. Alejandro',
            'role': 'Especialista en Español Formal',
            'personality': 'Profesional, detallado, erudito',
            'specialties': ['español_formal', 'literatura', 'escritura_académica'],
            'avatar_image': '👨‍🎓',
            'background': 'Doctor en Filología Hispánica, experto en español formal y académico',
            'greeting': 'Buenos días. Soy el Dr. Alejandro, especialista en español formal y académico.',
            'style': 'formal and scholarly'
        }
    ],
    'fr': [
        {
            'id': 'claire_professeur',
            'name': 'Claire',
            'role': 'Professeure de Français',
            'personality': 'Élégante, patiente, raffinée',
            'specialties': ['grammaire', 'prononciation', 'culture_française'],
            'avatar_image': '👩‍🏫',
            'background': 'Professeure parisienne avec une passion pour la langue française',
            'greeting': 'Bonjour! Je suis Claire, votre professeure de français. Enchanté de vous rencontrer!',
            'style': 'elegant and precise'
        },
        {
            'id': 'pierre_parisien',
            'name': 'Pierre',
            'role': 'Parisien Authentique',
            'personality': 'Charmant, spirituel, authentique',
            'specialties': ['français_familier', 'argot', 'vie_parisienne'],
            'avatar_image': '👨‍🎨',
            'background': 'Parisien de naissance qui adore partager sa culture',
            'greeting': 'Salut! Moi c\'est Pierre. On va apprendre le français comme un vrai Parisien!',
            'style': 'charming and witty'
        }
    ],
    'de': [
        {
            'id': 'hans_lehrer',
            'name': 'Hans',
            'role': 'Deutschlehrer',
            'personality': 'Strukturiert, geduldig, thorough',
            'specialties': ['grammatik', 'deutsche_kultur', 'hochdeutsch'],
            'avatar_image': '👨‍🏫',
            'background': 'Erfahrener Deutschlehrer aus Berlin',
            'greeting': 'Guten Tag! Ich bin Hans, Ihr Deutschlehrer. Freut mich, Sie kennenzulernen!',
            'style': 'systematic and thorough'
        },
        {
            'id': 'greta_berlin',
            'name': 'Greta',
            'role': 'Berlinerin',
            'personality': 'Cool, direkt, modern',
            'specialties': ['umgangssprache', 'berliner_dialekt', 'jugendsprache'],
            'avatar_image': '👩‍🎤',
            'background': 'Echte Berlinerin mit moderner Sicht auf die deutsche Sprache',
            'greeting': 'Hallo! Ich bin Greta aus Berlin. Lass uns Deutsch lernen, wie es wirklich gesprochen wird!',
            'style': 'modern and direct'
        }
    ],
    'ja': [
        {
            'id': 'yuki_sensei',
            'name': 'Yuki',
            'role': '日本語の先生',
            'personality': 'Polite, patient, traditional',
            'specialties': ['keigo', 'kanji', 'japanese_culture'],
            'avatar_image': '👩‍🏫',
            'background': 'Traditional Japanese teacher with deep cultural knowledge',
            'greeting': 'こんにちは！私はゆきです。日本語と日本の文化を教えます。',
            'style': 'polite and traditional'
        },
        {
            'id': 'takeshi_tokyo',
            'name': 'Takeshi',
            'role': '東京人',
            'personality': 'Modern, friendly, tech-savvy',
            'specialties': ['casual_japanese', 'modern_slang', 'tokyo_life'],
            'avatar_image': '👨‍💻',
            'background': 'Young Tokyo professional who loves sharing modern Japanese',
            'greeting': 'こんにちは！たけしです。現代の日本語を一緒に学びましょう！',
            'style': 'modern and casual'
        }
    ],
    'zh': [
        {
            'id': 'mei_laoshi',
            'name': 'Mei',
            'role': '中文老师',
            'personality': 'Kind, patient, traditional',
            'specialties': ['pinyin', 'characters', 'chinese_culture'],
            'avatar_image': '👩‍🏫',
            'background': 'Experienced Chinese teacher from Beijing',
            'greeting': '你好！我是美老师。我来帮你学习中文！',
            'style': 'patient and encouraging'
        },
        {
            'id': 'chen_beijing',
            'name': 'Chen',
            'role': '北京人',
            'personality': 'Humorous, authentic, cultural',
            'specialties': ['beijing_dialect', 'chinese_idioms', 'daily_conversation'],
            'avatar_image': '👨‍🍳',
            'background': 'Beijing native who loves sharing Chinese culture and language',
            'greeting': '你好！我是小陈，地地道道的北京人。咱们一起学中文吧！',
            'style': 'humorous and authentic'
        }
    ]
}

@app.route('/api/avatars', methods=['GET'])
@rate_limit
def get_avatars():
    """Get available AI avatars for a language"""
    try:
        language = request.args.get('language', 'en')
        
        if language not in AVATAR_DATA:
            return jsonify({'error': f'No avatars available for language {language}'}), 404
        
        avatars = AVATAR_DATA[language]
        
        return jsonify({
            'avatars': avatars,
            'total': len(avatars),
            'language': language,
            'available_languages': list(AVATAR_DATA.keys())
        })
        
    except Exception as e:
        logger.error(f"Error fetching avatars: {e}")
        return jsonify({'error': 'Failed to fetch avatars'}), 500

@app.route('/api/avatar/<avatar_id>', methods=['GET'])
@rate_limit
def get_avatar_details(avatar_id):
    """Get detailed information about a specific avatar"""
    try:
        language = request.args.get('language', 'en')
        
        if language not in AVATAR_DATA:
            return jsonify({'error': f'Language {language} not supported'}), 404
        
        avatar = next((a for a in AVATAR_DATA[language] if a['id'] == avatar_id), None)
        
        if not avatar:
            return jsonify({'error': f'Avatar {avatar_id} not found'}), 404
        
        return jsonify(avatar)
        
    except Exception as e:
        logger.error(f"Error fetching avatar details: {e}")
        return jsonify({'error': 'Failed to fetch avatar details'}), 500

@app.route('/api/conversation/avatar', methods=['POST'])
@rate_limit
def avatar_conversation():
    """Enhanced conversation with AI avatars"""
    try:
        data = request.get_json()
        user_input = data.get('text')
        language = data.get('language')
        user_id = data.get('userId')
        avatar_id = data.get('avatarId')
        context = data.get('context', 'general')
        proficiency = data.get('proficiency', 'beginner')
        conversation_history = data.get('conversationHistory', [])
        
        if not all([user_input, language, user_id, avatar_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get avatar data
        if language not in AVATAR_DATA:
            return jsonify({'error': f'Language {language} not supported'}), 404
            
        avatar = next((a for a in AVATAR_DATA[language] if a['id'] == avatar_id), None)
        if not avatar:
            return jsonify({'error': f'Avatar {avatar_id} not found'}), 404

        # Build conversation history context
        history_context = ""
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 exchanges
            history_context = "\nConversation History:\n"
            for msg in recent_history:
                if msg['type'] == 'user':
                    history_context += f"User: {msg['text']}\n"
                elif msg['type'] == 'avatar':
                    history_context += f"You: {msg['response']}\n"

        # Generate enhanced conversation prompt with avatar personality
        conversation_prompt = f"""
        You are {avatar['name']}, a {avatar['role']} with the following characteristics:
        - Personality: {avatar['personality']}
        - Specialties: {', '.join(avatar['specialties'])}
        - Background: {avatar['background']}
        - Communication Style: {avatar['style']}
        
        You are having a conversation in {language} with a {proficiency} level learner.
        Context: {context}
        {history_context}
        
        User just said: "{user_input}"
        
        Respond in character as {avatar['name']} and provide a JSON response with these exact keys:
        {{
            "response": "Your natural response in {language} matching your personality",
            "translation": "English translation of your response",
            "vocabulary": ["key", "vocabulary", "words", "from", "response"],
            "grammar_notes": "Brief grammar explanation relevant to your response",
            "cultural_note": "Cultural context if relevant to your character or response",
            "suggested_responses": ["suggestion1", "suggestion2", "suggestion3"],
            "avatar_emotion": "happy/encouraging/thoughtful/excited/concerned",
            "teaching_tip": "A helpful tip related to your specialties if appropriate"
        }}
        
        Stay in character and adapt your response style to match {avatar['name']}'s personality.
        Keep responses appropriate for {proficiency} level learners.
        """

        # Generate response using LLM API
        if not gemini_model:
            return jsonify({'error': 'AI service temporarily unavailable'}), 503
            
        response_text = call_llm_api(conversation_prompt)
        
        try:
            # Try to parse the JSON response
            conversation_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback response in character
            conversation_data = {
                "response": avatar['greeting'] if not conversation_history else "I understand. Please continue.",
                "translation": avatar['greeting'] if not conversation_history else "I understand. Please continue.",
                "vocabulary": ["understand", "continue", "please"],
                "grammar_notes": "Simple present tense",
                "cultural_note": f"This is how {avatar['name']} would respond",
                "suggested_responses": ["Yes, I see", "Can you help me?", "Tell me more"],
                "avatar_emotion": "encouraging",
                "teaching_tip": f"Practice with {avatar['name']} to improve your {language} skills"
            }
        
        # Add avatar information to response
        conversation_data['avatar'] = {
            'id': avatar['id'],
            'name': avatar['name'],
            'role': avatar['role'],
            'avatar_image': avatar['avatar_image']
        }

        # Track user progress with avatar interaction
        if db_service:
            practice_session = {
                'timestamp': datetime.now().isoformat(),
                'type': 'avatar_conversation',
                'user_input': user_input,
                'ai_response': conversation_data['response'],
                'language': language,
                'context': context,
                'proficiency': proficiency,
                'avatar_id': avatar_id,
                'avatar_name': avatar['name'],
                'duration': 60,
                'performance': 0.8
            }
            
            # Use database service to track the session
            session_data = {
                'user_id': user_id,
                'session_type': 'avatar_conversation',
                'language': language,
                'context': context,
                'proficiency': proficiency,
                'duration': 60,
                'performance': 0.8,
                'data': practice_session
            }
            db_service.track_event(session_data)
        
        return jsonify(conversation_data)
        
    except Exception as e:
        logger.error(f"Error in avatar conversation: {e}")
        return jsonify({'error': 'Failed to generate avatar conversation response'}), 500

@app.route('/api/conversation/start-session', methods=['POST'])
@rate_limit
def start_conversation_session():
    """Start a new conversation session with an avatar"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        language = data.get('language')
        avatar_id = data.get('avatarId')
        
        if not all([user_id, language, avatar_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get avatar data
        if language not in AVATAR_DATA:
            return jsonify({'error': f'Language {language} not supported'}), 404
            
        avatar = next((a for a in AVATAR_DATA[language] if a['id'] == avatar_id), None)
        if not avatar:
            return jsonify({'error': f'Avatar {avatar_id} not found'}), 404

        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create initial greeting from avatar
        initial_message = {
            'type': 'avatar',
            'response': avatar['greeting'],
            'translation': avatar['greeting'],  # Same for greeting
            'avatar': {
                'id': avatar['id'],
                'name': avatar['name'],
                'role': avatar['role'],
                'avatar_image': avatar['avatar_image']
            },
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'vocabulary': [],
            'grammar_notes': 'Welcome message',
            'cultural_note': f"Meet {avatar['name']}, your {avatar['role']}",
            'avatar_emotion': 'welcoming'
        }
        
        return jsonify({
            'session_id': session_id,
            'avatar': avatar,
            'initial_message': initial_message,
            'language': language
        })
        
    except Exception as e:
        logger.error(f"Error starting conversation session: {e}")
        return jsonify({'error': 'Failed to start conversation session'}), 500

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

@app.route('/api/debug/populate-words', methods=['POST'])
def populate_word_data():
    """Debug endpoint to manually populate comprehensive word-of-day data for multiple languages"""
    try:
        logger.info("Manually populating multilingual word-of-day data...")
        
        # Ensure database tables exist
        create_tables()
        
        # Comprehensive word data for multiple languages
        multilingual_words = {
            'en': [
                {
                    'word': 'serendipity',
                    'translation': 'the occurrence of events by chance in a happy way',
                    'pronunciation': 'ˌser.ənˈdɪp.ə.ti',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'It was pure serendipity that we met at the coffee shop.',
                    'example_translation': 'Describes pleasant surprises or fortunate accidents.',
                    'etymology': 'Coined by Horace Walpole in 1754 from the Persian fairy tale',
                    'related_words': ['chance', 'fortune', 'luck', 'coincidence'],
                    'cultural_note': 'A beloved English word expressing life\'s pleasant surprises.'
                },
                {
                    'word': 'wanderlust',
                    'translation': 'a strong desire to travel and explore the world',
                    'pronunciation': 'ˈwɒn.də.lʌst',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Her wanderlust led her to visit 30 countries.',
                    'example_translation': 'Used to describe someone with a passion for traveling.',
                    'etymology': 'From German wandern (to hike) + lust (desire)',
                    'related_words': ['travel', 'adventure', 'exploration'],
                    'cultural_note': 'Reflects the human desire for exploration and discovery.'
                },
                {
                    'word': 'resilience',
                    'translation': 'the ability to recover quickly from difficulties',
                    'pronunciation': 'rɪˈzɪl.i.əns',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'She showed remarkable resilience after the setback.',
                    'example_translation': 'The capacity to bounce back from challenges.',
                    'etymology': 'From Latin resilire (to rebound)',
                    'related_words': ['strength', 'toughness', 'adaptability'],
                    'cultural_note': 'Highly valued quality in personal and professional contexts.'
                }
            ],
            'es': [
                {
                    'word': 'sobremesa',
                    'translation': 'time spent at the table after finishing a meal',
                    'pronunciation': 'so.βɾeˈme.sa',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'La sobremesa duró más que la cena.',
                    'example_translation': 'The after-dinner conversation lasted longer than dinner.',
                    'etymology': 'From sobre (over) + mesa (table)',
                    'related_words': ['charla', 'conversación', 'tertulia'],
                    'cultural_note': 'An important social custom in Spanish-speaking countries.'
                },
                {
                    'word': 'duende',
                    'translation': 'a quality of passion and inspiration, especially in flamenco',
                    'pronunciation': 'ˈdwen.de',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'El bailaor de flamenco tiene mucho duende.',
                    'example_translation': 'The flamenco dancer has great spirit and charm.',
                    'etymology': 'From dueño (owner), originally meaning a magical creature',
                    'related_words': ['alma', 'espíritu', 'pasión'],
                    'cultural_note': 'Essential concept in flamenco and Spanish arts.'
                },
                {
                    'word': 'querencia',
                    'translation': 'a place where one feels safe and at home',
                    'pronunciation': 'ke.ˈɾen.θja',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'Este café es mi querencia en la ciudad.',
                    'example_translation': 'This café is my safe haven in the city.',
                    'etymology': 'From querer (to love, to want)',
                    'related_words': ['hogar', 'refugio', 'santuario'],
                    'cultural_note': 'Deeply rooted in Spanish culture and bullfighting tradition.'
                }
            ],
            'fr': [
                {
                    'word': 'dépaysement',
                    'translation': 'the feeling of being in a foreign place',
                    'pronunciation': 'de.pɛ.iz.mɑ̃',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'Le dépaysement total lors de mon premier voyage à Tokyo.',
                    'example_translation': 'The complete feeling of displacement during my first trip to Tokyo.',
                    'etymology': 'From dé- (un-) + pays (country)',
                    'related_words': ['voyage', 'étranger', 'expatriation'],
                    'cultural_note': 'Unique French concept with no direct English equivalent.'
                },
                {
                    'word': 'flâner',
                    'translation': 'to wander aimlessly with pleasure',
                    'pronunciation': 'flɑ.ne',
                    'part_of_speech': 'verb',
                    'difficulty': 'intermediate',
                    'example_sentence': 'J\'aime flâner dans les rues de Paris.',
                    'example_translation': 'I love strolling through the streets of Paris.',
                    'etymology': 'From Old Norse flana (to rush about)',
                    'related_words': ['se promener', 'errer', 'déambuler'],
                    'cultural_note': 'Central to Parisian culture and the art of leisurely observation.'
                },
                {
                    'word': 'savoir-vivre',
                    'translation': 'knowledge of how to live well and behave properly',
                    'pronunciation': 'sa.vwaʁ.vivʁ',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Son savoir-vivre impressionne toujours les invités.',
                    'example_translation': 'His good manners always impress the guests.',
                    'etymology': 'From savoir (to know) + vivre (to live)',
                    'related_words': ['étiquette', 'politesse', 'bonnes manières'],
                    'cultural_note': 'Essential concept in French social interactions.'
                }
            ],
            'de': [
                {
                    'word': 'Fernweh',
                    'translation': 'longing for distant places; wanderlust',
                    'pronunciation': 'ˈfɛʁn.veː',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Sie hat Fernweh nach den Bergen.',
                    'example_translation': 'She longs for the mountains.',
                    'etymology': 'From fern (far) + Weh (pain)',
                    'related_words': ['Heimweh', 'Reisefieber', 'Wanderlust'],
                    'cultural_note': 'Reflects German romantic ideals of travel and exploration.'
                },
                {
                    'word': 'Gemütlichkeit',
                    'translation': 'warmth, coziness, and good cheer',
                    'pronunciation': 'ɡəˈmyːt.lɪç.kaɪt',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'Die Gemütlichkeit des Cafés lädt zum Verweilen ein.',
                    'example_translation': 'The coziness of the café invites you to linger.',
                    'etymology': 'From Gemüt (mind, spirit) + -lich (like) + -keit (-ness)',
                    'related_words': ['Behaglichkeit', 'Wärme', 'Geborgenheit'],
                    'cultural_note': 'Central to German culture and hospitality.'
                },
                {
                    'word': 'Zeitgeist',
                    'translation': 'the spirit or mood of a particular time period',
                    'pronunciation': 'ˈtsaɪt.ɡaɪst',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Der Zeitgeist der 60er Jahre war revolutionär.',
                    'example_translation': 'The spirit of the 60s was revolutionary.',
                    'etymology': 'From Zeit (time) + Geist (spirit)',
                    'related_words': ['Epoche', 'Ära', 'Stimmung'],
                    'cultural_note': 'Widely adopted into English and other languages.'
                }
            ],
            'ja': [
                {
                    'word': '木漏れ日',
                    'translation': 'sunlight filtering through trees',
                    'pronunciation': 'ko-mo-re-bi',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': '木漏れ日が森の中で踊っている。',
                    'example_translation': 'Sunlight is dancing through the trees in the forest.',
                    'etymology': 'From 木 (tree) + 漏れ (leak) + 日 (sun)',
                    'related_words': ['日光', '森林', '陽射し'],
                    'cultural_note': 'Reflects Japanese appreciation for subtle natural beauty.'
                },
                {
                    'word': 'もったいない',
                    'translation': 'regret over waste; too good to waste',
                    'pronunciation': 'mot-tai-nai',
                    'part_of_speech': 'adjective',
                    'difficulty': 'intermediate',
                    'example_sentence': 'まだ食べられるのに捨てるなんてもったいない。',
                    'example_translation': 'It\'s wasteful to throw it away when it\'s still edible.',
                    'etymology': 'From Buddhist concept of intrinsic value',
                    'related_words': ['無駄', '惜しい', '節約'],
                    'cultural_note': 'Reflects Japanese values of conservation and respect for resources.'
                },
                {
                    'word': '一期一会',
                    'translation': 'once in a lifetime encounter; treasure the moment',
                    'pronunciation': 'i-chi-go-i-chi-e',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': '今日の出会いは一期一会ですね。',
                    'example_translation': 'Today\'s meeting is a once-in-a-lifetime encounter.',
                    'etymology': 'From tea ceremony philosophy',
                    'related_words': ['出会い', '瞬間', '大切'],
                    'cultural_note': 'Important concept in Japanese tea ceremony and relationships.'
                }
            ],
            'zh': [
                {
                    'word': '缘分',
                    'translation': 'predestined relationship or connection',
                    'pronunciation': 'yuán-fèn',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': '我们能相遇真是缘分。',
                    'example_translation': 'Our meeting is truly fate.',
                    'etymology': 'From 缘 (connection) + 分 (portion)',
                    'related_words': ['命运', '缘份', '注定'],
                    'cultural_note': 'Important concept in Chinese philosophy and relationships.'
                },
                {
                    'word': '面子',
                    'translation': 'face; dignity and reputation in social contexts',
                    'pronunciation': 'miàn-zi',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': '给他留点面子吧。',
                    'example_translation': 'Let\'s save some face for him.',
                    'etymology': 'From 面 (face) + 子 (suffix)',
                    'related_words': ['尊严', '脸面', '声誉'],
                    'cultural_note': 'Crucial concept in Chinese social interactions.'
                },
                {
                    'word': '孝顺',
                    'translation': 'filial piety; respect and care for parents',
                    'pronunciation': 'xiào-shùn',
                    'part_of_speech': 'adjective/noun',
                    'difficulty': 'intermediate',
                    'example_sentence': '他是个很孝顺的儿子。',
                    'example_translation': 'He is a very filial son.',
                    'etymology': 'From 孝 (filial piety) + 顺 (obedience)',
                    'related_words': ['尊敬', '孝心', '侍奉'],
                    'cultural_note': 'Fundamental virtue in Confucian culture.'
                }
            ],
            'it': [
                {
                    'word': 'dolce far niente',
                    'translation': 'the sweetness of doing nothing',
                    'pronunciation': 'ˈdol.tʃe far ˈnjen.te',
                    'part_of_speech': 'phrase',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Oggi ho voglia di dolce far niente.',
                    'example_translation': 'Today I feel like enjoying the sweetness of doing nothing.',
                    'etymology': 'From dolce (sweet) + far (to do) + niente (nothing)',
                    'related_words': ['riposo', 'relax', 'ozio'],
                    'cultural_note': 'Italian appreciation for leisure and contemplation.'
                },
                {
                    'word': 'passeggiata',
                    'translation': 'evening stroll for socializing',
                    'pronunciation': 'pas.sed.ˈdʒa.ta',
                    'part_of_speech': 'noun',
                    'difficulty': 'beginner',
                    'example_sentence': 'Facciamo una passeggiata in centro?',
                    'example_translation': 'Shall we take a stroll in the city center?',
                    'etymology': 'From passeggiare (to walk, to stroll)',
                    'related_words': ['camminata', 'giro', 'passeggiate'],
                    'cultural_note': 'Important Italian social tradition, especially in small towns.'
                },
                {
                    'word': 'sprezzatura',
                    'translation': 'studied carelessness; effortless grace',
                    'pronunciation': 'spret.tsa.ˈtu.ra',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'La sua sprezzatura nel vestire è ammirevole.',
                    'example_translation': 'His effortless elegance in dressing is admirable.',
                    'etymology': 'From sprezzare (to despise, to scorn)',
                    'related_words': ['eleganza', 'grazia', 'naturalezza'],
                    'cultural_note': 'Renaissance ideal of appearing naturally graceful.'
                }
            ],
            'pt': [
                {
                    'word': 'saudade',
                    'translation': 'deep nostalgic longing for something absent',
                    'pronunciation': 'saw.ˈda.dʒi',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Tenho saudade dos tempos de escola.',
                    'example_translation': 'I have nostalgia for school days.',
                    'etymology': 'From Latin solitas (solitude)',
                    'related_words': ['nostalgia', 'longing', 'melancolia'],
                    'cultural_note': 'Quintessential Portuguese emotion, untranslatable to other languages.'
                },
                {
                    'word': 'cafuné',
                    'translation': 'gently running fingers through someone\'s hair',
                    'pronunciation': 'ka.fu.ˈnɛ',
                    'part_of_speech': 'noun',
                    'difficulty': 'intermediate',
                    'example_sentence': 'Ela fazia cafuné no filho para ele dormir.',
                    'example_translation': 'She gently stroked her son\'s hair to help him sleep.',
                    'etymology': 'From African languages brought to Brazil',
                    'related_words': ['carinho', 'caricia', 'mimo'],
                    'cultural_note': 'Tender gesture common in Brazilian family relationships.'
                },
                {
                    'word': 'desenrascanço',
                    'translation': 'the art of finding creative solutions to problems',
                    'pronunciation': 'de.zen.ʁas.ˈkɐ̃.su',
                    'part_of_speech': 'noun',
                    'difficulty': 'advanced',
                    'example_sentence': 'O desenrascanço português é famoso no mundo todo.',
                    'example_translation': 'Portuguese resourcefulness is famous worldwide.',
                    'etymology': 'From desenrascar (to get out of trouble)',
                    'related_words': ['criatividade', 'jeitinho', 'improviso'],
                    'cultural_note': 'Reflects Portuguese resourcefulness and problem-solving spirit.'
                }
            ]
        }
        
        # Add word data for each language
        total_added = 0
        total_failed = 0
        languages_processed = []
        
        for language, words in multilingual_words.items():
            language_added = 0
            
            for word in words:
                success = db_service.add_word_of_day(language, word)
                if success:
                    language_added += 1
                    total_added += 1
                    logger.info(f"Added {language}: {word['word']}")
                else:
                    total_failed += 1
                    logger.warning(f"Failed to add {language}: {word['word']}")
            
            if language_added > 0:
                languages_processed.append(f"{language} ({language_added} words)")
        
        # Verify by getting test words from each language
        verification_results = {}
        for language in multilingual_words.keys():
            test_word = db_service.get_word_of_day(language)
            verification_results[language] = test_word.get('word') if test_word else 'NONE'
        
        return jsonify({
            'success': True,
            'message': f'Successfully populated multilingual word-of-day data',
            'total_added': total_added,
            'total_failed': total_failed,
            'languages_processed': languages_processed,
            'available_languages': list(multilingual_words.keys()),
            'verification': verification_results,
            'summary': f'Added {total_added} words across {len(multilingual_words)} languages'
        })
        
    except Exception as e:
        logger.error(f"Error populating multilingual word data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to populate multilingual word-of-day data'
        }), 500

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