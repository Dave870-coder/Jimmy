# 🤖 AI Bot Platform - Complete Setup for GitHub & Hosting

## 📚 Complete Documentation

| Guide | Purpose |
|-------|---------|
| **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)** | ⚡ Get running in 5 minutes |
| **[GITHUB_HOSTING_GUIDE.md](GITHUB_HOSTING_GUIDE.md)** | 🚀 Deploy to Railway/Heroku/AWS |
| **[CUSTOM_AGENTS_TOOLS_GUIDE.md](CUSTOM_AGENTS_TOOLS_GUIDE.md)** | 🛠️ Extend with custom agents |
| **[DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md)** | 🌐 Platform-specific setup |

---

## 🚀 Get Started Immediately

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-bot-platform.git
cd ai-bot-platform
```

### 2️⃣ Get API Keys (5 minutes)

**Google AI Studio:**
- Visit: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy key → Add to `.env`

**Telegram Bot:**
- Open Telegram, search "@BotFather"
- Send `/newbot`
- Copy token → Add to `.env`

### 3️⃣ Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Create .env file
cp .env.example .env

# Edit .env with your keys
nano .env
```

### 4️⃣ Test Locally

```bash
# Run test suite
python local_test.py

# Expected: ✅ Tools PASSED, ✅ Orchestrator PASSED
```

### 5️⃣ Deploy Online

**Railway (easiest - 2 minutes):**
```bash
# Push to GitHub
git push origin main

# Go to railway.app, connect GitHub repo, set env vars
# That's it! Railway auto-deploys
```

---

## 🎯 What This Bot Can Do

### 🤖 Powered by Google AI Studio (Gemini)
- Fast, intelligent responses
- Multi-turn conversations
- Context awareness
- Custom system prompts

### 💬 Multi-Channel Communication
- **Telegram**: Direct chat interface
- **WhatsApp**: Optional QR code auth
- **API**: REST endpoints for integration

### 🧠 Intelligent Agents
Bot automatically routes queries to best agent:

| Agent | Purpose | Examples |
|-------|---------|----------|
| **Chat** | General conversation | "Hello!", "Tell me about AI" |
| **Research** | Knowledge base search | "search for...", "find..." |
| **Memory** | Store user preferences | "remember that..." |
| **Workflow** | Task automation | "create workflow..." |
| **Planner** | Break down complex tasks | "plan how to..." |

### 🛠️ Custom Agents & Tools
Built-in:
- Summary Agent
- Analysis Agent
- Recommendation Agent
- Validation Agent
- Integration Agent

And tools like:
- Slack integration
- Webhook sender
- Data transformation
- File processing
- Task scheduling
- Analytics tracking

### 📊 Admin Features
- User management
- Conversation history
- Analytics dashboard
- Rate limiting
- Security & authentication

---

## 💾 Storage & Data

Default setup uses **SQLite** (no database setup needed):
```
data/
├── bot.db          # SQLite database
└── chroma/         # Vector embeddings for search
```

For production, use PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## 🔐 Security

The bot includes:
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ Input validation
- ✅ Environment variable secrets
- ✅ CORS protection
- ✅ Error tracking (Sentry)

**Never commit `.env`!** It's in `.gitignore`.

---

## 📱 Using the Bot

### Via Telegram

1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get token, add to `.env`
3. Start bot: `python run_telegram_bot.py`
4. Message your bot on Telegram

### Via API

```bash
# Start API server
uvicorn src.main:app --reload

# Send message
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "message": "Hello bot!"}'
```

### Via WhatsApp (optional)

See `SETUP_GOOGLE_AI_TELEGRAM_WHATSAPP.md`

---

## 🧪 Testing

### Run Test Suite

```bash
# Full test suite
pytest tests/

# With coverage
pytest tests/ --cov=src

# Or use provided test script
python local_test.py
```

### GitHub Actions Testing

Tests run automatically on every push:
- Go to **Actions** tab in GitHub
- See test results, code coverage
- Logs show any failures

---

## 📦 Deployment Options

