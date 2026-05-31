# 🚀 Quick Start - GitHub & Online Hosting

Get your AI Bot Platform running on GitHub and deployed online in **5 minutes**.

## 📋 Prerequisites

- Python 3.12+
- Git
- Google AI API Key (free from [makersuite.google.com](https://makersuite.google.com))
- Telegram Bot Token (from @BotFather on Telegram)
- GitHub account

---

## ⚡ Step 1: Initialize Git Repository

```bash
cd /path/to/ai-bot-platform

# Initialize git
git init
git add .
git commit -m "Initial commit: AI Bot Platform with Google AI"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-bot-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Your repo is now on GitHub!** 🎉

---

## 🔑 Step 2: Configure API Keys

### Get Google AI API Key

1. Go to [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key
4. Paste into `.env`:
   ```
   GOOGLE_API_KEY=your-key-here
   ```

### Get Telegram Bot Token

1. Open Telegram, search **@BotFather**
2. Send `/newbot`
3. Follow instructions
4. Copy the HTTP API token
5. Paste into `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-token-here
   ```

---

## 🧪 Step 3: Test Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Test bot
python local_test.py
```

Expected output:
```
✅ Tools: PASSED
✅ Orchestrator: PASSED
```

---

## 🚀 Step 4: Deploy Online (Choose One)

### Option A: Railway (⭐ Easiest - 2 minutes)

```bash
# 1. Go to railway.app and sign up with GitHub

# 2. Connect your GitHub repository

# 3. Set environment variables in Railway:
#    GOOGLE_API_KEY=...
#    TELEGRAM_BOT_TOKEN=...
#    APP_ENV=production
#    DEBUG=False

# 4. Push to main branch
git push origin main

# Railway auto-deploys!
```

**Your bot is now live!** ✨

### Option B: Heroku (3 minutes)

```bash
# 1. Sign up at heroku.com

# 2. Install Heroku CLI
npm install -g heroku
heroku login

# 3. Create app
heroku create your-bot-name

# 4. Set environment variables
heroku config:set GOOGLE_API_KEY=your-key
heroku config:set TELEGRAM_BOT_TOKEN=your-token
heroku config:set SECRET_KEY=random-secure-key

# 5. Deploy
git push heroku main

# 6. Check it's working
heroku logs --tail
```

### Option C: GitHub + Docker (Run Anywhere)

```bash
# Build and push Docker image to GitHub Container Registry
docker build -t ghcr.io/YOUR_USERNAME/ai-bot-platform:latest .
docker push ghcr.io/YOUR_USERNAME/ai-bot-platform:latest

# Or push to Docker Hub
docker build -t YOUR_USERNAME/ai-bot-platform:latest .
docker push YOUR_USERNAME/ai-bot-platform:latest

# Others can now run:
docker run -e GOOGLE_API_KEY=your-key ghcr.io/YOUR_USERNAME/ai-bot-platform
```

---

## 🧰 Configuration Files

### `.env` (Local - never commit!)
```env
GOOGLE_API_KEY=your-google-api-key
TELEGRAM_BOT_TOKEN=your-telegram-token
APP_ENV=development
DEBUG=True
```

### `.env.production` (Production settings)
Use `.env.production` template in the repo for production deployments.

---

## 📊 Monitor Your Bot

### Railway Dashboard
- Go to railway.app
- Click your project
- See logs, CPU usage, memory
- Restart if needed

### Heroku Dashboard
```bash
# View logs
heroku logs --tail

# See status
heroku ps

# Restart
heroku restart
```

### Local Logs
```bash
tail -f logs/app.log
```

---

## 🔧 Troubleshooting

### "GOOGLE_API_KEY not found"
- Check `.env` file exists
- Verify key is pasted correctly (no extra spaces)
- Restart bot after changing `.env`

### "Telegram bot not responding"
- Verify `TELEGRAM_BOT_TOKEN` in `.env`
- Check bot is running: `python run_telegram_bot.py`
- Check @BotFather still shows bot as active

### "Deploy failed on Railway/Heroku"
- Check logs: `heroku logs --tail` or Railway dashboard
- Ensure all required environment variables are set
- Verify requirements are installed: `pip install -e .`

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -e . --force-reinstall
```

### "Port already in use"
```bash
# Run on different port
uvicorn src.main:app --port 8001
```

---

## 📈 Next Steps

### 1. Customize AI Responses
Edit `.env` to adjust:
- `GOOGLE_MODEL` - Change model (currently `gemini-1.5-pro`)
- Custom system prompts in `src/ai/orchestrator.py`

### 2. Add WhatsApp Integration
- Follow `SETUP_GOOGLE_AI_TELEGRAM_WHATSAPP.md`
- Add WhatsApp access token to `.env`

### 3. Add Custom Agents
- See `CUSTOM_AGENTS_TOOLS_GUIDE.md`
- Create specialized agents for your use case

### 4. Set Up Monitoring
- Add Sentry for error tracking
- Set up log aggregation
- Enable performance monitoring

### 5. Production Checklist
- [ ] Database backups enabled
- [ ] Secrets in platform (Railway/Heroku)
- [ ] Logging configured
- [ ] Error tracking active
- [ ] Rate limiting enabled
- [ ] CORS configured for domain

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `.env` | Local configuration (never commit) |
| `.env.example` | Template for `.env` |
| `.env.production` | Production settings |
| `GITHUB_HOSTING_GUIDE.md` | Detailed hosting guide |
| `CUSTOM_AGENTS_TOOLS_GUIDE.md` | Extend functionality |
| `DEPLOYMENT_ENVIRONMENTS.md` | Platform-specific setup |
| `local_test.py` | Test locally before deploy |

---

## 🆘 Need Help?

- **Google AI**: [makersuite.google.com](https://makersuite.google.com)
- **Telegram Bot API**: [core.telegram.org/bots](https://core.telegram.org/bots)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Heroku Docs**: [devcenter.heroku.com](https://devcenter.heroku.com)

---

## 💡 Pro Tips

### 1. Use Railway for Quick Prototyping
- Free tier with generous limits
- Auto-deploys from GitHub
- Built-in PostgreSQL and Redis

### 2. Use Heroku for Production
- Better for production workloads
- Extensive add-ons ecosystem
- Good documentation

### 3. Enable GitHub Actions Testing
- Tests run on every push
- Catches bugs before deploy
- Already configured in repo

### 4. Set Up GitHub Secrets
```bash
# Go to Settings → Secrets and add:
GOOGLE_API_KEY
TELEGRAM_BOT_TOKEN
WHATSAPP_ACCESS_TOKEN  # (if using)
```

### 5. Use Environment-Specific Configs
```python
# In code
from src.config import get_settings
settings = get_settings()

if settings.app_env == "production":
    # Production behavior
else:
    # Development behavior
```

---

## 🎉 You're All Set!

Your AI Bot is now:
- ✅ On GitHub
- ✅ Ready to deploy
- ✅ Powered by Google AI Studio
- ✅ Connected to Telegram
- ✅ Production-ready

**Next: Push to GitHub and deploy to Railway/Heroku!**

```bash
git push origin main
```

Happy coding! 🚀
