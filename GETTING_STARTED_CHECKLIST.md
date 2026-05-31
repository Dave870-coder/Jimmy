# Getting Started Checklist 🚀

Use this checklist to ensure your AI Bot Platform is configured correctly for Google AI, Telegram, and WhatsApp.

## Pre-Setup Requirements

- [ ] Google Account (for Google AI API)
- [ ] Telegram Account (for Telegram Bot)
- [ ] Facebook Business Account (optional, for WhatsApp)
- [ ] Docker Desktop installed (or Docker + docker-compose)
- [ ] Git installed (to clone the repo)

---

## Step 1: Get Your API Keys ✅

### Google AI API Key
- [ ] Visit: https://makersuite.google.com/app/apikey
- [ ] Click "Create API Key" button
- [ ] Copy the API key to a secure location
- [ ] Key format: `AIza...` (should start with AIza)

### Telegram Bot Token
- [ ] Open Telegram and search for `@BotFather`
- [ ] Send `/newbot`
- [ ] Follow the instructions:
  - [ ] Choose a name for your bot
  - [ ] Choose a username for your bot (must end with `bot`)
- [ ] Copy the HTTP API token (format: `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh`)
- [ ] Optional: Send `/setprivacy` and set to "DISABLED" for group support

### WhatsApp Credentials (Optional - for later)
- [ ] Go to: https://developers.facebook.com/
- [ ] Create a Facebook App (or use existing)
- [ ] Add WhatsApp Product to your app
- [ ] Create Business Account
- [ ] Collect these values (for later):
  - [ ] Business Account ID
  - [ ] Phone Number ID
  - [ ] Access Token
  - [ ] Webhook Verify Token (generate a random string)

---

## Step 2: Configure the Application 🔧

### 2.1 Clone the Repository
```bash
git clone <your-repo-url>
cd jimmy
```

### 2.2 Create `.env` File
- [ ] Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```

### 2.3 Edit `.env` File with Your Keys
Open `.env` in your editor and update:

```env
# Google AI (Required)
GOOGLE_API_KEY=<your-api-key-from-google>
GOOGLE_MODEL=gemini-pro

# Telegram (Required)
TELEGRAM_BOT_TOKEN=<your-token-from-botfather>

# WhatsApp (Optional - leave blank for now)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_BUSINESS_PHONE_NUMBER_ID=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
```

**Verification**:
- [ ] `GOOGLE_API_KEY` is filled and looks like: `AIza...`
- [ ] `TELEGRAM_BOT_TOKEN` is filled and looks like: `123456789:ABCD...`
- [ ] No empty values for required fields

---

## Step 3: Start the Services 🐳

### 3.1 Start with Docker
```bash
docker-compose up -d
```

**Verification**:
- [ ] All services started successfully
- [ ] No error messages in output

### 3.2 Check Service Health
```bash
docker-compose ps
```

You should see:
- [ ] `postgres` - running (health: healthy)
- [ ] `redis` - running (health: healthy)
- [ ] `api` - running (health: healthy)
- [ ] `dashboard` - running

### 3.3 Test API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

- [ ] API responds with `healthy` status

---

## Step 4: Test Telegram Bot 💬

### 4.1 Open Telegram

1. [ ] Search for your bot by username (the one you created with @BotFather)
2. [ ] Click on the bot to open chat

### 4.2 Send Test Commands

Send these commands and verify responses:

- [ ] `/start` 
  - Expected: Welcome message from your bot
  
- [ ] `/help`
  - Expected: List of available commands
  
- [ ] `/status`
  - Expected: "Bot Status: Online" message
  
- [ ] Send a regular message (e.g., "Hello!")
  - Expected: Response from Google AI (takes 2-3 seconds)

### 4.3 Check Logs
```bash
docker-compose logs -f api
```

- [ ] Messages appear in logs
- [ ] No error messages related to Google AI or Telegram

---

## Step 5: Test API Endpoints (Optional) 📡

### 5.1 API Documentation
Visit: http://localhost:8000/docs

- [ ] Page loads successfully
- [ ] See Swagger UI with all endpoints

### 5.2 Test Chat Endpoint
```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Use the token from response
curl -X POST http://localhost:8000/api/v1/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is Python?",
    "message_type": "text",
    "source": "api"
  }'
