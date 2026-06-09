# Jimmy AI Bot - Quick Reference Card

## 🚀 Essential Commands

### Activate Virtual Environment
```bash
# Windows
.\.venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### Start Bot Locally
```bash
python run_bot.py
```
Then open: http://localhost:8000/docs

### Run Verification
```bash
python quick_startup_check.py
```

### Test Locally
```bash
python local_test.py
```

---

## 📝 Essential Files & Locations

| File | Purpose | Edit? |
|------|---------|-------|
| `.env` | API keys & secrets | ✅ YES - Add keys here |
| `run_bot.py` | Bot entry point | ❌ Don't edit |
| `src/main.py` | FastAPI app | ✅ Advanced users |
| `src/bot/telegram/handler.py` | Telegram bot | ✅ Advanced users |
| `.gitignore` | Ignore secrets | ❌ Don't edit |
| `requirements.txt` | Python packages | ❌ Don't edit |

---

## 🔑 Required .env Keys

```
GOOGLE_API_KEY=AIza_your_key_here
TELEGRAM_BOT_TOKEN=123456789:AABBCCDDEEFFgghhiijjkkllmmnnooppqq
```

---

## 🌐 GitHub Commands

```bash
# First time setup
git config user.name "Your Name"
git config user.email "your@email.com"
git init

# Create GitHub repo at: https://github.com/new

# Push code
git remote add origin https://github.com/USERNAME/jimmy-ai-bot.git
git add .
git commit -m "Initial commit"
git push -u origin main

# Future updates
git add .
git commit -m "Your message"
git push
```

---

## 🚀 Deployment (Railway)

**First time:**
1. Go to railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select repo
4. Wait 3-5 minutes
5. Add environment variables

**Update after code changes:**
- Just push to GitHub
- Railway auto-deploys! ⚡

---

## 🧪 Testing Checklist

```bash
# Local
python run_bot.py
# → Open http://localhost:8000/docs
# → Send message in Telegram

# Production
curl https://your-domain.com/health
# → Should return 200

# Telegram Live
# → Find your bot in Telegram
# → Send message
# → Bot should respond
```

---

## 📊 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if bot is alive |
| `/ready` | GET | Check if ready |
| `/docs` | GET | API documentation |
| `/api/v1/telegram/webhook` | POST | Telegram webhook |
| `/api/v1/whatsapp/webhook` | POST | WhatsApp webhook |

---

## 🔍 Troubleshooting Quick Fixes

**Bot not starting:**
```bash
# Check Python version
python --version
# Must be 3.12+

# Check dependencies
pip install -e .

# Clear cache
rm -rf __pycache__ .pytest_cache
```

**API key not working:**
```bash
# Verify in .env
cat .env | grep GOOGLE_API_KEY

# Add if missing
echo "GOOGLE_API_KEY=AIza_your_key" >> .env
```

**Telegram not responding:**
1. Check `/health` endpoint
2. Verify token in .env
3. Check Railway logs
4. Restart service

**Database error:**
```bash
# Create data directory
mkdir data

# Bot auto-creates database
python run_bot.py
```

---

## 📱 Telegram Commands

| Command | Effect |
|---------|--------|
| `/start` | Start bot |
| `/help` | Get help |
| `/whatsapp-qr` | Show WhatsApp QR |
| `/status` | Bot status |
| Any message | AI responds |

---

## 🌐 API Keys Quick Reference

| Service | Get Key From | Docs |
|---------|--------------|------|
| **Google AI** | https://aistudio.google.com | [Docs](https://ai.google.dev) |
| **Telegram** | @BotFather | [Docs](https://core.telegram.org/bots) |
| **WhatsApp** | https://developers.facebook.com | [Docs](https://www.whatsapp.com/business/api/) |

---

## 🔗 Important Links

- **Google AI Studio:** https://aistudio.google.com/
- **Telegram BotFather:** @BotFather
- **Railway Dashboard:** https://railway.app/dashboard
- **GitHub:** https://github.com
- **Bot Repo:** https://github.com/YOUR_USERNAME/jimmy-ai-bot
- **Documentation:** See START_HERE.md

---

## 💾 Regular Maintenance

**Weekly:**
- Check logs for errors
- Test with message
- Monitor database size

**Monthly:**
- Review usage stats
- Update dependencies
- Backup database

---

## 🎯 Next: What to Do Now

1. **Read:** START_HERE.md
2. **Get Keys:** Google AI + Telegram
3. **Edit:** .env file
4. **Test:** `python run_bot.py`
5. **Push:** `git push`
6. **Deploy:** Railway
7. **Test Live:** Open Telegram

---

## 📞 Help Resources

1. **Local Issues?** Run: `python quick_startup_check.py`
2. **Deployment Issues?** Check Railway logs
3. **Code Issues?** Check Python error output
4. **API Issues?** Check API documentation

---

**You've got everything you need! 🚀**

Start with [START_HERE.md](START_HERE.md)
