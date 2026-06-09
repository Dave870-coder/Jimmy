# 🤖 Jimmy AI Bot - START HERE

**Your complete AI bot platform powered by Google Gemini, Telegram, and WhatsApp**

---

## 👋 Welcome!

You have a fully-configured Jimmy AI Bot project! This guide will walk you through **3 simple steps** to get it running live.

**Total time: 30-45 minutes**

---

## ⏱️ Quick Overview

| Step | Task | Time | Status |
|------|------|------|--------|
| 1️⃣ | Get API Keys | 15 min | 📋 Do Now |
| 2️⃣ | Test Locally | 10 min | 📋 Do Now |
| 3️⃣ | Deploy Live | 10 min | 📋 Then Deploy |

---

## 🔑 Step 1: Get Your API Keys (15 minutes)

Your bot needs 2 API keys to work:

### 1a. Google AI Studio Key (Required - 5 min)

Google Gemini powers all the intelligence in your bot.

**Steps:**
1. Open: https://aistudio.google.com/
2. Click **"Get API Key"** (top right)
3. Click **"Create API key in new project"**
4. Copy the key (starts with `AIza...`)
5. **Keep it safe!** Don't share it

**Add to your .env file:**
```
GOOGLE_API_KEY=AIza_your_key_here
```

### 1b. Telegram Bot Token (Required - 5 min)

This lets your bot work on Telegram.

