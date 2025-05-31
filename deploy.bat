@echo off
echo Deploying TTSAI Backend to Cloud Run...
echo NOTE: Make sure GEMINI_API_KEY is set as an environment variable

echo Building and pushing Docker image...
gcloud builds submit --tag gcr.io/ttsai-461209/ttsai-backend:latest ./backend

echo Deploying to Cloud Run...
gcloud run deploy ttsai-backend ^
  --image gcr.io/ttsai-461209/ttsai-backend:latest ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --port 5000 ^
  --memory 1Gi ^
  --cpu 1 ^
  --set-env-vars="GEMINI_API_KEY=%GEMINI_API_KEY%,DATABASE_URL=sqlite:///app/ttsai.db"

echo Deployment complete! 