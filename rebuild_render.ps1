#!/usr/bin/env powershell
<#
.SYNOPSIS
Automatically trigger Render rebuild and wait for it to complete
.DESCRIPTION
This script uses Render's API to manually deploy the latest code
.PARAMETER ApiKey
Your Render API key from https://dashboard.render.com/account/api-keys
#>

param(
    [string]$ApiKey,
    [string]$ServiceId = "srv_ppngm15lftpc73nph7r0"  # jimmy-ai-bot service
)

if (-not $ApiKey) {
    Write-Host "❌ Error: API key required" -ForegroundColor Red
    Write-Host ""
    Write-Host "Get your Render API key:"
    Write-Host "1. Go to https://dashboard.render.com/account/api-keys"
    Write-Host "2. Click 'Create API Key'"
    Write-Host "3. Copy the key"
    Write-Host ""
    Write-Host "Usage: .\rebuild_render.ps1 -ApiKey 'your-api-key-here'"
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}

Write-Host "🔄 Triggering Render rebuild..." -ForegroundColor Cyan

# Trigger manual deploy
$deployUrl = "https://api.render.com/v1/services/$ServiceId/deploys"
$body = @{
    "clearCache" = "clear"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $deployUrl -Method POST -Headers $headers -Body $body
    Write-Host "✅ Deploy triggered: $($response.id)" -ForegroundColor Green
    
    $deployId = $response.id
    
    # Wait for deploy to complete
    Write-Host "⏳ Waiting for rebuild to complete (this may take 2-3 minutes)..." -ForegroundColor Yellow
    
    $maxWait = 300  # 5 minutes
    $elapsed = 0
    $checkInterval = 5
    
    while ($elapsed -lt $maxWait) {
        Start-Sleep -Seconds $checkInterval
        $elapsed += $checkInterval
        
        $statusUrl = "https://api.render.com/v1/services/$ServiceId/deploys/$deployId"
        $deploy = Invoke-RestMethod -Uri $statusUrl -Method GET -Headers $headers
        
        $status = $deploy.status
        Write-Host "  Status: $status... ($elapsed seconds)" -ForegroundColor Cyan
        
        if ($status -eq "live") {
            Write-Host "✅ Deploy completed and live!" -ForegroundColor Green
            
            # Wait a moment for app to fully initialize
            Write-Host "⏳ Waiting for app to initialize..."
            Start-Sleep -Seconds 5
            
            # Check database status
            Write-Host "🔍 Checking database status..." -ForegroundColor Cyan
            $health = Invoke-WebRequest -Uri "https://jimmy-ai-bot.onrender.com/health" -UseBasicParsing
            $healthData = $health.Content | ConvertFrom-Json
            
            if ($healthData.database -eq "ready") {
                Write-Host "✅ SUCCESS! Database is ready!" -ForegroundColor Green
                Write-Host ""
                Write-Host "Frontend: https://dave870-coder.github.io/Jimmy/"
                Write-Host "Backend:  https://jimmy-ai-bot.onrender.com/health"
            } else {
                Write-Host "⚠️  Database status: $($healthData.database)" -ForegroundColor Yellow
                Write-Host "Trying to initialize database..." -ForegroundColor Cyan
                
                $init = Invoke-WebRequest -Uri "https://jimmy-ai-bot.onrender.com/initialize-db" -Method POST -UseBasicParsing
                $initData = $init.Content | ConvertFrom-Json
                
                if ($initData.success) {
                    Write-Host "✅ Database initialized successfully!" -ForegroundColor Green
                } else {
                    Write-Host "❌ Database initialization failed: $($initData.message)" -ForegroundColor Red
                }
            }
            
            exit 0
        } elseif ($status -eq "failed" -or $status -eq "canceled") {
            Write-Host "❌ Deploy failed with status: $status" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "❌ Deploy timeout after $maxWait seconds" -ForegroundColor Red
    exit 1
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "- Verify API key is correct"
    Write-Host "- Check https://dashboard.render.com/dashboard"
    Write-Host "- Look for Render service errors in the logs"
    exit 1
}
