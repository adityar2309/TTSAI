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
from datetime import datetime
import random
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow all origins, methods and headers
CORS(app, resources={
    r"/*": {  # Allow all routes
        "origins": [
            "http://localhost:3000",  # Development
            "https://ttsai.netlify.app",  # Production Netlify domain
            "https://*.netlify.app",  # All Netlify preview deployments
            "https://6837027b175dc48ca24afe5c--ttsai.netlify.app"  # Current preview deployment
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Google Cloud clients
speech_client = SpeechClient()
tts_client = TextToSpeechClient()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found in environment variables")

logger.info(f"Configuring Gemini with API key: {api_key[:4]}...{api_key[-4:]}")
genai.configure(api_key=api_key)

# Use gemini-1.0-pro
model = genai.GenerativeModel('gemini-1.5-flash')

def get_advanced_translation_prompt(text, source_lang, target_lang, formality="neutral", dialect=None):
    return f"""Provide a comprehensive translation analysis with the following components:

1. Main Translation:
   - Translate from {source_lang} to {target_lang}
   - Formality level: {formality}
   {f'- Dialect: {dialect}' if dialect else ''}

2. Alternative Translations:
   - Provide 2-3 alternative translations with confidence scores (%)
   - Explain the nuances of each alternative

3. Pronunciation Guide:
   - IPA notation
   - Syllable breakdown
   - Stress markers

4. Grammar Analysis:
   - Part of speech for key words
   - Sentence structure explanation
   - Grammar rules applied

5. Contextual Usage:
   - Common contexts where this phrase is used
   - Example sentences
   - Cultural notes if relevant

Text to analyze: {text}

Return the response in JSON format with these exact keys:
{
    "main_translation": "",
    "alternatives": [{"text": "", "confidence": 0, "explanation": ""}],
    "pronunciation": {"ipa": "", "syllables": "", "stress": ""},
    "grammar": {"parts_of_speech": [], "structure": "", "rules": []},
    "context": {"usage": [], "examples": [], "cultural_notes": ""}
}"""

@app.route('/api/advanced-translate', methods=['POST'])
def advanced_translate():
    try:
        data = request.json
        text = data.get('text')
        source_lang = data.get('sourceLang')
        target_lang = data.get('targetLang')
        formality = data.get('formality', 'neutral')
        dialect = data.get('dialect')
        
        if not all([text, source_lang, target_lang]):
            missing = []
            if not text: missing.append('text')
            if not source_lang: missing.append('sourceLang')
            if not target_lang: missing.append('targetLang')
            error_msg = f"Missing required parameters: {', '.join(missing)}"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
        
        prompt = get_advanced_translation_prompt(text, source_lang, target_lang, formality, dialect)
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return jsonify({'error': 'Translation failed'}), 500
            
        try:
            translation_data = json.loads(response.text)
            return jsonify(translation_data)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid response format'}), 500
            
    except Exception as e:
        error_msg = f"Translation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

# Learning tools endpoints
PHRASES_FILE = 'data/common_phrases.json'
WORD_OF_DAY_FILE = 'data/word_of_day.json'
USER_PROGRESS_FILE = 'data/user_progress.json'

def load_json_file(file_path, default=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json_file(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/common-phrases', methods=['GET'])
def get_common_phrases():
    language = request.args.get('language')
    if not language:
        return jsonify({'error': 'Language parameter required'}), 400
        
    phrases = load_json_file(PHRASES_FILE, {'phrases': {}})
    return jsonify(phrases.get('phrases', {}).get(language, []))

@app.route('/api/word-of-day', methods=['GET'])
def get_word_of_day():
    language = request.args.get('language')
    if not language:
        return jsonify({'error': 'Language parameter required'}), 400
        
    words = load_json_file(WORD_OF_DAY_FILE, {'words': {}})
    today = datetime.now().strftime('%Y-%m-%d')
    
    if language not in words.get('words', {}):
        return jsonify({'error': 'Language not supported'}), 404
        
    word_list = words['words'][language]
    # Use date as seed for consistent daily word
    random.seed(today)
    word = random.choice(word_list)
    
    return jsonify(word)

@app.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    try:
        data = request.json
        user_id = data.get('userId')
        translation = data.get('translation')
        
        if not all([user_id, translation]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        
        if user_id not in progress['users']:
            progress['users'][user_id] = {
                'flashcards': [],
                'quiz_scores': [],
                'practice_sessions': []
            }
            
        flashcard = {
            'id': len(progress['users'][user_id]['flashcards']) + 1,
            'translation': translation,
            'created_at': datetime.now().isoformat(),
            'review_count': 0,
            'mastery_level': 0
        }
        
        progress['users'][user_id]['flashcards'].append(flashcard)
        save_json_file(USER_PROGRESS_FILE, progress)
        
        return jsonify(flashcard)
        
    except Exception as e:
        error_msg = f"Flashcard creation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        user_id = data.get('userId')
        language = data.get('language')
        difficulty = data.get('difficulty', 'beginner')
        
        if not all([user_id, language]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Generate quiz based on user's flashcards and common phrases
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        user_flashcards = progress.get('users', {}).get(user_id, {}).get('flashcards', [])
        common_phrases = load_json_file(PHRASES_FILE, {'phrases': {}}).get('phrases', {}).get(language, [])
        
        # Combine and generate quiz questions
        quiz_questions = []
        if user_flashcards:
            flashcard_questions = generate_questions_from_flashcards(user_flashcards, difficulty)
            quiz_questions.extend(flashcard_questions)
            
        if common_phrases:
            phrase_questions = generate_questions_from_phrases(common_phrases, difficulty)
            quiz_questions.extend(phrase_questions)
            
        random.shuffle(quiz_questions)
        return jsonify({'questions': quiz_questions[:10]})  # Return 10 questions
        
    except Exception as e:
        error_msg = f"Quiz generation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

@app.route('/api/progress/update', methods=['POST'])
def update_progress():
    try:
        data = request.json
        user_id = data.get('userId')
        activity_type = data.get('activityType')  # 'flashcard', 'quiz', or 'practice'
        activity_data = data.get('activityData')
        
        if not all([user_id, activity_type, activity_data]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        progress = load_json_file(USER_PROGRESS_FILE, {'users': {}})
        
        if user_id not in progress['users']:
            progress['users'][user_id] = {
                'flashcards': [],
                'quiz_scores': [],
                'practice_sessions': []
            }
            
        if activity_type == 'flashcard':
            update_flashcard_progress(progress['users'][user_id], activity_data)
        elif activity_type == 'quiz':
            update_quiz_progress(progress['users'][user_id], activity_data)
        elif activity_type == 'practice':
            update_practice_progress(progress['users'][user_id], activity_data)
            
        save_json_file(USER_PROGRESS_FILE, progress)
        return jsonify({'status': 'success'})
        
    except Exception as e:
        error_msg = f"Progress update error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

def generate_questions_from_flashcards(flashcards, difficulty):
    questions = []
    for card in flashcards:
        question = {
            'type': 'translation',
            'text': card['translation']['originalText'],
            'correct_answer': card['translation']['translatedText'],
            'options': generate_options(card['translation']['translatedText'], difficulty),
            'difficulty': difficulty
        }
        questions.append(question)
    return questions

def generate_questions_from_phrases(phrases, difficulty):
    questions = []
    for phrase in phrases:
        question = {
            'type': 'phrase',
            'text': phrase['text'],
            'correct_answer': phrase['translation'],
            'options': generate_options(phrase['translation'], difficulty),
            'difficulty': difficulty
        }
        questions.append(question)
    return questions

def generate_options(correct_answer, difficulty):
    # Implement logic to generate plausible wrong answers
    # This is a placeholder - you would need to implement proper option generation
    return [correct_answer, "Option 2", "Option 3", "Option 4"]

def update_flashcard_progress(user_data, activity_data):
    for flashcard in user_data['flashcards']:
        if flashcard['id'] == activity_data['flashcardId']:
            flashcard['review_count'] += 1
            flashcard['mastery_level'] = min(5, flashcard['mastery_level'] + activity_data['success'])
            break

def update_quiz_progress(user_data, activity_data):
    user_data['quiz_scores'].append({
        'timestamp': datetime.now().isoformat(),
        'score': activity_data['score'],
        'total_questions': activity_data['totalQuestions'],
        'difficulty': activity_data['difficulty']
    })

def update_practice_progress(user_data, activity_data):
    user_data['practice_sessions'].append({
        'timestamp': datetime.now().isoformat(),
        'duration': activity_data['duration'],
        'type': activity_data['practiceType'],
        'performance': activity_data['performance']
    })

# List of supported languages with their codes and names
SUPPORTED_LANGUAGES = [
    {'code': 'en', 'name': 'English'},
    {'code': 'es', 'name': 'Spanish'},
    {'code': 'fr', 'name': 'French'},
    {'code': 'de', 'name': 'German'},
    {'code': 'it', 'name': 'Italian'},
    {'code': 'pt', 'name': 'Portuguese'},
    {'code': 'ru', 'name': 'Russian'},
    {'code': 'ja', 'name': 'Japanese'},
    {'code': 'ko', 'name': 'Korean'},
    {'code': 'zh', 'name': 'Chinese'},
    {'code': 'hi', 'name': 'Hindi'},
    {'code': 'ar', 'name': 'Arabic'},
]

@app.route('/api/supported-languages', methods=['GET'])
def get_supported_languages():
    """Return the list of supported languages."""
    return jsonify(SUPPORTED_LANGUAGES)

@app.route('/api/detect-language', methods=['POST'])
def detect_language():
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        # Use Gemini to detect language
        prompt = f"Detect the language of this text and return only the ISO 639-1 language code: {text}"
        response = model.generate_content(prompt)
        
        # Extract the language code from response
        lang_code = response.text.strip().lower()
        
        return jsonify({
            'detectedLanguage': lang_code,
            'confidence': 0.9  # Placeholder confidence score
        })
        
    except Exception as e:
        error_msg = f"Language detection error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text')
        source_lang = data.get('sourceLang')
        target_lang = data.get('targetLang')
        
        if not all([text, target_lang]):
            missing = []
            if not text: missing.append('text')
            if not target_lang: missing.append('targetLang')
            error_msg = f"Missing required parameters: {', '.join(missing)}"
            return jsonify({'error': error_msg}), 400
            
        # Use Gemini for basic translation
        prompt = f"Translate this text from {source_lang if source_lang else 'auto'} to {target_lang}: {text}"
        response = model.generate_content(prompt)
        
        return jsonify({
            'translatedText': response.text.strip(),
            'detectedSourceLanguage': source_lang or 'auto'
        })
    
    except Exception as e:
        error_msg = f"Translation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')
        language_code = data.get('languageCode', 'en-US')
        
        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400
        
        # Map language codes to appropriate voice names
        voice_mapping = {
            'en': 'en-US-Standard-C',
            'es': 'es-ES-Standard-A',
            'fr': 'fr-FR-Standard-A',
            'de': 'de-DE-Standard-A',
            'it': 'it-IT-Standard-A',
            'pt': 'pt-BR-Standard-A',
            'ru': 'ru-RU-Standard-A',
            'ja': 'ja-JP-Standard-A',
            'ko': 'ko-KR-Standard-A',
            'zh': 'cmn-CN-Standard-A',
            'hi': 'hi-IN-Standard-A',
            'ar': 'ar-XA-Standard-A',
        }

        # Get the base language code (e.g., 'en' from 'en-US')
        base_language = language_code.split('-')[0].lower()
        
        # Get the appropriate voice name or fallback to a default
        voice_name = voice_mapping.get(base_language, 'en-US-Standard-C')

        # Configure the voice request
        synthesis_input = tts.SynthesisInput(text=text)
        
        # Build the voice parameters
        voice = tts.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        # Select the audio file type
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        # Perform the text-to-speech request
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Convert the binary audio content to base64
        audio_content = base64.b64encode(response.audio_content).decode('utf-8')
        
        return jsonify({'audioContent': audio_content})
    
    except Exception as e:
        error_msg = f"Text-to-speech error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development') 