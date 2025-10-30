@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    TTSAI Backend Deployment Script
echo ========================================
echo.

REM Check if gcloud is installed and authenticated
echo [1/4] Checking Google Cloud CLI...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Google Cloud CLI not found. Please install gcloud CLI first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo ✓ Google Cloud CLI found

REM Check authentication
echo [2/4] Checking authentication...
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
echo [3/4] Checking environment variables...
if "%GEMINI_API_KEY%"=="" (
    echo Using default GEMINI_API_KEY from .env file
    set "GEMINI_API_KEY=AIzaSyCZzto0BK9sPgX8_QEidRP4mM8-90tf-OM"
) else (
    echo ✓ GEMINI_API_KEY is set: %GEMINI_API_KEY:~0,8%...
)

REM Change to backend directory
echo [4/4] Deploying to Cloud Run...
cd /d "%~dp0backend"
if not exist "Dockerfile" (
    echo ERROR: Dockerfile not found in backend directory.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo Deploying with configuration:
echo   - Region: us-central1
echo   - Memory: 2Gi
echo   - CPU: 2
echo   - Environment: Using Google AI Studio (Gemini)

REM Deploy directly from source code
gcloud run deploy ttsai-backend ^
  --source . ^
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
  --set-env-vars GEMINI_API_KEY=%GEMINI_API_KEY%,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production

if errorlevel 1 (
    echo ERROR: Cloud Run deployment failed.
    cd /d "%~dp0"
    pause
    exit /b 1
)

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
) else (
    echo ⚠️  Could not retrieve service URL. Check deployment manually.
)

cd /d "%~dp0"
echo.
echo ========================================
echo    Deployment Complete!
echo ========================================
pause