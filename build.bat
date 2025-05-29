@echo off
echo Building frontend with production API URL...
set REACT_APP_API_URL=https://ttsai-backend-321805997355.us-central1.run.app/api
npm run build
echo Build complete! 