@echo off
echo ========================================
echo TTSAI Authentication Setup and Deployment
echo ========================================
echo.

echo Step 1: Setting up Google OAuth credentials...
python setup_google_oauth.py
if %ERRORLEVEL% neq 0 (
    echo Failed to setup OAuth credentials!
    pause
    exit /b 1
)

echo.
echo Step 2: Testing authentication integration...
python test_auth_integration.py
if %ERRORLEVEL% neq 0 (
    echo Authentication tests failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Starting deployment process...
python deploy_with_auth.py
if %ERRORLEVEL% neq 0 (
    echo Deployment failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup and deployment completed successfully!
echo ========================================
pause