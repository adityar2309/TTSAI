@echo off
echo Deploying TTSAI Backend to Cloud Run...
echo NOTE: Make sure GEMINI_API_KEY is set as an environment variable
gcloud run deploy ttsai-backend --image gcr.io/ttsai-461209/ttsai-backend:latest --platform managed --region us-central1 --allow-unauthenticated --port 8080 --set-env-vars="GEMINI_API_KEY=%GEMINI_API_KEY%"
echo Deployment complete! 