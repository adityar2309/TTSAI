# Manual Deployment Instructions to Fix 503 Errors

## Problem
Your API key `AIzaSyCZd37vcyOUdxhQ5XWJrDCOkbRRDadf-OM` is invalid, causing 503 errors.

## Solution Steps

### Step 1: Get New API Key
1. Open: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select your project
4. Copy the new API key (starts with `AIzaSy...`)

### Step 2: Set Environment Variable
In PowerShell:
```powershell
$env:GEMINI_API_KEY = "YOUR_NEW_API_KEY_HERE"
```

In Command Prompt:
```cmd
set GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

### Step 3: Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project ttsai-476712
```

### Step 4: Deploy to Cloud Run
```bash
cd backend
gcloud run deploy ttsai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars GEMINI_API_KEY="AIzaSyDhFOZFdZZjoA-hgHrbW9waBtvoYSRY6nw",DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production \
  --port 5000
```

### Step 5: Test the Fix
```bash
cd ..
python test_backend.py
```

## Success Indicators
- Health check shows `'gemini': True`
- Translation tests pass (no more 503 errors)
- Your frontend translation feature works again

## Alternative: Quick Fix with gcloud
If you just want to update the environment variable without full redeploy:

```bash
gcloud run services update ttsai-backend \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

## Verification
After deployment, your service URL will be:
`https://ttsai-backend-321805997355.us-central1.run.app`

Test it:
- Health: https://ttsai-backend-321805997355.us-central1.run.app/api/health
- Should show `'gemini': True` instead of `'gemini': False` 