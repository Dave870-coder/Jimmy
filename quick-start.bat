@echo off
REM Quick start script for the AI Bot Platform (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 AI Bot Platform - Quick Start (Windows)
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Edit .env and add your API keys:
    echo    - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)
    echo    - TELEGRAM_BOT_TOKEN (from @BotFather)
    echo.
    echo Then run this script again!
    pause
    exit /b 0
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    echo    Install Docker Desktop from: https://docker.com
    pause
    exit /b 1
)

echo ✅ Docker is installed
echo.

REM Start services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services
echo ⏳ Waiting for services to start ^(30 seconds^)...
timeout /t 30 /nobreak

REM Check services
echo.
echo 🏥 Checking service health...
docker-compose ps

REM Test API
echo.
echo 🧪 Testing API health...
for /f %%i in ('curl -s http://localhost:8000/health 2^>nul') do set response=%%i

if "%response%" neq "" (
    echo ✅ API is responding!
) else (
    echo ⚠️  API might still be starting...
)

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Open Telegram and find your bot
echo 2. Send /start to test the bot
echo 3. View logs: docker-compose logs -f api
echo 4. API docs: http://localhost:8000/docs
echo.
echo 💡 To stop services: docker-compose down
echo.
pause
