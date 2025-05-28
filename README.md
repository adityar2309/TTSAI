# Real-Time Speech Translation App

This application provides real-time speech translation using Google Cloud Speech-to-Text, Gemini LLM, and Google Cloud Text-to-Speech APIs.

## Features

- Real-time speech recognition
- Dynamic language translation using Gemini LLM
- Text-to-speech output in target language
- Mobile-responsive design
- Support for multiple language pairs

## Prerequisites

1. Node.js (v16 or higher)
2. Python 3.8+
3. Google Cloud Platform account
4. Gemini API access

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Frontend (.env):
```
REACT_APP_API_URL=http://localhost:5000
```

### Backend (.env):
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=development
```

## Setup

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure your Google Cloud credentials and Gemini API key

## Running the Application

1. Start the backend:
   ```bash
   cd backend
   flask run
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open http://localhost:3000 in your browser

## Security Considerations

- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting
- Add user authentication if needed

## Deployment

### Frontend
- Build the React app using `npm run build`
- Deploy to a static hosting service (Netlify, Vercel, etc.)

### Backend
- Deploy to a cloud platform (Google Cloud Run, Heroku, etc.)
- Set up environment variables in your deployment platform
- Enable CORS for your frontend domain
- Use HTTPS for all API calls

## License

MIT 