### ⭐ Railway (Recommended)
- **Easiest**: Auto-deploys from GitHub
- **Free**: $5/month free tier
- **Setup**: 2 minutes
- **PostgreSQL**: Built-in optional
- **Docs**: [railway.app](https://railway.app)

### 🔵 Heroku
- **Production-grade**: Long track record
- **Setup**: 5 minutes
- **PostgreSQL**: Easy add-on
- **Docs**: [heroku.com](https://heroku.com)

### ☁️ AWS EC2
- **Control**: Full infrastructure control
- **Setup**: 10 minutes
- **Cost**: Starts at ~$5/month
- **Docs**: [aws.amazon.com](https://aws.amazon.com)

### 🐳 Docker
- **Portable**: Works anywhere
- **Setup**: 5 minutes
- **Docs**: [docker.com](https://docker.com)

See **[GITHUB_HOSTING_GUIDE.md](GITHUB_HOSTING_GUIDE.md)** for detailed setup for each platform.

---

## 🚦 Monitoring & Debugging

### View Logs

**Locally:**
```bash
tail -f logs/app.log
```

**Railway:**
```
dashboard.railway.app → Your Project → Logs
```

**Heroku:**
```bash
heroku logs --tail
```

### Check Bot Status

```bash
# API health check
curl http://localhost:8000/health

# Telegram bot status
python run_telegram_bot.py  # Check output
```

---

## 🔧 Configuration

### Key Environment Variables

```env
# API Keys (REQUIRED)
GOOGLE_API_KEY=your-key          # From Google AI Studio
TELEGRAM_BOT_TOKEN=your-token    # From @BotFather

# Optional
WHATSAPP_ACCESS_TOKEN=...        # For WhatsApp
OPENAI_API_KEY=...               # Fallback AI
SENTRY_DSN=...                   # Error tracking

# Server
APP_ENV=development|production
DEBUG=True|False
API_PORT=8000

# Database (defaults to SQLite)
DATABASE_URL=sqlite:///data/bot.db
# Or use PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=True|False
```

### Customize AI Behavior

Edit `src/ai/orchestrator.py`:
```python
custom_prompts = {
    "chat": """Your system prompt here.
    You are a helpful AI assistant that..."""
}
```

---

## 🎓 Learning Resources

### Google AI Studio
- API Keys: https://makersuite.google.com/app/apikey
- Models: https://ai.google.dev/models/
- Docs: https://ai.google.dev/

### Telegram Bot API
- Bot API: https://core.telegram.org/bots
- @BotFather: https://t.me/BotFather

### Deployment Platforms
- Railway: https://docs.railway.app
- Heroku: https://devcenter.heroku.com
- AWS: https://docs.aws.amazon.com

---

## ⚡ Quick Commands

```bash
# Development
python -m venv venv              # Create venv
source venv/bin/activate         # Activate (Windows: venv\Scripts\activate)
pip install -e .                 # Install deps
uvicorn src.main:app --reload    # Start API
python run_telegram_bot.py       # Start Telegram bot
python local_test.py             # Run tests

# Deployment
git push origin main              # Push to GitHub
python -m pip list                # Check installed packages
docker build -t mybot .           # Build Docker image
docker run -e GOOGLE_API_KEY=... # Run container

# Database
alembic upgrade head              # Run migrations
alembic downgrade -1              # Rollback last migration
```

---

## 🆘 Troubleshooting

### API Key Issues
```
Error: "GOOGLE_API_KEY not configured"

Solution:
1. Verify .env file exists
2. Check key is pasted correctly (no spaces)
3. Restart bot after changing .env
```

### Bot Not Responding
```
Error: "Bot doesn't reply on Telegram"

Solution:
1. Check TELEGRAM_BOT_TOKEN in .env
2. Verify bot running: python run_telegram_bot.py
3. Check @BotFather shows bot as active
```

### Deployment Failed
```
Error: "Deploy failed"

Solution:
1. Check logs in Railway/Heroku dashboard
2. Verify all env vars are set
3. Check requirements are installed
4. Try deploying again
```

See **[GITHUB_HOSTING_GUIDE.md](GITHUB_HOSTING_GUIDE.md)** for more troubleshooting.

---

## 🎁 Next Steps

1. ✅ Clone this repository
2. ✅ Add API keys to `.env`
3. ✅ Run `python local_test.py` to verify
4. ✅ Deploy to Railway/Heroku
5. ✅ Customize agents & tools
6. ✅ Monitor in dashboard

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

---

## 📞 Support

- **Docs**: See documentation files
- **Issues**: GitHub Issues tab
- **Email**: team@aibot.com

---

## 🎉 You're Ready!

Your AI Bot Platform is ready to serve. Follow **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)** to get online in 5 minutes!

```bash
git push origin main
```

**Happy deploying!** 🚀
