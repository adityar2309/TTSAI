@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    TTSAI Full Stack Deployment Script
echo    (Backend + Frontend with Auth)
echo ========================================
echo.

REM Check if gcloud is installed and authenticated
echo [1/8] Checking Google Cloud CLI...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Google Cloud CLI not found. Please install gcloud CLI first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ✓ Google Cloud CLI found

REM Check authentication
echo [2/8] Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr "@" >nul
if errorlevel 1 (
    echo ERROR: Not authenticated with Google Cloud. Please run:
    echo   gcloud auth login
    echo   gcloud config set project ttsai-461209
    pause
    exit /b 1
)
echo ✓ Google Cloud authentication verified

REM Check if GEMINI_API_KEY is set
echo [3/8] Checking environment variables...
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY is not set. Using default from .env file.
    set GEMINI_API_KEY=AIzaSyCZzto0BK9sPgX8_QEidRP4mM8-90tf-OM
    echo Using API key: !GEMINI_API_KEY:~0,8!...
) else (
    echo ✓ GEMINI_API_KEY is set: %GEMINI_API_KEY:~0,8%...
)

REM Change to backend directory
echo [4/8] Building backend Docker image...
cd /d "%~dp0backend"
if not exist "Dockerfile" (
    echo ERROR: Dockerfile not found in backend directory.
    cd /d "%~dp0"
    pause
    exit /b 1
)

REM Build and push using Cloud Build
echo Building backend with Cloud Build...
gcloud builds submit --tag gcr.io/ttsai-461209/ttsai-backend:latest .
if errorlevel 1 (
    echo ERROR: Backend Docker build failed.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo ✓ Backend Docker image built and pushed successfully

REM Deploy backend to Cloud Run
echo [5/8] Deploying backend to Cloud Run...
cd /d "%~dp0"

REM Set environment variables for deployment (including new auth variables)
set "ENV_VARS=GEMINI_API_KEY=%GEMINI_API_KEY%,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production,GOOGLE_CLIENT_ID=your_client_id_here,GOOGLE_CLIENT_SECRET=your_client_secret_here,GOOGLE_CALLBACK_URL=https://ttsai-backend-321805997355.us-central1.run.app/api/auth/google/callback,JWT_SECRET=your_jwt_secret_here"

echo Deploying backend with configuration:
echo   - Image: gcr.io/ttsai-461209/ttsai-backend:latest
echo   - Region: us-central1
echo   - Memory: 2Gi
echo   - CPU: 2
echo   - Max instances: 100
echo   - Min instances: 0
echo   - Environment: Google AI Studio + Authentication

gcloud run deploy ttsai-backend ^
  --image gcr.io/ttsai-461209/ttsai-backend:latest ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --port 5000 ^
  --memory 2Gi ^
  --cpu 2 ^
  --max-instances 100 ^
  --min-instances 0 ^
  --timeout 300 ^
  --concurrency 80 ^
  --set-env-vars=%ENV_VARS%

if errorlevel 1 (
    echo ERROR: Backend Cloud Run deployment failed.
    pause
    exit /b 1
)

echo ✓ Backend deployment completed successfully!

REM Get the backend service URL
echo [6/8] Getting backend service URL...
for /f "tokens=*" %%i in ('gcloud run services describe ttsai-backend --region=us-central1 --format="value(status.url)"') do set BACKEND_URL=%%i

if "%BACKEND_URL%"=="" (
    echo ERROR: Could not retrieve backend service URL.
    pause
    exit /b 1
)

echo ✓ Backend URL: %BACKEND_URL%

REM Test backend health
echo Testing backend health...
timeout /t 10 /nobreak >nul
curl -s "%BACKEND_URL%/api/health" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend health check failed - service might still be starting up
) else (
    echo ✓ Backend health check passed!
)

REM Build frontend
echo [7/8] Building frontend...
cd /d "%~dp0frontend"

REM Update frontend environment with new backend URL
echo Updating frontend environment variables...
echo REACT_APP_API_URL="%BACKEND_URL%/api" > .env.production
echo REACT_APP_GOOGLE_CLIENT_ID="your_client_id_here" >> .env.production

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Frontend dependency installation failed.
        cd /d "%~dp0"
        pause
        exit /b 1
    )
)

REM Build frontend
echo Building frontend for production...
npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo ✓ Frontend build completed successfully!

REM Deploy frontend to Netlify
echo [8/8] Deploying frontend to Netlify...

REM Check if Netlify CLI is installed
netlify --version >nul 2>&1
if errorlevel 1 (
    echo Installing Netlify CLI...
    npm install -g netlify-cli
    if errorlevel 1 (
        echo ERROR: Failed to install Netlify CLI.
        echo Please install manually: npm install -g netlify-cli
        echo Then run: netlify deploy --prod --dir=build
        cd /d "%~dp0"
        pause
        exit /b 1
    )
)

REM Deploy to Netlify
echo Deploying to Netlify...
netlify deploy --prod --dir=build
if errorlevel 1 (
    echo ERROR: Netlify deployment failed.
    echo You can deploy manually by running:
    echo   cd frontend
    echo   netlify deploy --prod --dir=build
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo ✓ Frontend deployment completed successfully!

cd /d "%~dp0"

echo.
echo ========================================
echo    Deployment Summary
echo ========================================
echo ✓ Backend URL: %BACKEND_URL%
echo ✓ Backend Health: %BACKEND_URL%/api/health
echo ✓ Frontend: Deployed to Netlify
echo ✓ Frontend URL: https://ttsai.netlify.app
echo.
echo ⚠️  IMPORTANT: Update Google OAuth credentials
echo 1. Go to Google Cloud Console
echo 2. Update OAuth client with new URLs
echo 3. Update environment variables with real OAuth credentials
echo.
echo New features deployed:
echo ✓ Google Authentication
echo ✓ Redesigned Learning Tools Page
echo ✓ New Quiz System
echo ✓ Simplified Avatar Chatbot
echo ✓ Progress Tracking
echo ✓ Responsive Design
echo.
echo ========================================
echo    Deployment Complete!
echo ========================================
pause