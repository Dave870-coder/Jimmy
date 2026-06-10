@echo off
REM One-Click Deployment Script for Jimmy AI Bot Platform (Windows)
REM This script prepares your bot for deployment to Render

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Jimmy AI Bot - Deploy to Render (LIVE!)
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if Git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git found
echo.

REM Run the deployment script
echo Starting deployment wizard...
echo.
python deploy_to_render_live.py

if errorlevel 1 (
    echo.
    echo ERROR: Deployment script failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Your app is ready for Render
echo ========================================
echo.
echo Next steps:
echo 1. Go to: https://dashboard.render.com
echo 2. Create a new Web Service
echo 3. Connect your GitHub repository
echo 4. Add environment variables (see RENDER_DEPLOYMENT_INSTRUCTIONS.txt)
echo 5. Deploy!
echo.
pause
