# 🚀 Jimmy AI Bot - Quick Start (5 Minutes)

## ⚡ One-Command Setup

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# OR
source venv/bin/activate             # Mac/Linux

# 2. Run verification
python quick_startup_check.py

# 3. Start the bot
python run_bot.py
```

## 📋 Pre-Setup Checklist

Before you start, get these API keys (takes ~10 minutes):

### 1. Google AI Studio Key (Required)
- Go to: https://aistudio.google.com/
- Click "Get API Key"
- Copy and add to `.env`: `GOOGLE_API_KEY=your-key`

### 2. Telegram Bot Token (Required)
- Open Telegram → Search @BotFather
- Send `/newbot`
- Copy token and add to `.env`: `TELEGRAM_BOT_TOKEN=your-token`

### 3. WhatsApp (Optional)
- Create Meta Business account
- Set up WhatsApp Business API
- Add tokens to `.env`

## 🔧 If you need to edit .env

Edit the file: `.env`

Update these values:
```
GOOGLE_API_KEY=your-actual-key-here
TELEGRAM_BOT_TOKEN=your-actual-token-here
```

## ✅ Verify Everything Works

```bash
python quick_startup_check.py
```

Expected output:
```
✅ .env file found
✅ Python version OK
✅ All packages installed
✅ Database ready
✅ All project files found
✅ API keys configured
```

## 🤖 Start the Bot

```bash
python run_bot.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🧪 Test the Bot

### Test 1: Open Dashboard
- Open: http://localhost:8000/docs
- You'll see interactive API documentation

### Test 2: Test Telegram Bot
1. Open Telegram
2. Search for your bot (from @BotFather)
3. Send: `/start`
4. Bot should respond!

### Test 3: Test AI
1. In Telegram, ask: "What's 2+2?"
2. Bot should think and respond: "2+2 = 4"

## 🌐 Deploy Live

When ready to go live:

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for production"
git push origin main

# 2. Deploy to Railway (recommended)
# Go to: https://railway.app
# Click "New Project" → "Deploy from GitHub"
# Select your repo → Deploy!
```

## 📞 Troubleshooting

**Problem:** Bot not responding
- Check: `python quick_startup_check.py`
- Look at logs for errors

**Problem:** "GOOGLE_API_KEY not set"
- Edit `.env` file
- Add your actual key (not placeholder)
- Restart bot

**Problem:** "Telegram token invalid"
- Get new token from @BotFather
- Update `.env`
- Restart bot

## 🎉 What's Running

Once bot starts, you have:
- ✅ **FastAPI Server** on port 8000
- ✅ **Telegram Bot** listening for messages
- ✅ **AI Engine** (Google Gemini) processing requests
- ✅ **Database** storing conversations
- ✅ **Admin Dashboard** at /docs

---

**Next:** [Full Setup Guide](JIMMY_COMPLETE_SETUP_GUIDE.md) for advanced options
