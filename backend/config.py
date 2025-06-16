import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# LLM Model Configuration - SINGLE SOURCE OF TRUTH
# Change this to switch models throughout the entire application
LLM_MODEL = "gemini-2.0-flash-exp"  # Direct Google AI Studio model name
LLM_PROVIDER = "google_ai_studio"  # Changed from openrouter to google_ai_studio
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0.7

# Google AI Studio API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_AI_STUDIO_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Legacy OpenRouter configuration (kept for backwards compatibility)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Google Cloud credentials path (optional - for TTS/STT only)
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'path/to/your/credentials.json')
if GOOGLE_CREDENTIALS_PATH and GOOGLE_CREDENTIALS_PATH != 'path/to/your/credentials.json':
    if not os.path.isabs(GOOGLE_CREDENTIALS_PATH):
        # Convert relative path to absolute
        GOOGLE_CREDENTIALS_PATH = str(BASE_DIR / GOOGLE_CREDENTIALS_PATH)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_PATH

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.getenv('PORT', 5000))

# Validation
if LLM_PROVIDER == "google_ai_studio" and not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set. LLM features will be unavailable.")
elif LLM_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. LLM features will be unavailable.")

def get_llm_config():
    """Get the current LLM configuration"""
    if LLM_PROVIDER == "google_ai_studio":
        return {
            "model": LLM_MODEL,
            "provider": LLM_PROVIDER,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
            "api_key": GEMINI_API_KEY,
            "base_url": GOOGLE_AI_STUDIO_BASE_URL
        }
    else:  # openrouter fallback
        return {
            "model": LLM_MODEL,
            "provider": LLM_PROVIDER,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
            "api_key": OPENROUTER_API_KEY,
            "base_url": OPENROUTER_BASE_URL
        }

def get_model_name():
    """Get the current model name - use this throughout the application"""
    return LLM_MODEL 