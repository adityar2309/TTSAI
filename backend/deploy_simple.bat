@echo off
echo ========================================
echo   DEPLOYING WITH NEW API KEY
echo ========================================

echo Setting environment variable...
set GEMINI_API_KEY=AIzaSyDhFOZFdZZjoA-hgHrbW9waBtvoYSRY6nw

echo.
echo Deploying to Google Cloud Run...
gcloud run deploy ttsai-backend --source . --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --cpu 2 --set-env-vars GEMINI_API_KEY="AIzaSyDhFOZFdZZjoA-hgHrbW9waBtvoYSRY6nw",DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production --port 5000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! DEPLOYMENT COMPLETED!
    echo ========================================
    echo.
    echo Testing the backend...
    cd ..
    python test_backend.py
) else (
    echo.
    echo ❌ Deployment failed. Check the error messages above.
)

echo.
pause 