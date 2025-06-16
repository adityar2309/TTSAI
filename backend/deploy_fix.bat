@echo off
echo Deploying TTSAI Backend with TTS/STT endpoints...

gcloud run deploy ttsai-backend ^
  --source . ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --memory 2Gi ^
  --cpu 2 ^
  --set-env-vars GEMINI_API_KEY=AIzaSyDhFOZFdZZjoA-hgHrbW9waBtvoYSRY6nw,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production ^
  --port 5000

echo Deployment complete!
pause 