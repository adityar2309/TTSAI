@echo off
echo ========================================
echo   FIXING 503 SERVICE UNAVAILABLE ERRORS
echo ========================================
echo.

echo PROBLEM: Your current API key is INVALID
echo This is causing all translation requests to return 503 errors.
echo.

echo STEP 1: GET A NEW API KEY
echo ========================================
echo 1. Open: https://aistudio.google.com/app/apikey
echo 2. Click "Create API Key"
echo 3. Select your project
echo 4. Copy the new API key
echo.

set /p NEW_API_KEY="Enter your NEW API key: "

if "%NEW_API_KEY%"=="" (
    echo ERROR: No API key entered. Exiting...
    pause
    exit /b 1
)

echo.
echo ✓ API key received: %NEW_API_KEY:~0,10%...

echo.
echo STEP 2: DEPLOYING WITH NEW API KEY
echo ========================================

echo Setting environment variable...
set GEMINI_API_KEY=%NEW_API_KEY%

echo Changing to backend directory...
cd backend

echo Authenticating with Google Cloud...
gcloud auth login

echo Setting project...
gcloud config set project ttsai-461209

echo Deploying to Cloud Run...
gcloud run deploy ttsai-backend ^
  --source . ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --memory 2Gi ^
  --cpu 2 ^
  --set-env-vars GEMINI_API_KEY=%NEW_API_KEY%,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production ^
  --port 5000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! DEPLOYMENT COMPLETED!
    echo ========================================
    echo.
    echo Testing the backend...
    cd..
    python test_backend.py
    echo.
    echo Your 503 errors should now be fixed!
    echo Try using your frontend application.
) else (
    echo.
    echo ❌ Deployment failed. Check the error messages above.
)

echo.
pause 