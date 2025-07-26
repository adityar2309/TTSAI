@echo off
echo ========================================
echo Pushing TTSAI with Authentication to GitHub
echo ========================================
echo.

echo Checking git status...
git status

echo.
echo Adding all files...
git add .

echo.
echo Committing changes...
git commit -m "Implement complete authentication system with Google OAuth

- Add Google OAuth integration for backend and frontend
- Implement JWT-based session management
- Add user database models and operations
- Create comprehensive auth components for React
- Add authentication middleware and route protection
- Include deployment scripts for Google Cloud and Netlify
- Add testing and setup automation scripts
- Update CORS configuration for production
- Add comprehensive documentation and guides"

echo.
echo Pushing to GitHub...
git push origin master

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Successfully pushed to GitHub!
    echo.
    echo Next steps:
    echo 1. Set up Google OAuth credentials: python setup_google_oauth.py
    echo 2. Test authentication: python test_auth_integration.py
    echo 3. Deploy to production: python deploy_with_auth.py
) else (
    echo.
    echo ❌ Failed to push to GitHub!
    echo Please check your git configuration and try again.
)

echo.
pause