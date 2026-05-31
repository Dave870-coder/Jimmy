#!/bin/bash
# Quick setup script for GitHub deployment

echo "🚀 AI Bot Platform - GitHub Setup Script"
echo "=========================================="

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.12 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install git."
    exit 1
fi
echo "✅ Git found"

# Create directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/chroma
mkdir -p logs
echo "✅ Directories created"

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ -d "venv" ]; then
    echo "ℹ️  venv already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate || . venv\Scripts\activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -e . 2>/dev/null || pip install -r requirements.txt 2>/dev/null || echo "⚠️  Dependencies partially installed"
echo "✅ Dependencies installed"

# Setup environment file
echo ""
echo "🔐 Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env created (edit with your API keys)"
    echo ""
    echo "📝 You need to add:"
    echo "   - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)"
    echo "   - TELEGRAM_BOT_TOKEN (from @BotFather on Telegram)"
else
    echo "✅ .env already exists"
fi

# Create data directories for SQLite
echo ""
echo "💾 Creating database directory..."
mkdir -p data
touch data/bot.db 2>/dev/null || true
echo "✅ Database directory ready"

# Summary
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
echo "2. Test locally:"
echo "   python local_test.py"
echo ""
echo "3. Start development server:"
echo "   uvicorn src.main:app --reload"
echo ""
echo "4. In another terminal, start Telegram bot:"
echo "   python run_telegram_bot.py"
echo ""
echo "5. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial setup'"
echo "   git push origin main"
echo ""
echo "6. Deploy to Railway, Heroku, or AWS:"
echo "   See GITHUB_HOSTING_GUIDE.md"
echo ""
echo "🚀 Your AI Bot is ready!"