```

- [ ] Login endpoint works
- [ ] Message endpoint returns response from Google AI

---

## Step 6: Optional - Setup WhatsApp Integration 📱

### 6.1 Get Credentials from Facebook
- [ ] Go to your app settings
- [ ] Get: Business Account ID, Phone Number ID, Access Token
- [ ] Generate a random token for webhook verification

### 6.2 Update `.env`
```env
WHATSAPP_BUSINESS_ACCOUNT_ID=your-id
WHATSAPP_BUSINESS_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_ACCESS_TOKEN=your-token
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-random-token
```

### 6.3 Setup Webhook
- [ ] Get your public domain name (using ngrok or deployment)
- [ ] Webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`
- [ ] Configure in Facebook App settings
- [ ] Verify webhook

### 6.4 Test WhatsApp
- [ ] Send a message from WhatsApp number
- [ ] Verify response from bot

---

## Troubleshooting 🔍

### Issue: "GOOGLE_API_KEY not configured"
**Solution:**
- [ ] Check `.env` file has `GOOGLE_API_KEY=...`
- [ ] Verify key is not empty
- [ ] Restart services: `docker-compose restart api`

### Issue: "Telegram bot token invalid"
**Solution:**
- [ ] Verify token from @BotFather again
- [ ] Copy-paste the exact token (no spaces)
- [ ] Check `.env` file: `TELEGRAM_BOT_TOKEN=<token>`

### Issue: "Database connection failed"
**Solution:**
- [ ] Check PostgreSQL is running: `docker-compose ps postgres`
- [ ] Check Redis is running: `docker-compose ps redis`
- [ ] Restart all services: `docker-compose restart`

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Bot not responding to messages
**Solution:**
- [ ] Check bot token is correct in `.env`
- [ ] Check Google API key is valid
- [ ] View logs: `docker-compose logs -f api | grep -i telegram`
- [ ] Verify bot token with @BotFather

---

## Production Deployment 🚀

When ready to deploy:

- [ ] Read: `docs/DEPLOYMENT.md`
- [ ] Choose platform:
  - [ ] Heroku
  - [ ] Railway
  - [ ] AWS
  - [ ] Google Cloud
  - [ ] Azure
  - [ ] DigitalOcean

---

## Important Notes ⚠️

1. **Security**: Never commit `.env` file to Git - it contains secrets
2. **API Keys**: Keep your Google API key and Telegram token safe
3. **Webhook**: WhatsApp requires a public HTTPS URL (not localhost)
4. **Rate Limits**: The bot has rate limiting (100 requests/hour by default)
5. **Free Tier**: Google AI Studio has free tier limits (check quotas)

---

## Quick Commands 💻

```bash
# View logs
docker-compose logs -f api

# Access database
docker-compose exec postgres psql -U aibot_user -d aibot_db

# Stop services
docker-compose down

# Remove all data
docker-compose down -v

# Rebuild services
docker-compose build --no-cache

# Run migrations
docker-compose exec api alembic upgrade head
```

---

## Get Help 🆘

- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Check/create issues in the repository
- **Logs**: `docker-compose logs -f api`
- **Setup Guide**: [SETUP_GOOGLE_AI_TELEGRAM_WHATSAPP.md](SETUP_GOOGLE_AI_TELEGRAM_WHATSAPP.md)

---

## Success Checklist ✨

You're all set when:
- [ ] `.env` file is configured with all required keys
- [ ] All Docker services are running and healthy
- [ ] API health check returns `healthy` status
- [ ] Telegram bot responds to `/start` command
- [ ] Bot responds to regular messages with Google AI responses
- [ ] No errors in logs
- [ ] (Optional) WhatsApp is configured and receiving messages

**Congratulations! Your AI Bot Platform is ready to go!** 🎉

