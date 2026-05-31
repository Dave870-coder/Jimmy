# Quick Start Guide

## 🚀 5-Minute Setup (Using Docker)

### Prerequisites
- Docker & Docker Compose installed

### Steps

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/ai-bot-platform.git
   cd ai-bot-platform
   ```

2. **Setup environment**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:3000

That's it! 🎉

## 📝 Local Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for dashboard)

### Steps

1. **Clone and setup**
   ```bash
   git clone <repo>
   cd ai-bot-platform
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Start development server**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Start dashboard** (in another terminal)
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

5. **Access application**
   - API: http://localhost:8000
   - Dashboard: http://localhost:3000

## 🔌 Telegram Bot Setup

1. Create bot via @BotFather on Telegram
2. Get bot token
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```
4. Run development server

## 💬 WhatsApp Setup

1. Register at https://developers.facebook.com/
2. Create WhatsApp Business Account
3. Get access token and phone number ID
4. Add to `.env`:
   ```
   WHATSAPP_ACCESS_TOKEN=your_token
   WHATSAPP_BUSINESS_PHONE_NUMBER_ID=your_id
   ```

## 🔑 API Keys

### Required
- OpenAI API key: https://platform.openai.com/api-keys
- Google AI key: https://makersuite.google.com/app/apikey (optional)

### Optional
- Sentry for error tracking
- AWS for S3 file storage

## ✅ Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "version": "1.0.0"}
```

## 🧪 Run Tests

```bash
pytest tests/ -v --cov=src
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

**Database connection error?**
```bash
# Check PostgreSQL
psql -U aibot_user -d aibot_db

# Reset if needed
dropdb aibot_db
createdb aibc_db
alembic upgrade head
```

**Redis not running?**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or check if running
redis-cli ping
```

## 💡 Next Steps

1. Customize bot responses in `src/ai/orchestrator.py`
2. Add your own tools in `src/ai/tools/`
3. Create custom workflows in dashboard
4. Configure integrations
5. Deploy to your cloud platform

## 📞 Support

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Email: support@aibot.com

---

Happy coding! 🚀
