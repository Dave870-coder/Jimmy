#!/bin/bash
# Quick start script for the AI Bot Platform

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🚀 AI Bot Platform - Quick Start"
echo "================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)"
    echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo ""
    echo "Then run this script again!"
    exit 0
fi

mkdir -p data/chroma logs

if [ ! -d .venv ]; then
    if command -v python3 &> /dev/null; then
        python3 -m venv .venv
    else
        python -m venv .venv
    fi
fi

VENV_PYTHON=".venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
fi

if [ ! -x "$VENV_PYTHON" ] && [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Python virtual environment could not be created"
    exit 1
fi

echo "✅ Python environment ready"
echo ""

echo "📦 Installing dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -e .

echo ""
echo "🚀 Starting bot..."
"$VENV_PYTHON" start_bot.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Open Telegram and find your bot"
echo "2. Send /start to test the bot"
echo "3. API docs: http://localhost:8000/docs"
echo ""
