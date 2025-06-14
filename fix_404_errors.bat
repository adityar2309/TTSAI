@echo off
echo ========================================
echo    TTSAI 404 Error Fix Script
echo ========================================
echo.
echo This script will fix the 404 errors by redeploying the backend
echo with the latest code that includes all learning tools endpoints.
echo.

echo Step 1: Checking gcloud authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ You need to authenticate with Google Cloud first.
    echo Please run: gcloud auth login
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✅ Google Cloud authentication found.
echo.

echo Step 2: Setting project configuration...
gcloud config set project ttsai-backend
echo.

echo Step 3: Deploying backend with latest code...
cd backend
gcloud run deploy ttsai-backend ^
  --source . ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --memory 2Gi ^
  --cpu 2 ^
  --set-env-vars=ENVIRONMENT=production ^
  --port 8080

if %ERRORLEVEL% neq 0 (
    echo ❌ Deployment failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Step 4: Testing deployment...
cd ..
echo Testing basic health check...
curl -s "https://ttsai-backend-321805997355.us-central1.run.app/api/health" | findstr "healthy" > nul
if %ERRORLEVEL% equ 0 (
    echo ✅ Health check passed
) else (
    echo ❌ Health check failed
)

echo.
echo Step 5: Initializing database with word-of-day data...
curl -X POST "https://ttsai-backend-321805997355.us-central1.run.app/api/debug/populate-words"
echo.

echo Step 6: Running comprehensive tests...
python3 test_learning_tools_deployed.py

echo.
echo ========================================
echo          Fix Complete!
echo ========================================
echo.
echo The 404 errors should now be resolved.
echo Your frontend should now be able to connect to all backend endpoints.
echo.
pause 