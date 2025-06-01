# TTSAI Project Planning

## 🎯 Project Overview
Real-time speech translation application with advanced learning tools, built with React frontend and Flask backend.

## 🏗️ Architecture

### Backend (Flask)
- **Core API**: Flask application with rate limiting and caching
- **AI Services**: Google Cloud + Gemini AI for translation
- **Data Storage**: SQLite database + JSON files for lightweight data
- **Authentication**: Basic user identification via userId parameter
- **Deployment**: Google Cloud Run

### Frontend (React)
- **UI Framework**: Material-UI (MUI) v5 
- **State Management**: React hooks + localStorage
- **API Communication**: Axios with error handling
- **Speech Processing**: Web Speech API
- **Build/Deploy**: Netlify

## 📁 File Structure Patterns

### Backend Structure
```
backend/
├── app.py              # Main Flask application (MAX 500 lines)
├── models.py           # Database models
├── db_service.py       # Database operations
├── config.py           # Configuration management
├── requirements.txt    # Dependencies
└── data/              # JSON storage files
```

### Frontend Structure  
```
frontend/src/
├── components/        # React components (MAX 500 lines each)
│   ├── Translator.js  # Main translation interface
│   ├── LearningTools.js # Learning features
│   └── Layout.js      # App layout
├── App.js            # Main app component
└── index.js          # Entry point
```

## 🔧 Technology Stack

### Required Dependencies
- **Backend**: Flask, Flask-CORS, SQLAlchemy, google-cloud-speech, google-cloud-texttospeech, google-generativeai
- **Frontend**: React 18, @mui/material, axios, @emotion/react, @emotion/styled

### API Patterns
- All endpoints prefixed with `/api/`
- Rate limiting: 100 requests/minute per IP
- Caching: 5-minute cache for translations
- Error handling: Consistent JSON error responses

## 🎨 Style Guidelines

### Naming Conventions
- **Files**: kebab-case for files, PascalCase for React components
- **Variables**: camelCase for JavaScript, snake_case for Python
- **Database**: snake_case for tables and columns
- **API**: kebab-case for endpoints

### Code Style
- **Python**: PEP8, type hints, Google-style docstrings
- **JavaScript**: ESLint, consistent arrow functions
- **Import Order**: Standard library → Third party → Local modules

## 🚀 Deployment Strategy

### Backend
- Container: Docker with multi-stage build
- Platform: Google Cloud Run
- Environment: Production environment variables
- Health checks: `/api/health` endpoint

### Frontend  
- Build: Create React App production build
- CDN: Netlify with automatic deployments
- Environment: React environment variables

## 🎯 Goals & Constraints

### Performance Goals
- Translation response: < 2 seconds
- UI interactions: < 100ms
- Mobile responsiveness: All screen sizes

### Learning Features
- Daily vocabulary with spaced repetition
- Interactive quizzes with progress tracking
- Conversation practice with AI feedback
- Flashcard system with user customization

### Quality Constraints
- Test coverage: Unit tests for all core functions
- File size: No file > 500 lines
- Error handling: All API calls have fallbacks
- Accessibility: WCAG 2.1 AA compliance 