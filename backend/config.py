import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# LLM Model Configuration - SINGLE SOURCE OF TRUTH
# Change this to switch models throughout the entire application
LLM_MODEL = "google/gemini-2.0-flash-exp:free"
LLM_PROVIDER = "openrouter"  # Currently supports: openrouter
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0.7

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Google Cloud credentials path (optional - for TTS/STT only)
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'path/to/your/credentials.json')
if GOOGLE_CREDENTIALS_PATH and GOOGLE_CREDENTIALS_PATH != 'path/to/your/credentials.json':
    if not os.path.isabs(GOOGLE_CREDENTIALS_PATH):
        # Convert relative path to absolute
        GOOGLE_CREDENTIALS_PATH = str(BASE_DIR / GOOGLE_CREDENTIALS_PATH)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_PATH

# Legacy Gemini API key (for backwards compatibility, but not required)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.getenv('PORT', 5000))

# Validation
if LLM_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. LLM features will be unavailable.")

def get_llm_config():
    """Get the current LLM configuration"""
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