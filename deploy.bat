@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    TTSAI Backend Deployment Script
echo ========================================
echo.

REM Check if gcloud is installed and authenticated
echo [1/6] Checking Google Cloud CLI...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Google Cloud CLI not found. Please install gcloud CLI first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ✓ Google Cloud CLI found

REM Check authentication
echo [2/6] Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" | findstr "@" >nul
if errorlevel 1 (
    echo ERROR: Not authenticated with Google Cloud. Please run:
    echo   gcloud auth login
    echo   gcloud config set project ttsai-476712
    pause
    exit /b 1
)
echo ✓ Google Cloud authentication verified

REM Check if GEMINI_API_KEY is set
echo [3/6] Checking environment variables...
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY is not set. The backend will run with limited functionality.
    echo Set it with: set GEMINI_API_KEY=your_google_ai_studio_api_key_here
    echo Get your API key from: https://aistudio.google.com/app/apikey
    set /p continue="Continue deployment anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo Deployment cancelled.
        pause
        exit /b 1
    )
) else (
    echo ✓ GEMINI_API_KEY is set: %GEMINI_API_KEY:~0,8%...
)

REM Change to backend directory
echo [4/6] Building Docker image...
cd /d "%~dp0backend"
if not exist "Dockerfile" (
    echo ERROR: Dockerfile not found in backend directory.
    cd /d "%~dp0"
    pause
    exit /b 1
)

REM Build and push using Cloud Build for faster, more reliable builds
echo Building with Cloud Build (faster than local Docker build)...
gcloud builds submit --tag gcr.io/ttsai-476712/ttsai-backend:latest .
if errorlevel 1 (
    echo ERROR: Docker build failed.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo ✓ Docker image built and pushed successfully

REM Deploy to Cloud Run
echo [5/6] Deploying to Cloud Run...
cd /d "%~dp0"

REM Set environment variables for deployment
if "%GEMINI_API_KEY%"=="" (
    set "ENV_VARS=DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production"
) else (
    set "ENV_VARS=GEMINI_API_KEY=%GEMINI_API_KEY%,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production"
)

echo Deploying with configuration:
echo   - Image: gcr.io/ttsai-476712/ttsai-backend:latest
echo   - Region: us-central1
echo   - Memory: 2Gi
echo   - CPU: 2
echo   - Max instances: 100
echo   - Min instances: 0
echo   - Environment: Using Google AI Studio (Gemini)

gcloud run deploy ttsai-backend ^
  --image gcr.io/ttsai-476712/ttsai-backend:latest ^
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
    echo ERROR: Cloud Run deployment failed.
    pause
    exit /b 1
)

echo [6/6] Testing deployment...
echo ✓ Deployment completed successfully!
echo.

REM Get the service URL
echo Getting service URL...
for /f "tokens=*" %%i in ('gcloud run services describe ttsai-backend --region=us-central1 --format="value(status.url)"') do set SERVICE_URL=%%i

if not "%SERVICE_URL%"=="" (
    echo.
    echo ========================================
    echo    Deployment Summary
    echo ========================================
    echo ✓ Backend URL: %SERVICE_URL%
    echo ✓ Health Check: %SERVICE_URL%/api/health
    echo ✓ Testing with basic request...
    
    REM Wait for service to be ready
    echo Waiting for service to start up...
    timeout /t 10 /nobreak >nul
    
    REM Test the health endpoint
    curl -s "%SERVICE_URL%/api/health" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Health check failed - service might still be starting up
        echo   Wait a minute and test manually: %SERVICE_URL%/api/health
    ) else (
        echo ✓ Health check passed!
    )
    
    echo.
    echo Next steps:
    echo 1. Update frontend API_BASE_URL to: %SERVICE_URL%/api
    echo 2. Test the learning tools with: python test_learning_tools_deployed.py
    echo 3. Redeploy frontend if needed
    echo.
    echo To set your API key for next time:
    echo set GEMINI_API_KEY=your_google_ai_studio_api_key_here
) else (
    echo ⚠️  Could not retrieve service URL. Check deployment manually.
)

echo.
echo ========================================
echo    Deployment Complete!
echo ========================================
pause 