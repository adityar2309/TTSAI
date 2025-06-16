# Real-Time Speech Translation App

A powerful real-time speech translation application with advanced learning tools, built with React, Flask, and Google's AI services.

## 🚀 Live Demo

Try the app here: [https://ttsai.netlify.app/](https://ttsai.netlify.app/)

## Features

### Translation
- Real-time speech-to-text translation
- Support for multiple languages with dialect selection
- Formality level control (formal, neutral, informal)
- Text-to-speech playback of translations
- **Romanization support for non-Latin scripts** (Chinese, Japanese, Arabic, Hindi, etc.)
- Conversation mode for bilingual chats
- Translation history with favorites
- Advanced translation details including:
  - Alternative translations with confidence scores
  - IPA pronunciation
  - Grammar analysis
  - Contextual usage examples

### Learning Tools
- Daily word/phrase learning
- Flashcard system with spaced repetition
- Interactive quizzes
- Progress tracking
- Pronunciation practice
- Cultural notes and usage examples

## Tech Stack

### Frontend
- React 18
- Material-UI (MUI) v5
- Axios for API calls
- Web Speech API for voice input
- LocalStorage for persistence

### Backend
- Flask
- Google AI Studio (Gemini) for translations
- Google Cloud Services (optional):
  - Text-to-Speech
  - Speech-to-Text
- CORS handling
- JSON file-based storage

## Prerequisites

1. Node.js (v16 or higher)
2. Python 3.8+
3. Google AI Studio API key (get from https://aistudio.google.com/app/apikey)
4. Google Cloud account (optional, for TTS/STT services)

## Setup Instructions

### Backend Setup

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file in backend directory
GEMINI_API_KEY=your_google_ai_studio_api_key_here
FLASK_ENV=development

# Optional: For Google Cloud TTS/STT services
# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-cloud-credentials.json
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
# Create .env file in frontend directory
REACT_APP_API_URL=http://localhost:5000/api
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:3000`

## Project Structure

```
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── data/              # JSON storage
│       ├── common_phrases.json
│       ├── word_of_day.json
│       └── user_progress.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Translator.js
│   │   │   ├── AdvancedTranslation.js
│   │   │   └── LearningTools.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── public/
└── README.md
```

## API Endpoints

### Translation Endpoints
- `POST /api/translate` - Basic translation
- `POST /api/advanced-translate` - Advanced translation with details
- `POST /api/detect-language` - Language detection
- `POST /api/text-to-speech` - Text to speech conversion

### Learning Tools Endpoints
- `GET /api/word-of-day` - Get word of the day
- `GET /api/flashcards` - Get user's flashcards
- `POST /api/flashcards` - Create new flashcard
- `POST /api/quiz/generate` - Generate new quiz
- `POST /api/quiz/submit` - Submit quiz answer
- `POST /api/progress/update` - Update learning progress

## Error Handling

The application includes comprehensive error handling:
- Network error detection and retry logic
- User-friendly error messages
- Fallback behaviors for unsupported features
- CORS error prevention
- API rate limiting protection

## Browser Support

- Chrome (recommended for full speech recognition support)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for your own purposes.

## Acknowledgments

- Google Cloud Platform for AI services
- Material-UI team for the component library
- React team for the framework
- Flask team for the backend framework 