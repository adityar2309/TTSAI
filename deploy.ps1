# TTSAI Backend Deployment Script (PowerShell)
# Enhanced deployment with better error handling and validation

param(
    [switch]$SkipTests,
    [switch]$Force
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    TTSAI Backend Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to test URL
function Test-Url($url) {
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -ErrorAction Stop
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

try {
    # Step 1: Check prerequisites
    Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
    
    if (!(Test-Command "gcloud")) {
        Write-Host "ERROR: Google Cloud CLI not found. Please install gcloud CLI first." -ForegroundColor Red
        Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Google Cloud CLI found" -ForegroundColor Green
    
    # Step 2: Check authentication
    Write-Host "[2/6] Checking authentication..." -ForegroundColor Yellow
    
    $authList = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (!$authList) {
        Write-Host "ERROR: Not authenticated with Google Cloud. Please run:" -ForegroundColor Red
        Write-Host "  gcloud auth login" -ForegroundColor Yellow
        Write-Host "  gcloud config set project ttsai-461209" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✓ Authenticated as: $authList" -ForegroundColor Green
    
    # Step 3: Check environment variables
    Write-Host "[3/6] Checking environment variables..." -ForegroundColor Yellow
    
    $geminiKey = $env:GEMINI_API_KEY
    if (!$geminiKey) {
        Write-Host "WARNING: GEMINI_API_KEY is not set. The backend will run with limited functionality." -ForegroundColor Yellow
        Write-Host "Set it with: `$env:GEMINI_API_KEY = 'your_api_key_here'" -ForegroundColor Yellow
        
        if (!$Force) {
            $continue = Read-Host "Continue deployment anyway? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-Host "Deployment cancelled." -ForegroundColor Red
                exit 1
            }
        }
    } else {
        $keyPreview = $geminiKey.Substring(0, [Math]::Min(8, $geminiKey.Length)) + "..."
        Write-Host "✓ GEMINI_API_KEY is set: $keyPreview" -ForegroundColor Green
    }
    
    # Step 4: Build Docker image
    Write-Host "[4/6] Building Docker image..." -ForegroundColor Yellow
    
    $backendPath = Join-Path $PSScriptRoot "backend"
    if (!(Test-Path "$backendPath\Dockerfile")) {
        Write-Host "ERROR: Dockerfile not found in backend directory." -ForegroundColor Red
        exit 1
    }
    
    Push-Location $backendPath
    try {
        Write-Host "Building with Cloud Build (faster than local Docker build)..." -ForegroundColor Cyan
        $buildResult = gcloud builds submit --tag gcr.io/ttsai-461209/ttsai-backend:latest . 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Docker build failed." -ForegroundColor Red
            Write-Host $buildResult -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ Docker image built and pushed successfully" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
    
    # Step 5: Deploy to Cloud Run
    Write-Host "[5/6] Deploying to Cloud Run..." -ForegroundColor Yellow
    
    # Set environment variables for deployment
    if ($geminiKey) {
        $envVars = "GEMINI_API_KEY=$geminiKey,DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production"
    } else {
        $envVars = "DATABASE_URL=sqlite:///app/ttsai.db,FLASK_ENV=production"
    }
    
    Write-Host "Deploying with configuration:" -ForegroundColor Cyan
    Write-Host "  - Image: gcr.io/ttsai-461209/ttsai-backend:latest"
    Write-Host "  - Region: us-central1"
    Write-Host "  - Memory: 2Gi"
    Write-Host "  - CPU: 2"
    Write-Host "  - Max instances: 100"
    Write-Host "  - Min instances: 0"
    Write-Host "  - Environment variables: $($envVars.Split(',').Count) variables set"
    
    $deployArgs = @(
        "run", "deploy", "ttsai-backend",
        "--image", "gcr.io/ttsai-461209/ttsai-backend:latest",
        "--platform", "managed",
        "--region", "us-central1",
        "--allow-unauthenticated",
        "--port", "5000",
        "--memory", "2Gi",
        "--cpu", "2",
        "--max-instances", "100",
        "--min-instances", "0",
        "--timeout", "300",
        "--concurrency", "80",
        "--set-env-vars", $envVars
    )
    
    $deployResult = & gcloud @deployArgs 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cloud Run deployment failed." -ForegroundColor Red
        Write-Host $deployResult -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green
    
    # Step 6: Test deployment
    Write-Host "[6/6] Testing deployment..." -ForegroundColor Yellow
    
    # Get service URL
    $serviceUrl = gcloud run services describe ttsai-backend --region=us-central1 --format="value(status.url)" 2>$null
    
    if ($serviceUrl) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "    Deployment Summary" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "✓ Backend URL: $serviceUrl" -ForegroundColor Green
        Write-Host "✓ Health Check: $serviceUrl/api/health" -ForegroundColor Green
        
        if (!$SkipTests) {
            Write-Host "✓ Testing health endpoint..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5  # Wait for service to start
            
            if (Test-Url "$serviceUrl/api/health") {
                Write-Host "✓ Health check passed!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Health check failed - service might still be starting up" -ForegroundColor Yellow
                Write-Host "   Wait a minute and test manually: $serviceUrl/api/health" -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Update frontend API_BASE_URL to: $serviceUrl/api"
        Write-Host "2. Test the learning tools with: python test_learning_tools_deployed.py"
        Write-Host "3. Redeploy frontend if needed"
        
        # Update the test file automatically
        $testFile = Join-Path $PSScriptRoot "test_learning_tools_deployed.py"
        if (Test-Path $testFile) {
            try {
                $content = Get-Content $testFile -Raw
                $pattern = "API_BASE = '[^']*'"
                $replacement = "API_BASE = '" + $serviceUrl + "/api'"
                $newContent = $content -replace $pattern, $replacement
                Set-Content $testFile -Value $newContent -NoNewline
                Write-Host "✓ Updated test_learning_tools_deployed.py with new API URL" -ForegroundColor Green
            }
            catch {
                Write-Host "⚠️  Could not update test file automatically" -ForegroundColor Yellow
            }
        }
        
    } else {
        Write-Host "⚠️  Could not retrieve service URL. Check deployment manually." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Deployment Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}
catch {
    Write-Host "ERROR: Deployment failed with exception:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Pause only if running interactively
if ($Host.Name -eq "ConsoleHost") {
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 