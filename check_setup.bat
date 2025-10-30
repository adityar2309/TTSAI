@echo off
echo Checking deployment prerequisites...
echo.

echo 1. Checking Google Cloud CLI...
gcloud --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Google Cloud CLI not found. Please install from https://cloud.google.com/sdk/docs/install
    exit /b 1
)

echo.
echo 2. Checking authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Not authenticated. Run: gcloud auth login
    exit /b 1
)

echo.
echo 3. Checking current project...
gcloud config get-value project
if %ERRORLEVEL% neq 0 (
    echo ERROR: No project set. Run: gcloud config set project ttsai-476712
    exit /b 1
)

echo.
echo 4. Checking GEMINI_API_KEY...
if "%GEMINI_API_KEY%"=="" (
    echo ERROR: GEMINI_API_KEY environment variable not set
    echo Please set it with: set GEMINI_API_KEY=your_api_key_here
    exit /b 1
) else (
    echo GEMINI_API_KEY is set (length: %GEMINI_API_KEY:~0,8%...)
)

echo.
echo 5. Checking Docker...
docker --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker not found. Please install Docker Desktop
    exit /b 1
)

echo.
echo ✅ All prerequisites met! Ready for deployment.
echo Run deploy.bat to start deployment. 