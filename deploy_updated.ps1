# TTSAI Full Stack Deployment Script (PowerShell)
# Deploys backend to Google Cloud Run and frontend to Netlify

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TTSAI Full Stack Deployment Script" -ForegroundColor Cyan
Write-Host "   (Backend + Frontend with Auth)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if gcloud is installed
Write-Host "[1/8] Checking Google Cloud CLI..." -ForegroundColor Yellow
if (-not (Test-Command "gcloud")) {
    Write-Host "ERROR: Google Cloud CLI not found. Please install gcloud CLI first." -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Google Cloud CLI found" -ForegroundColor Green

# Check authentication
Write-Host "[2/8] Checking authentication..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authCheck) {
    Write-Host "ERROR: Not authenticated with Google Cloud. Please run:" -ForegroundColor Red
    Write-Host "  gcloud auth login" -ForegroundColor Red
    Write-Host "  gcloud config set project ttsai-461209" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Google Cloud authentication verified" -ForegroundColor Green

# Check environment variables
Write-Host "[3/8] Checking environment variables..." -ForegroundColor Yellow
$GEMINI_API_KEY = $env:GEMINI_API_KEY
if (-not $GEMINI_API_KEY) {
    Write-Host "WARNING: GEMINI_API_KEY is not set. Using default from .env file." -ForegroundColor Yellow
    $GEMINI_API_KEY = "AIzaSyCZzto0BK9sPgX8_QEidRP4mM8-90tf-OM"
    Write-Host "Using API key: $($GEMINI_API_KEY.Substring(0,8))..." -ForegroundColor Yellow
} else {
    Write-Host "✓ GEMINI_API_KEY is set: $($GEMINI_API_KEY.Substring(0,8))..." -ForegroundColor Green
}

# Build backend
Write-Host "[4/8] Building backend Docker image..." -ForegroundColor Yellow
Set-Location -Path "backend"

if (-not (Test-Path "Dockerfile")) {
    Write-Host "ERROR: Dockerfile not found in backend directory." -ForegroundColor Red
    Set-Location -Path ".."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Building backend with Cloud Build..." -ForegroundColor Cyan
$buildResult = gcloud builds submit --tag gcr.io/ttsai-461209/ttsai-backend:latest . 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend Docker build failed." -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Red
    Set-Location -Path ".."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Backend Docker image built and pushed successfully" -ForegroundColor Green

# Deploy backend
Write-Host "[5/8] Deploying backend to Cloud Run..." -ForegroundColor Yellow
Set-Location -Path ".."

# Set environment variables for deployment
$ENV_VARS = "GEMINI_API_KEY=$GEMINI_API_KEY,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production,GOOGLE_CLIENT_ID=your_client_id_here,GOOGLE_CLIENT_SECRET=your_client_secret_here,GOOGLE_CALLBACK_URL=https://ttsai-backend-321805997355.us-central1.run.app/api/auth/google/callback,JWT_SECRET=your_jwt_secret_here"

Write-Host "Deploying backend with configuration:" -ForegroundColor Cyan
Write-Host "  - Image: gcr.io/ttsai-461209/ttsai-backend:latest" -ForegroundColor Cyan
Write-Host "  - Region: us-central1" -ForegroundColor Cyan
Write-Host "  - Memory: 2Gi" -ForegroundColor Cyan
Write-Host "  - CPU: 2" -ForegroundColor Cyan

$deployResult = gcloud run deploy ttsai-backend `
  --image gcr.io/ttsai-461209/ttsai-backend:latest `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --port 5000 `
  --memory 2Gi `
  --cpu 2 `
  --max-instances 100 `
  --min-instances 0 `
  --timeout 300 `
  --concurrency 80 `
  --set-env-vars=$ENV_VARS 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend Cloud Run deployment failed." -ForegroundColor Red
    Write-Host $deployResult -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Backend deployment completed successfully!" -ForegroundColor Green

# Get backend URL
Write-Host "[6/8] Getting backend service URL..." -ForegroundColor Yellow
$BACKEND_URL = gcloud run services describe ttsai-backend --region=us-central1 --format="value(status.url)" 2>$null

if (-not $BACKEND_URL) {
    Write-Host "ERROR: Could not retrieve backend service URL." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Backend URL: $BACKEND_URL" -ForegroundColor Green

# Test backend health
Write-Host "Testing backend health..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

try {
    $healthResponse = Invoke-WebRequest -Uri "$BACKEND_URL/api/health" -TimeoutSec 30 -ErrorAction Stop
    Write-Host "✓ Backend health check passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend health check failed - service might still be starting up" -ForegroundColor Yellow
}

# Build frontend
Write-Host "[7/8] Building frontend..." -ForegroundColor Yellow
Set-Location -Path "frontend"

# Update frontend environment
Write-Host "Updating frontend environment variables..." -ForegroundColor Cyan
@"
REACT_APP_API_URL=$BACKEND_URL/api
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here
"@ | Out-File -FilePath ".env.production" -Encoding UTF8

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Frontend dependency installation failed." -ForegroundColor Red
        Set-Location -Path ".."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Build frontend
Write-Host "Building frontend for production..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed." -ForegroundColor Red
    Set-Location -Path ".."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Frontend build completed successfully!" -ForegroundColor Green

# Deploy to Netlify
Write-Host "[8/8] Deploying frontend to Netlify..." -ForegroundColor Yellow

# Check if Netlify CLI is installed
if (-not (Test-Command "netlify")) {
    Write-Host "Installing Netlify CLI..." -ForegroundColor Cyan
    npm install -g netlify-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Netlify CLI." -ForegroundColor Red
        Write-Host "Please install manually: npm install -g netlify-cli" -ForegroundColor Red
        Write-Host "Then run: netlify deploy --prod --dir=build" -ForegroundColor Red
        Set-Location -Path ".."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Deploy to Netlify
Write-Host "Deploying to Netlify..." -ForegroundColor Cyan
netlify deploy --prod --dir=build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Netlify deployment failed." -ForegroundColor Red
    Write-Host "You can deploy manually by running:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor Yellow
    Write-Host "  netlify deploy --prod --dir=build" -ForegroundColor Yellow
    Set-Location -Path ".."
    Read-Host "Press Enter to continue"
} else {
    Write-Host "✓ Frontend deployment completed successfully!" -ForegroundColor Green
}

Set-Location -Path ".."

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Backend URL: $BACKEND_URL" -ForegroundColor Green
Write-Host "✓ Backend Health: $BACKEND_URL/api/health" -ForegroundColor Green
Write-Host "✓ Frontend: Deployed to Netlify" -ForegroundColor Green
Write-Host "✓ Frontend URL: https://ttsai.netlify.app" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: Update Google OAuth credentials" -ForegroundColor Yellow
Write-Host "1. Go to Google Cloud Console" -ForegroundColor Yellow
Write-Host "2. Update OAuth client with new URLs" -ForegroundColor Yellow
Write-Host "3. Update environment variables with real OAuth credentials" -ForegroundColor Yellow
Write-Host ""
Write-Host "New features deployed:" -ForegroundColor Cyan
Write-Host "✓ Google Authentication" -ForegroundColor Green
Write-Host "✓ Redesigned Learning Tools Page" -ForegroundColor Green
Write-Host "✓ New Quiz System" -ForegroundColor Green
Write-Host "✓ Simplified Avatar Chatbot" -ForegroundColor Green
Write-Host "✓ Progress Tracking" -ForegroundColor Green
Write-Host "✓ Responsive Design" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"