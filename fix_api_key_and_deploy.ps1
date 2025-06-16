# Fix Invalid API Key and Redeploy TTSAI Backend
# This script will guide you through replacing the invalid API key and redeploying

Write-Host "========================================" -ForegroundColor Red
Write-Host "  FIXING 503 SERVICE UNAVAILABLE ERRORS" -ForegroundColor Red  
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "PROBLEM IDENTIFIED:" -ForegroundColor Yellow
Write-Host "Your current API key 'AIzaSyCZd37vcyOUdxhQ5XWJrDCOkbRRDadf-OM' is INVALID" -ForegroundColor Red
Write-Host "This is causing all translation requests to return 503 errors." -ForegroundColor Red
Write-Host ""

# Step 1: Get new API key
Write-Host "STEP 1: GET A NEW API KEY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Open this URL in your browser:" -ForegroundColor White
Write-Host "   https://aistudio.google.com/app/apikey" -ForegroundColor Blue
Write-Host ""
Write-Host "2. Click 'Create API Key'" -ForegroundColor White
Write-Host "3. Select your project (or create new one)" -ForegroundColor White  
Write-Host "4. Copy the new API key (starts with 'AIzaSy...')" -ForegroundColor White
Write-Host ""

# Get new API key from user
do {
    $newApiKey = Read-Host "Enter your NEW API key"
    
    if ($newApiKey.Length -lt 20) {
        Write-Host "ERROR: API key seems too short. Please check and try again." -ForegroundColor Red
        continue
    }
    
    if (!$newApiKey.StartsWith("AIzaSy")) {
        Write-Host "WARNING: API key doesn't start with 'AIzaSy'. Are you sure this is correct?" -ForegroundColor Yellow
        $confirm = Read-Host "Continue anyway? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            continue
        }
    }
    
    break
} while ($true)

Write-Host ""
Write-Host "✓ API key received: $($newApiKey.Substring(0,10))..." -ForegroundColor Green

# Step 2: Test the new API key
Write-Host ""
Write-Host "STEP 2: TESTING NEW API KEY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Set environment variable
    $env:GEMINI_API_KEY = $newApiKey
    
    # Test the key with our diagnostic script
    Write-Host "Testing API key with Gemini..." -ForegroundColor Yellow
    
    $testResult = python test_gemini_direct.py 2>&1
    
    if ($testResult -match "✅.*Gemini API working") {
        Write-Host "✓ NEW API KEY IS WORKING!" -ForegroundColor Green
    } else {
        Write-Host "❌ New API key test failed:" -ForegroundColor Red
        Write-Host $testResult -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check your API key and try again." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Error testing API key: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Deploy with new API key
Write-Host ""
Write-Host "STEP 3: DEPLOYING WITH NEW API KEY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Starting deployment with your new API key..." -ForegroundColor Yellow
Write-Host ""

try {
    # Run the deployment script with the new API key
    .\deploy.ps1 -Force
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 SUCCESS! Deployment completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "VERIFICATION STEPS:" -ForegroundColor Cyan
        Write-Host "1. Test your backend:" -ForegroundColor White
        Write-Host "   python test_backend.py" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2. Test in your frontend app:" -ForegroundColor White
        Write-Host "   - Open your React app" -ForegroundColor Yellow
        Write-Host "   - Try translating some text" -ForegroundColor Yellow
        Write-Host "   - The 503 errors should be gone!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "3. If frontend still shows old URL:" -ForegroundColor White
        Write-Host "   - Hard refresh (Ctrl+F5)" -ForegroundColor Yellow
        Write-Host "   - Clear browser cache" -ForegroundColor Yellow
        
    } else {
        Write-Host "❌ Deployment failed. Check the error messages above." -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Deployment error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  503 ERRORS SHOULD NOW BE FIXED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green 