import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Google Cloud credentials path
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if GOOGLE_CREDENTIALS_PATH and not os.path.isabs(GOOGLE_CREDENTIALS_PATH):
    # Convert relative path to absolute
    GOOGLE_CREDENTIALS_PATH = str(BASE_DIR / GOOGLE_CREDENTIALS_PATH)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_PATH

# Verify credentials file exists
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    raise FileNotFoundError(
        f"Google Cloud credentials file not found at {GOOGLE_CREDENTIALS_PATH}. "
        "Please follow the setup instructions to configure your credentials."
    )

# Other configuration settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set. "
        "Please add it to your .env file."
    )

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.getenv('PORT', 5000)) 