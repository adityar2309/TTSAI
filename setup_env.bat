@echo off
echo ========================================
echo    TTSAI Environment Setup
echo ========================================
echo.

echo This script will help you set up your environment variables for TTSAI.
echo.
echo You need a Google AI Studio API key to use the translation features.
echo Get your free API key from: https://aistudio.google.com/app/apikey
echo.

set /p API_KEY="Enter your Google AI Studio API key: "

if "%API_KEY%"=="" (
    echo No API key provided. Exiting.
    pause
    exit /b 1
)

echo.
echo Setting environment variable...
set GEMINI_API_KEY=%API_KEY%

echo ✓ GEMINI_API_KEY has been set for this session.
echo.
echo To make this permanent, you can either:
echo 1. Add it to your system environment variables, or
echo 2. Create a .env file in the backend directory with:
echo    GEMINI_API_KEY=%API_KEY%
echo.
echo Current API key: %API_KEY:~0,8%...
echo.
echo You can now run deploy.bat to deploy your backend!
echo.
pause 