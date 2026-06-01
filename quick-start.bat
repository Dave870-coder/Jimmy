@echo off
REM Quick start script for the AI Bot Platform (Windows)

setlocal enabledelayedexpansion
set "ROOT=%~dp0"
pushd "%ROOT%"

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
    popd
    exit /b 0
)

REM Create runtime directories
if not exist data mkdir data
if not exist data\chroma mkdir data\chroma
if not exist logs mkdir logs

REM Create virtual environment if needed
if not exist .venv\Scripts\python.exe (
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo ❌ Python virtual environment could not be created
    pause
    popd
    exit /b 1
)

echo ✅ Python environment ready
echo.

echo 📦 Installing dependencies...
"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -e .

echo.
echo 🚀 Starting bot...
"%PYTHON%" start_bot.py

popd
