# 🚀 Jimmy Bot - Complete Render + GitHub Deployment Guide

## Quick Deploy (2 minutes)

### 1. Click Deploy Button
```
https://render.com/deploy?repo=https://github.com/Dave870-coder/Jimmy
```

Or manually:
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select "Deploy existing repository"
4. Search for "Dave870-coder/Jimmy"
5. Click "Deploy"

### 2. Add Environment Variables

In the Render dashboard, add these variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `GOOGLE_API_KEY` | (from Google AI Studio) | Required for AI responses |
| `TELEGRAM_BOT_TOKEN` | (from @BotFather) | Required for Telegram |
| `SECRET_KEY` | (generate random) | For session security |
| `PUBLIC_BASE_URL` | Leave blank initially | Will be set after deploy |
| `DATABASE_URL` | Default: sqlite | Or use PostgreSQL |

### 3. Deployment Complete!
- Wait 3-5 minutes for build
- You'll get a URL like: `https://jimmy-bot-xyz.onrender.com`
- Copy this URL for step 4

---

## Step-by-Step Instructions

### Phase 1: GitHub Repository Setup

Your repository is ready with:
- ✅ `render.yaml` - Deployment configuration
- ✅ `build.sh` - Build script
- ✅ `requirements.txt` - Python dependencies
- ✅ `src/main.py` - FastAPI application

### Phase 2: Deploy to Render

#### Option A: One-Click Deploy (Easiest)

1. **Click Deploy Button:**
   ```
   https://render.com/deploy?repo=https://github.com/Dave870-coder/Jimmy
   ```

2. **Authorize GitHub**
   - Log in to GitHub if prompted
   - Grant Render access to your repository

3. **Review Configuration**
   - Service name: `jimmy-ai-bot`
   - Region: `oregon` (free tier)
   - Plan: `Free`
   - Click "Deploy"

4. **Wait for Build (3-5 min)**
   - Render will build and deploy
   - You'll see status updates
   - Once "Live" appears, it's ready!

#### Option B: Manual Setup

1. **Go to https://render.com**
2. **Sign in with GitHub**
3. **Click "New Web Service"**
4. **Connect Your Repository:**
   - Search: `Jimmy`
   - Select: `Dave870-coder/Jimmy`
   - Click "Connect"

5. **Configure Service:**
   - Name: `jimmy-ai-bot` (default)
   - Environment: `Python`
   - Build Command: `bash ./build.sh`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free** ($0/month)

6. **Add Environment Variables:**
   ```
   GOOGLE_API_KEY = (from Google AI Studio)
   TELEGRAM_BOT_TOKEN = (from @BotFather)
   SECRET_KEY = (generate: openssl rand -hex 32)
   DATABASE_URL = (leave default or set PostgreSQL)
   APP_ENV = production
   ```

7. **Click "Create Web Service"**
8. **Wait 3-5 minutes**
9. **Get Your URL**
   - Once deployed, you'll see: `https://jimmy-ai-bot.onrender.com`
   - Copy this URL

### Phase 3: Configure GitHub Dashboard

Once your backend is deployed on Render:

1. **Get Your Render URL**
   - From Render dashboard
   - Format: `https://jimmy-ai-bot.onrender.com`

2. **Add GitHub Secret**
   - Go to: https://github.com/Dave870-coder/Jimmy/settings/secrets/actions
   - Click "New repository secret"
   - Name: `NEXT_PUBLIC_API_BASE`
   - Value: `https://jimmy-ai-bot.onrender.com`
   - Click "Add secret"

3. **Trigger Dashboard Rebuild**
   - Go to: https://github.com/Dave870-coder/Jimmy/actions
   - Click "Deploy Dashboard to GitHub Pages"
   - Click "Run workflow"
   - Wait 1-2 minutes

4. **Verify Connection**
   - Open: https://dave870-coder.github.io/Jimmy/
   - Check "API status" (should show "Connected")

---

## Verification Checklist

### Backend (Render)
```bash
# Check if backend is running:
curl https://jimmy-ai-bot.onrender.com/health

# Should return: {"status": "healthy"}
```

### Dashboard (GitHub Pages)
```bash
# Open in browser:
https://dave870-coder.github.io/Jimmy/

# Should show:
- ✅ Dashboard loads
- ✅ All components visible
- ✅ API status shows "Connected"
```

