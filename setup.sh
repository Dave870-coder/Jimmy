#!/bin/bash
# Quick setup script for GitHub deployment

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🚀 AI Bot Platform - GitHub Setup Script"
echo "=========================================="

echo ""
echo "📋 Checking prerequisites..."
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python 3 not found. Install Python 3.12 or higher."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install git."
    exit 1
fi

echo "✅ Python $($PYTHON_CMD --version | cut -d' ' -f2) found"
echo "✅ Git found"

echo ""
echo "📁 Creating data directories..."
mkdir -p data/chroma logs
echo "✅ Directories created"

echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    "$PYTHON_CMD" -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  .venv already exists, skipping..."
fi

VENV_PYTHON=".venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
fi

if [ ! -x "$VENV_PYTHON" ] && [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Could not locate virtual environment Python"
    exit 1
fi

echo ""
echo "📥 Installing dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -e .
echo "✅ Dependencies installed"

echo ""
echo "🔐 Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env created (edit with your API keys)"
    echo ""
    echo "📝 You need to add:"
    echo "   - GOOGLE_API_KEY (create it in Google AI Studio: https://aistudio.google.com/)"
    echo "   - TELEGRAM_BOT_TOKEN (from @BotFather on Telegram)"
    echo "   - SECRET_KEY (generate a strong random value for production)"
else
    echo "✅ .env already exists"
fi

echo ""
echo "💾 Preparing database directory..."
mkdir -p data
touch data/bot.db 2>/dev/null || true
echo "✅ Database directory ready"

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start the bot:"
echo "   $VENV_PYTHON start_bot.py"
echo ""
echo "3. Test locally:"
echo "   python local_test.py"
echo ""
echo "4. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial setup'"
echo "   git push origin main"
echo ""
echo "5. Deploy to Render:"
echo "   Set GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN, SECRET_KEY, APP_ENV=production, DEBUG=False"
echo "   Render auto-deploys after GitHub push"
echo ""
echo "🚀 Your AI Bot is ready!"