**Steps:**
1. Open Telegram app (or https://web.telegram.org)
2. Search for: **@BotFather** (official Telegram bot)
3. Send message: `/newbot`
4. Choose bot name: "Jimmy Bot" (or anything you want)
5. Choose username: "jimmy_ai_bot_123" (must be unique with numbers)
6. BotFather gives you a token (looks like: `123456789:AABBCCDDEEFFgghhiijjkkllmmnnooppqq`)
7. **Keep it safe!** Don't share it

**Add to your .env file:**
```
TELEGRAM_BOT_TOKEN=123456789:AABBCCDDEEFFgghhiijjkkllmmnnooppqq
```

### 1c. WhatsApp (Optional - 5 min)

If you want WhatsApp support too:
1. Go to: https://developers.facebook.com/
2. Create a Meta Business account
3. Create WhatsApp Business app
4. Get: Business Account ID, Phone Number ID, Access Token
5. Add to `.env` (see file for details)

**Note:** WhatsApp is optional. You can use QR code auth instead (`/whatsapp-qr` in Telegram).

---

## 🔧 Step 2: Test Locally (10 minutes)

Make sure everything works before going live.

### 2a. Edit .env File

1. Find and open the `.env` file in your project
2. Replace placeholders:
   ```
   # Change from:
   GOOGLE_API_KEY=test_google_key
   # To:
   GOOGLE_API_KEY=AIza_your_actual_key_here

   # Change from:
   TELEGRAM_BOT_TOKEN=test_token_123
   # To:
   TELEGRAM_BOT_TOKEN=123456789:AABBCCDDEEFFgghhiijjkkllmmnnooppqq
   ```
3. **Save the file!**

### 2b. Start the Bot

Open PowerShell terminal in project directory, then:

```powershell
# 1. Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Start the bot
python run_bot.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

### 2c. Test It Works

**Open in browser:** http://localhost:8000/docs
- You'll see interactive API documentation
- Everything should load fine

**Test Telegram:**
1. Open Telegram app
2. Search for your bot (the username you created)
3. Click **Start**
4. Bot should say: "Welcome to Jimmy Bot! 🤖"
5. Send: "Hello bot"
6. Bot should respond with AI reply!

**Success!** ✅ Your bot is working locally!

---

## 🚀 Step 3: Deploy Live (10 minutes)

Get your bot running on the internet 24/7 with 1 click!

### 3a. Push Code to GitHub

First, save your code on GitHub:

```powershell
# In another PowerShell terminal (keep bot running):

# Configure Git
git config user.name "Your Name"
git config user.email "your@email.com"

# Create GitHub repo at: https://github.com/new
# Name it: jimmy-ai-bot

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/jimmy-ai-bot.git

# Push code
git add .
git commit -m "Jimmy AI Bot - Ready for production"
git push -u origin main
```

**Verify:** Check GitHub, you should see all files there!

### 3b. Add GitHub Secrets

GitHub secrets let the deployment platform access your API keys safely:

1. Go to your GitHub repo
2. Click **Settings** (top right)
3. Left menu: **Secrets and variables → Actions**
4. Click **New repository secret**
5. Add each secret:

**Secret 1:**
- Name: `GOOGLE_API_KEY`
- Value: Your Google AI key
- Add

**Secret 2:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: Your Telegram token
- Add

**Secret 3:**
- Name: `SECRET_KEY`
- Value: Any random string (e.g., "jimmy-bot-secret-2026")
- Add

### 3c. Deploy to Railway

Railway is the easiest way to run your bot 24/7:

1. Go to: https://railway.app
2. Click **Login** (or create free account)
3. Click **New Project**
4. Click **"Deploy from GitHub repo"**
5. Click **"Connect GitHub"** and authorize
6. Select your `jimmy-ai-bot` repo
7. Click **Deploy**
8. **Wait 3-5 minutes** (Railway builds and deploys!)

**When done:**
1. You'll see a green checkmark ✓
2. Click **Deployments** tab
3. Copy your domain (like: `jimmy-ai-bot-production.up.railway.app`)

### 3d. Test Live

Your bot is now on the internet!

**Test 1 - Health Check:**
```powershell
curl https://your-domain.up.railway.app/health
```
Should return: `{"status": "healthy"}`

**Test 2 - Telegram Online:**
1. Open Telegram
2. Find your bot
3. Send: `/start`
4. **Bot responds from the cloud!** 🎉

**Test 3 - Ask a Question:**
1. Send: "What's 2+2?"
2. Bot responds: "Based on my calculations, 2+2 equals 4"

---

## 🎉 You're Done!

Your Jimmy AI Bot is now:
- ✅ Running **24/7 online**
- ✅ Responding on **Telegram**
- ✅ Powered by **Google AI (Gemini)**
- ✅ Using **WhatsApp** (if configured)
- ✅ Automatically **updating from GitHub**

---

## 📚 Next Steps

### Want to customize?
- Edit AI behavior: Check `src/ai/orchestrator.py`
- Add commands: Check `src/bot/telegram/handler.py`
- Add features: Check `src/api/routes/`

### Want to monitor?
1. Go to Railway dashboard
2. Click your project
3. See real-time logs of bot activity

### Want to scale?
- Railway auto-scales as you get more users
- Upgrade from free ($5/month) to pay-as-you-go

### Want to use custom domain?
1. Buy domain (GoDaddy, Namecheap, etc.)
2. Point DNS to Railway
3. Use your own domain!

---

## 📋 Detailed Guides

- **[Quick Start Local](QUICK_START_LOCAL.md)** - Get running in 5 minutes
- **[Complete Setup Guide](JIMMY_COMPLETE_SETUP_GUIDE.md)** - Full walkthrough with troubleshooting
- **[GitHub Guide](GITHUB_SETUP_GUIDE.md)** - Detailed GitHub setup
- **[Railway Deployment](RAILWAY_DEPLOYMENT_GUIDE.md)** - Advanced Railway options
- **[Implementation Checklist](COMPLETE_IMPLEMENTATION_CHECKLIST.md)** - Step-by-step checklist

---

## ❓ Quick FAQ

**Q: Is it free?**
A: Yes! Railway gives $5/month free credits. Most hobby bots use ~$2/month. Completely free tier!

**Q: Can I use my own domain?**
A: Yes! Buy a domain and point it to Railway (takes 5 min).

**Q: Will my bot stay on 24/7?**
A: Yes! Railway keeps it running automatically. Never stops!

**Q: Can I update the bot?**
A: Yes! Update code on GitHub, push, and Railway auto-deploys (no downtime).

**Q: What if something breaks?**
A: Check the logs in Railway dashboard. Look for error messages and fix!

**Q: Can I add WhatsApp later?**
A: Yes! Configure WhatsApp Business API anytime and update `.env`.

**Q: How many users can it handle?**
A: Railway auto-scales. Start with $5/month, upgrade as needed.

---

## 🆘 Need Help?

1. **Check logs:** Railway dashboard → Deployments → Logs
2. **Read guides:** Check documentation folder
3. **Test locally first:** Always test with `python run_bot.py`
4. **Check GitHub Issues:** See if others solved it

---

## 🎯 Your Bot is Ready!

Everything is configured and tested. You have:
- ✅ All source code
- ✅ All configuration files
- ✅ All documentation
- ✅ Ready-to-deploy setup

**No more setup needed. Just follow the 3 steps above!**

**Time to go live:** ⏱️ 30-45 minutes

---

## 📊 What's Inside

```
jimmy-ai-bot/
├── src/                      # Source code
│   ├── ai/                   # AI orchestrator
│   ├── bot/                  # Telegram & WhatsApp
│   ├── api/                  # FastAPI endpoints
│   ├── database/             # SQLite database
│   └── ...
├── docs/                     # Documentation
├── tests/                    # Tests
├── .env                      # Your secrets (don't commit!)
├── run_bot.py                # Bot entry point
├── requirements.txt          # Python packages
├── Procfile                  # Production config
└── ...
```

---

## 🚀 Let's Go!

Ready? Here's the checklist:

- [ ] Got Google AI key from aistudio.google.com
- [ ] Got Telegram token from @BotFather
- [ ] Updated .env file with keys
- [ ] Tested locally: `python run_bot.py`
- [ ] Opened Telegram and tested bot
- [ ] Created GitHub repo
- [ ] Pushed code to GitHub
- [ ] Added GitHub secrets
- [ ] Deployed to Railway
- [ ] Tested live: Telegram works from the cloud
- [ ] Bot is now online 24/7! 🎉

---

**Made with ❤️ by Onuoha Ikechukwu David**

**Questions?** Check the detailed guides or Railway docs at https://docs.railway.app

---

## 🎊 Welcome to Production!

Your Jimmy AI Bot is now live and ready to talk to the world! 🌍