### Complete Integration
```bash
# Once connected:
1. Visit https://dave870-coder.github.io/Jimmy/
2. Go to "Production setup" tab
3. Add your API keys:
   - Telegram bot token
   - Google AI API key
4. Click "Save production settings"
5. Check "Analytics" tab for real data
```

---

## Getting Required API Keys

### Google AI Studio API Key
1. Go to: https://aistudio.google.com/
2. Click "Get API key"
3. Select your project or create new
4. Copy the API key
5. Add to Render: `GOOGLE_API_KEY=`

### Telegram Bot Token
1. Message: @BotFather on Telegram
2. Send: `/newbot`
3. Follow instructions
4. Copy the token (format: `123456:ABC...`)
5. Add to Render: `TELEGRAM_BOT_TOKEN=`

### Generate Secret Key
```bash
# On your computer:
openssl rand -hex 32

# Or use Python:
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and add to Render: `SECRET_KEY=`
```

---

## Environment Variables Explained

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `GOOGLE_API_KEY` | Google AI Gemini API | Yes | `AIzaSy...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot auth | Yes | `123456:ABC...` |
| `SECRET_KEY` | JWT/session encryption | Yes | `a1b2c3...` |
| `PUBLIC_BASE_URL` | Your deployed URL | Auto | `https://jimmy-ai-bot.onrender.com` |
| `DATABASE_URL` | Database connection | No (SQLite default) | `postgresql://...` |
| `APP_ENV` | Environment mode | No | `production` |

---

## Common Issues & Solutions

### Issue: Build Fails
**Solution:**
```bash
# Check build.sh exists:
ls -la build.sh

# Check requirements.txt:
cat requirements.txt

# Both files must be in root directory
```

### Issue: Backend Times Out
**Solution:**
- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes 30 seconds
- To prevent: Use paid tier ($7/month) or keep bot active

### Issue: Dashboard Says "API Error"
**Solution:**
1. Check `NEXT_PUBLIC_API_BASE` in GitHub Secrets
2. Verify format: `https://jimmy-ai-bot.onrender.com` (no trailing slash)
3. Run workflow again: https://github.com/Dave870-coder/Jimmy/actions

### Issue: Telegram Webhook Not Working
**Solution:**
```bash
# Set webhook URL:
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook \
  -d "url=https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook"

# Verify it worked:
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

---

## URLs After Deployment

| Component | URL | Status |
|-----------|-----|--------|
| **Dashboard (UI)** | https://dave870-coder.github.io/Jimmy/ | ✅ Live |
| **Backend (API)** | https://jimmy-ai-bot.onrender.com | ⏳ To Deploy |
| **API Health** | https://jimmy-ai-bot.onrender.com/health | ⏳ To Deploy |
| **GitHub Repo** | https://github.com/Dave870-coder/Jimmy | ✅ Live |
| **Actions** | https://github.com/Dave870-coder/Jimmy/actions | ✅ Live |

---

## Architecture After Deployment

```
User Browser
    ↓
    ├─→ GitHub Pages (Dashboard)
    │   https://dave870-coder.github.io/Jimmy/
    │
    └─→ Renders UI + calls → Render Backend (API)
        https://jimmy-ai-bot.onrender.com/api/v1/*

Render Backend
    ├─→ SQLite Database
    ├─→ Google AI (Gemini)
    ├─→ Telegram API
    └─→ WhatsApp API
```

---

## Next Steps

1. **Deploy to Render** (5 min)
   - Click deploy button or follow manual steps
   - Add environment variables
   - Wait for build to complete

2. **Connect Dashboard** (2 min)
   - Add GitHub Secret
   - Trigger dashboard rebuild

3. **Configure Telegram** (2 min)
   - Get bot token from @BotFather
   - Set webhook URL

4. **Test Everything** (2 min)
   - Visit dashboard
   - Add API keys
   - Send test message

**Total time: ~15 minutes to full working setup!**

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **GitHub Pages:** https://pages.github.com
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Google AI Studio:** https://aistudio.google.com

---

## You're Ready! 🚀

Your Jimmy Bot is ready to go live with:
- ✅ Dashboard on GitHub Pages
- ✅ Backend on Render
- ✅ Telegram integration
- ✅ WhatsApp integration  
- ✅ Google AI integration
- ✅ Auto-scaling for 7M users

**Let's deploy!**

