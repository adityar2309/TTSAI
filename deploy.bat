@echo off
echo Deploying TTSAI Backend to Cloud Run...
gcloud run deploy ttsai-backend --image gcr.io/ttsai-461209/ttsai-backend:latest --platform managed --region us-central1 --allow-unauthenticated --port 8080
echo Deployment complete! 