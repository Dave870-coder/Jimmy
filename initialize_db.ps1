# Initialize database on Render backend (PowerShell)
# This script calls the manual initialization endpoint

Write-Host "🚀 Database Initialization Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

$BACKEND_URL = "https://jimmy-ai-bot.onrender.com"
$MAX_RETRIES = 3
$RETRY_COUNT = 0

# Check if backend is running
Write-Host ""
Write-Host "1️⃣ Checking backend status..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$BACKEND_URL/health" -UseBasicParsing | ConvertFrom-Json
    Write-Host "   ✅ Backend is online"
    Write-Host "   Status: $($health.status)"
    Write-Host "   Database: $($health.database)"
} catch {
    Write-Host "   ❌ Backend is offline or unreachable" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "⚠️  Important: Make sure Render has deployed the latest code"
    Write-Host "   Steps:"
    Write-Host "   1. Visit: https://render.com/dashboard"
    Write-Host "   2. Select: jimmy-ai-bot service"
    Write-Host "   3. Click: Manual Deploy button"
    Write-Host "   4. Run this script again"
    exit 1
}

# Try to initialize database (with retries)
Write-Host ""
Write-Host "2️⃣ Initializing database..." -ForegroundColor Yellow

while ($RETRY_COUNT -lt $MAX_RETRIES) {
    try {
        Write-Host "   Attempt $($RETRY_COUNT + 1)/$MAX_RETRIES..."
        Write-Host "   Calling: POST $BACKEND_URL/initialize-db"
        
        $response = Invoke-WebRequest -Uri "$BACKEND_URL/initialize-db" `
            -Method POST `
            -ContentType "application/json" `
            -UseBasicParsing | ConvertFrom-Json
        
        Write-Host "   Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        
        if ($response.success) {
            Write-Host ""
            Write-Host "✅ Database initialized successfully!" -ForegroundColor Green
            Write-Host "   Message: $($response.message)"
            break
        } else {
            Write-Host "   ⚠️  Initialization returned success=false" -ForegroundColor Yellow
            Write-Host "   Message: $($response.message)"
            $RETRY_COUNT++
            if ($RETRY_COUNT -lt $MAX_RETRIES) {
                Write-Host "   Retrying in 3 seconds..."
                Start-Sleep -Seconds 3
            }
        }
    } catch {
        Write-Host "   Error: $_" -ForegroundColor Red
        $RETRY_COUNT++
        if ($RETRY_COUNT -lt $MAX_RETRIES) {
            Write-Host "   Retrying in 3 seconds..."
            Start-Sleep -Seconds 3
        }
    }
}

# Verify database status
Write-Host ""
Write-Host "3️⃣ Verifying database status..." -ForegroundColor Yellow
try {
    $health_new = Invoke-WebRequest -Uri "$BACKEND_URL/health" -UseBasicParsing | ConvertFrom-Json
    
    Write-Host "   Status: $($health_new.status)" -ForegroundColor Cyan
    Write-Host "   Database: $($health_new.database)" -ForegroundColor Cyan
    Write-Host "   Timestamp: $($health_new.timestamp)"
    
    if ($health_new.database -eq "ready") {
        Write-Host ""
        Write-Host "🎉 SUCCESS! Database is ready!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⏳ Database status: $($health_new.database)" -ForegroundColor Yellow
        Write-Host "   May still be initializing. Check again in 30 seconds."
    }
} catch {
    Write-Host "   Error checking status: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Expected Result:"
Write-Host "   • Health endpoint shows: {""database"": ""ready""}"
Write-Host "   • Dashboard should connect to backend"
Write-Host "   • Analytics/Users/Messages should load"
Write-Host ""
Write-Host "🔗 Check these URLs:"
Write-Host "   1. Backend Health: https://jimmy-ai-bot.onrender.com/health"
Write-Host "   2. Backend Ready: https://jimmy-ai-bot.onrender.com/ready"
Write-Host "   3. Dashboard: https://dave870-coder.github.io/Jimmy/"
