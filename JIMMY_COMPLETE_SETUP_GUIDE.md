# 🤖 Jimmy AI Bot - Complete Production Setup Guide

**Status:** Ready for Production Deployment  
**Last Updated:** June 2026  
**Author:** Your Project Team

---

## 📋 Table of Contents

1. [Part 1: Get API Keys](#part-1-get-api-keys)
2. [Part 2: Local Testing](#part-2-local-testing)
3. [Part 3: Push to GitHub](#part-3-push-to-github)
4. [Part 4: Deploy to Production](#part-4-deploy-to-production)
5. [Part 5: Testing Live](#part-5-testing-live)
6. [Troubleshooting](#troubleshooting)

---

## Part 1: Get API Keys

### 🔑 1a. Google AI Studio API Key (5 minutes)

**What is it?** Google Generative AI powers all the intelligence in Jimmy Bot.

**Steps:**
1. Open: https://aistudio.google.com/
2. Click **"Get API Key"** (blue button, top right)
3. Click **"Create API key in new project"**
4. Google creates a new project automatically
5. Copy the API key (starts with `AIza...`)
6. Paste into `.env` file:
   ```
   GOOGLE_API_KEY=your-key-here
   ```

**Verify it works:**
```bash
python local_test.py
```

### 🤖 1b. Telegram Bot Token (2 minutes)

**What is it?** Allows Jimmy Bot to receive and send messages on Telegram.

**Steps:**
1. Open Telegram app (or web.telegram.org)
2. Search for: **@BotFather** (official Telegram bot)
3. Send: `/newbot`
4. BotFather asks for a name → Enter: **Jimmy Bot** (or your choice)
5. BotFather asks for username → Enter: **jimmy_ai_bot_123** (must be unique)
6. BotFather gives you a token (starts with `123456789:`)
7. Copy and paste into `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:AABBCCDDEEFFgghhiijjkkllmmnnooppqq
   ```

**Optional: Set up webhook (for production):**
1. In BotFather, send: `/mybots`
2. Select your bot
3. Select "API Token"
4. Send: `/setwebhook`
5. Use your production URL: `https://yourdomain.com/api/v1/telegram/webhook`

### 💬 1c. WhatsApp Business API (Optional but Recommended - 10 minutes)

**What is it?** Allows Jimmy Bot to send/receive WhatsApp messages.

**Steps:**
1. Go to: https://developers.facebook.com/
2. Log in or create a Meta Developer account
3. Create an app (type: Business)
4. Add "WhatsApp" product
5. Get your:
   - **Business Account ID**
   - **Phone Number ID**
   - **Access Token** (generates automatically)
   - **Verify Token** (you create this - use: `jimmy-whatsapp-verify-token`)
6. Update `.env`:
   ```
   WHATSAPP_BUSINESS_ACCOUNT_ID=your-id
   WHATSAPP_BUSINESS_PHONE_NUMBER_ID=your-phone-id
   WHATSAPP_ACCESS_TOKEN=your-token
   WHATSAPP_WEBHOOK_VERIFY_TOKEN=jimmy-whatsapp-verify-token
   ```

**For testing without Business API:**
- Jimmy Bot supports QR code authentication (no API key needed!)
- Use: `/whatsapp-qr` command in Telegram

---

## Part 2: Local Testing

### Prerequisites
```
✅ Python 3.12+
✅ pip (Python package manager)
✅ Git (for version control)
```

### 2a. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Verify:** You should see `(.venv)` at the start of your terminal line.

### 2b. Install Dependencies

```bash
pip install -e .
```

**What it installs:**
- FastAPI (web framework)
- SQLAlchemy (database)
- python-telegram-bot (Telegram integration)
- google-generativeai (Google AI)
- pydantic (validation)
- uvicorn (web server)
- All other dependencies in requirements.txt

### 2c. Test All Systems

**Run the comprehensive test:**
```bash
python verify_production_startup.py
```

**Expected output:**
```
✅ Tools: PASSED
✅ Orchestrator: PASSED
✅ Database: OK
✅ Configuration: PASSED
✅ Google AI: PASSED
✅ Telegram: PASSED
```

### 2d. Start the Bot Locally

**Terminal 1 - Start API Server:**
```bash
python run_bot.py
```

**Expected:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Open in browser:** http://localhost:8000/docs
- You'll see interactive API documentation
- Test endpoints here

**Terminal 2 - Test Bot Commands:**
```bash
# Test Telegram bot
python run_telegram_bot.py
```

**Terminal 3 - Test basic AI:**
```bash
python local_test.py
```

### 2e. Test Telegram Bot Locally

Once API is running:

1. **Open Telegram**
2. **Search for your bot** (e.g., @jimmy_ai_bot_123)
3. **Send:** `/start`
4. **Bot should respond:** "Welcome to Jimmy Bot! 🤖"
5. **Send a message:** "Hello, what's 2+2?"
6. **Bot should respond:** "Based on my calculations, 2+2 equals 4."

---

## Part 3: Push to GitHub

### 3a. Initialize Git Repository

**If not already done:**
```bash
git init
git config user.name "Your Name"
git config user.email "your@email.com"
```

### 3b. Create GitHub Repository

1. Go to: https://github.com/new
2. Create new repository:
   - Name: **jimmy-ai-bot**
   - Description: "AI Bot Platform powered by Google Gemini, integrated with Telegram and WhatsApp"
   - Public or Private (your choice)
   - Click "Create repository"

### 3c. Add Remote and Push

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/jimmy-ai-bot.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: Jimmy AI Bot - Production Ready"

# Push to GitHub
git push -u origin main
```

**Verify:** Check GitHub - you should see all files there!

### 3d. Add GitHub Secrets (for deployment)

1. Go to GitHub repo
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Name | Value |
|------|-------|
| `GOOGLE_API_KEY` | Your Google AI key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram token |
| `WHATSAPP_ACCESS_TOKEN` | Your WhatsApp token |
| `SECRET_KEY` | A strong random string |

---

## Part 4: Deploy to Production

### Option A: Railway (⭐ Recommended)

**Why Railway?**
- Free tier: $5/month credits (enough for hobby bot)
- Auto-deploy from GitHub
- Auto-HTTPS
- SQLite support
- 24/7 uptime

**Steps:**

1. Go to: https://railway.app/
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Authorize Railway with GitHub
5. Select your **jimmy-ai-bot** repo
6. Railway auto-detects Python project
7. Click **"Deploy"** (takes ~3 minutes)

**Configure Environment:**

1. Click **"Variables"** tab
2. Add these variables:
   ```
   GOOGLE_API_KEY=your-key
   TELEGRAM_BOT_TOKEN=your-token
   WHATSAPP_ACCESS_TOKEN=your-token
   SECRET_KEY=generate-strong-key
   APP_ENV=production
   DEBUG=False
   ```
3. Click **"Save"**

**Get Your URL:**

1. Click **"Deployments"** tab
2. Top deployment shows **domain**: `your-bot-12345.railway.app`
3. This is your public URL!

### Option B: Render

**Steps:**

1. Go to: https://render.com/
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** and select repo
4. Set environment:
   - Name: `jimmy-ai-bot`
   - Language: Python 3.12
   - Build: `pip install -e .`
   - Start: `python run_bot.py`
5. Add environment variables (same as Railway above)
6. Click **"Create Web Service"**

---

## Part 5: Testing Live

### 5a. Check Health Endpoint

Once deployed:

```bash
curl https://your-domain.com/health
```

**Expected:**
```json
{"status": "healthy", "timestamp": "2026-06-09T..."}
```

### 5b. Test Telegram Online

1. **Open Telegram**
2. **Find your bot** (now running online!)
3. **Send:** `/start`
4. **Send:** "What's your name?"
5. **Bot should respond** (from the cloud!)

### 5c. Test WhatsApp (if configured)

1. **Scan QR code in Telegram** (send: `/whatsapp-qr`)
2. **Send WhatsApp message to bot**
3. **Bot should respond**

### 5d. Monitor Logs

**Railway:**
1. Go to railway.app
2. Click your project
3. Click **"Logs"** tab
4. See real-time bot activity

**Render:**
1. Go to render.com
2. Click your service
3. See logs at bottom

---

## Part 6: Troubleshooting

### Problem: "GOOGLE_API_KEY not set"

**Solution:**
```bash
# Check your .env file has the key
cat .env | grep GOOGLE_API_KEY

# Add if missing:
echo "GOOGLE_API_KEY=your-key" >> .env

# Restart bot
python run_bot.py
```

### Problem: "Telegram token invalid"

**Solution:**
1. Get a new token from @BotFather
2. Update .env with exact token (no spaces!)
3. Restart

### Problem: "Database file not found"

**Solution:**
```bash
# Create data directory
mkdir data

# The database will auto-create when bot starts
python run_bot.py
```

### Problem: "Bot not responding on Railway/Render"

**Solution:**
1. Check deployment logs for errors
2. Verify all environment variables are set
3. Check `/health` endpoint returns 200
4. Restart deployment

### Problem: WhatsApp not connecting

**Solution:**
- Use QR code method (easier): Send `/whatsapp-qr` in Telegram
- For Business API, verify tokens in Facebook Dashboard
- Check webhook URL is correct in Facebook settings

---

## 📊 Post-Deployment Checklist

- [ ] `/health` endpoint returns 200
- [ ] `/ready` endpoint shows ready
- [ ] Telegram `/start` command works
- [ ] Bot responds to messages
- [ ] WhatsApp (if set up) connects successfully
- [ ] Logs show no errors
- [ ] Database has created tables
- [ ] All features responding from cloud

---

## 🎉 You're Done!

Your Jimmy AI Bot is now:
- ✅ Running 24/7 online
- ✅ Responding to Telegram messages
- ✅ Powered by Google AI (Gemini)
- ✅ Using WhatsApp integration (optional)
- ✅ Completely secure
- ✅ Auto-deploying from GitHub

---

## 📞 Support & Resources

### Official Docs
- Google AI: https://ai.google.dev/
- Telegram Bot: https://core.telegram.org/bots
- FastAPI: https://fastapi.tiangolo.com/
- Railway: https://docs.railway.app/

### Get Help
- Report issues: GitHub Issues
- Check logs: Railway/Render dashboard
- Test locally first: `python run_bot.py`

---

**Made with ❤️ by Onuoha Ikechukwu David**
