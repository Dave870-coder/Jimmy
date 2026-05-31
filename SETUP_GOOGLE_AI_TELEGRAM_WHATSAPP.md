# Setup Guide - Google AI + Telegram + WhatsApp Bot

This guide will help you get your AI bot working with Google AI Studio, Telegram, and WhatsApp in 15 minutes.

## 🎯 What You Need

1. **Google AI API Key** (free) - from https://makersuite.google.com/app/apikey
2. **Telegram Bot Token** - from @BotFather on Telegram
3. **WhatsApp Setup** (optional) - Facebook Business Account required

---

## 📋 Step 1: Get Your API Keys

### Google AI Studio API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key
4. **Keep this safe!** You'll need it in the next step

### Telegram Bot Token
1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the instructions to create a bot
4. Copy the **HTTP API token** provided
5. Send `/setprivacy` and choose "DISABLED" (for group support)

### WhatsApp (Optional - For Later)
For now, skip this. We'll focus on getting Google AI + Telegram working first.

---

## 🚀 Step 2: Quick Setup (Docker - Recommended)

### 2.1 Clone and Configure

```bash
cd c:\Users\Dave\3D Objects\jimmy
cp .env.example .env
```

### 2.2 Edit `.env` File

Open `.env` and update these 3 lines:

```env
# Your Google AI key from step 1
GOOGLE_API_KEY=paste-your-api-key-here

# Your Telegram bot token from step 1
TELEGRAM_BOT_TOKEN=paste-your-telegram-token-here

# Leave blank for now if you don't have WhatsApp yet
WHATSAPP_ACCESS_TOKEN=
```

### 2.3 Start with Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- FastAPI backend (port 8000)
- Admin dashboard (port 3000)

**Wait 30 seconds for services to fully start**

### 2.4 Verify It's Running

```bash
# Check if all services are healthy
docker-compose ps

# Check API is responding
curl http://localhost:8000/health
```

You should see:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

## 💬 Step 3: Test Telegram Bot

### 3.1 Start the Telegram Bot

```bash
# In a new terminal
docker-compose exec api python -c "
import asyncio
from src.bot.telegram.handler import get_telegram_bot

async def main():
    bot = await get_telegram_bot()
    print('🤖 Telegram bot starting...')
    await bot.run_polling()

asyncio.run(main())
"
```

Or use polling directly:

```bash
# Simpler approach - bot will run in polling mode
docker-compose exec api telegram-bot
```

### 3.2 Test in Telegram

1. In Telegram, find your bot (search for the name you gave it)
2. Send `/start`
3. You should see: "👋 Welcome to AI Bot Platform!"
4. Try sending a message: "Hello!"
5. The bot should respond using Google AI

---

## 🧪 Step 4: API Testing

### Test Chat Endpoint

```bash
# Get an access token first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

Then use the token:

```bash
curl -X POST http://localhost:8000/api/v1/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is Python?",
    "message_type": "text",
    "source": "api"
  }'
```

You should get a response from Google AI.

---

## 📱 Step 5: WhatsApp Setup (Optional)

### 5.1 Get WhatsApp Credentials

1. Go to: https://developers.facebook.com/
2. Create a Facebook App
3. Add WhatsApp Product
4. Create a Business Account
5. Get:
   - Business Account ID
   - Phone Number ID
   - Access Token
   - Webhook Verify Token (create your own random string)

### 5.2 Update `.env`

```env
WHATSAPP_BUSINESS_ACCOUNT_ID=your-account-id
WHATSAPP_BUSINESS_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### 5.3 Setup Webhook

Your webhook URL should be:
```
https://yourdomain.com/api/v1/whatsapp/webhook
```

(You'll need a public domain and HTTPS)

---

## 🔧 Troubleshooting

### "GOOGLE_API_KEY not configured"
- Make sure you added your key to `.env`
- Restart Docker: `docker-compose restart api`

### "Telegram bot token invalid"
- Verify the token from @BotFather is correct
- Check for spaces or extra characters

### "Database connection failed"
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart postgres
```

### "Port 8000 already in use"
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

---

## 📊 Monitoring

### Check Logs

```bash
# Real-time logs
docker-compose logs -f api

# Telegram bot logs
docker-compose logs -f api | grep telegram

# Database logs
docker-compose logs postgres
```

### API Documentation

Visit: http://localhost:8000/docs

This shows all available endpoints with examples.

### Admin Dashboard

Visit: http://localhost:3000

(Login with admin user setup in database)

---

## 🎓 Next Steps

### 1. Customize Bot Responses
Edit: `src/ai/orchestrator.py`

```python
system_prompt = """You are a helpful assistant for [YOUR PURPOSE].
You specialize in [YOUR EXPERTISE].
Always be [YOUR TONE]."""
```

### 2. Add Custom Commands
Edit: `src/bot/telegram/handler.py`

Add new command handlers like:
```python
async def my_command_handler(self, update: Update, context):
    """Handle /mycommand."""
    await update.message.reply_text("Custom response")
```

### 3. Add Tools
Create tools in: `src/ai/tools/external.py`

Example:
```python
async def search_web(query: str) -> list[dict]:
    """Search the web."""
    # Implement your search logic
    pass
```

### 4. Deploy to Production
See: `docs/DEPLOYMENT.md` for:
- Heroku
- Railway
- AWS
- Google Cloud
- Azure

---

## 🆘 Support

- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report problems
- **Logs**: `docker-compose logs api`

---

## ✅ Quick Checklist

- [ ] Google AI API key obtained
- [ ] Telegram bot created with @BotFather
- [ ] `.env` file updated with tokens
- [ ] Docker services running (`docker-compose ps`)
- [ ] API health check passing
- [ ] Telegram bot responding
- [ ] API endpoints working

**Once all checked, you're ready to use your bot!** 🚀

---

### Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Restart bot
docker-compose restart api

# Access database
docker-compose exec postgres psql -U aibot_user -d aibot_db

# Run migrations
docker-compose exec api alembic upgrade head
```

---

**Made with ❤️ for your AI Bot** 🤖
