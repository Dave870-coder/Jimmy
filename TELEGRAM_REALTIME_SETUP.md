# 🚀 Telegram Real-Time Setup Guide

Enable Jimmy to work on Telegram in **real-time** (not demo mode) with full message processing and responses.

---

## 📋 Prerequisites

- ✅ Jimmy backend running (locally or on Render)
- ✅ Google AI API key configured
- ✅ Telegram account
- ✅ A Telegram bot created with @BotFather

---

## 🔧 Step 1: Create Your Telegram Bot

### 1.1 Create Bot with BotFather

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Choose a name (e.g., "My Jimmy Bot")
4. Choose a username (e.g., "my_jimmy_bot")
5. **Copy the token** - you'll need this

Example token format: `123456789:ABCdEF-ghijklmnopQrstuvWxyz_123456`

### 1.2 Configure Bot Settings

```
/setcommands
```

Then paste:
```
start - Start using the bot
help - Show available commands
status - Check bot status
memory - View your memories
clear - Clear conversation history
search - Search knowledge base
tasks - View active tasks
settings - Configure preferences
```

---

## 🌐 Step 2: Get Your Public URL

Your Telegram bot needs a **public URL** to receive messages.

### Option A: Using Render (Production)

If Jimmy is deployed on Render:
```
https://jimmy-ai-bot.onrender.com
```

### Option B: Using Local Tunnel (Development)

For local testing, use **ngrok** or **localtunnel**:

**ngrok:**
```bash
ngrok http 8000
```

You'll get: `https://abc123.ngrok.io`

**localtunnel:**
```bash
npm install -g localtunnel
lt --port 8000
```

You'll get: `https://yourname.loca.lt`

---

## 🔐 Step 3: Configure Environment Variables

### 3.1 Local Development (.env)

Edit `c:\Users\Dave\3D Objects\jimmy\.env`:

```env
# TELEGRAM - Replace with YOUR values
TELEGRAM_BOT_TOKEN=123456789:ABCdEF-ghijklmnopQrstuvWxyz_123456
TELEGRAM_WEBHOOK_URL=https://your-public-url.com/api/v1/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=your-secret-token-123

# GOOGLE AI - Must be configured for real responses
GOOGLE_API_KEY=your-actual-google-ai-key
GOOGLE_MODEL=gemini-1.5-pro

# Environment
APP_ENV=production
DEBUG=False
```

### 3.2 Production Deployment (Render)

In Render dashboard:

1. Go to your Jimmy service
2. **Settings → Environment Variables**
3. Add these variables:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdEF-ghijklmnopQrstuvWxyz_123456
TELEGRAM_WEBHOOK_URL=https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=your-secret-token-123
GOOGLE_API_KEY=your-actual-google-ai-key
APP_ENV=production
DEBUG=False
```

---

## 🔌 Step 4: Register Telegram Webhook

The bot needs to know where to send messages.

### 4.1 Automatic Setup (Recommended)

Run the setup script:

```bash
python setup_telegram_webhook.py
```

This will:
- ✅ Validate your Telegram token
- ✅ Register the webhook with Telegram
- ✅ Test the connection
- ✅ Show configuration status

### 4.2 Manual Setup (via cURL)

```bash
# Test your Telegram token
curl https://api.telegram.org/bot{YOUR_TOKEN}/getMe

# Register webhook
curl -X POST https://api.telegram.org/bot{YOUR_TOKEN}/setWebhook \
  -d "url=https://your-public-url.com/api/v1/telegram/webhook" \
  -d "secret_token=your-secret-token-123"

# Verify webhook
curl https://api.telegram.org/bot{YOUR_TOKEN}/getWebhookInfo
```

Replace:
- `{YOUR_TOKEN}` with your actual token
- `https://your-public-url.com` with your Render/local URL
- `your-secret-token-123` with your webhook secret

---

## ✅ Step 5: Test the Bot

### 5.1 Test Locally

Start the backend:

```bash
# Terminal 1: Start the bot
python run_bot.py

# Terminal 2: Test the webhook (if using ngrok/localtunnel)
python test_telegram_webhook.py
```

### 5.2 Test on Telegram

1. Open Telegram
2. Find your bot (@your_bot_username)
3. Send: `/start`

You should see:
```
👋 Hi Friend! Welcome to AI Bot Platform!

🤖 I'm powered by Google AI and ready to help.
📚 Use /help for available commands.
```

4. Send any message, e.g., "Hello!"

You should get a **real response** from Google AI in seconds.

---

## 🎯 How Real-Time Mode Works

```
User on Telegram
       ↓
[Sends message to your bot]
       ↓
Telegram API → Your Webhook
       ↓
http://your-url/api/v1/telegram/webhook
       ↓
Handler receives update
       ↓
Sends to Google AI Orchestrator
       ↓
Google AI generates response
       ↓
Response sent back to Telegram user
       ↓
User sees reply in seconds ✅
```

---

## 📊 Monitoring Real-Time Messages

### Check Webhook Status

```bash
curl https://api.telegram.org/bot{YOUR_TOKEN}/getWebhookInfo
```

Example response:
```json
{
  "ok": true,
  "result": {
    "url": "https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

### View Logs

**On Render:**
```
Dashboard → Your Service → Logs
```

Look for:
```
📨 Message from 123456789: hello
✅ Response sent to 123456789
```

**Locally:**
```bash
tail -f logs/bot.log
```

---

## 🔧 Troubleshooting

### Problem: "Bot not responding"

**Solution 1: Check Webhook Registration**
```bash
python -c "
import requests
import os
from src.config import get_settings

settings = get_settings()
token = settings.telegram_bot_token

response = requests.get(f'https://api.telegram.org/bot{token}/getWebhookInfo')
print(response.json())
"
```

**Solution 2: Verify Google API Key**
```bash
python -c "
import google.generativeai as genai
from src.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.google_api_key)
model = genai.GenerativeModel(settings.google_model)
response = model.generate_content('test')
print('✅ Google AI working:', response.text[:50])
"
```

### Problem: "Invalid token"

1. Double-check token from @BotFather (no spaces!)
2. Token format: `123456789:ABCdEF-...`
3. Regenerate token if needed: Go to @BotFather → /token

### Problem: "Webhook URL not accessible"

1. If local: Use ngrok/localtunnel, not localhost
2. If Render: Ensure service is running (check health: `/health`)
3. Firewall: Port 443 (HTTPS) must be open

### Problem: "Empty or error responses"

1. Check GOOGLE_API_KEY is set in environment
2. Test Google AI independently:
   ```bash
   python test_google_ai.py
   ```
3. Check logs for error details

---

## 🚀 Production Checklist

Before going live:

- [ ] ✅ Telegram bot created with @BotFather
- [ ] ✅ Real token stored in environment (not test_token_123)
- [ ] ✅ Google API key configured and tested
- [ ] ✅ Public URL set (Render or custom domain)
- [ ] ✅ Webhook registered with Telegram
- [ ] ✅ APP_ENV=production (not development)
- [ ] ✅ DEBUG=False in production
- [ ] ✅ Bot tested on Telegram (at least 3 messages)
- [ ] ✅ Logs show real message processing
- [ ] ✅ Response time < 5 seconds

---

## 📱 Real-Time Commands Available

Once set up, users can:

```
/start          → Greet the user
/help           → Show all commands
/status         → Check if bot is online
/memory         → View stored memories
/clear          → Clear chat history
/search query   → Search knowledge base
/tasks          → View active tasks
/settings       → Configure bot (coming soon)

[Any message]   → Get AI response
```

---

## 🎯 Advanced: Custom Webhook Secret

For security, use a webhook secret:

```bash
# Generate a random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example: K-_1jLk9mZ3p5xQr7vT0aB2cD4eF6gH8iJ0k

# Set in .env
TELEGRAM_WEBHOOK_SECRET=K-_1jLk9mZ3p5xQr7vT0aB2cD4eF6gH8iJ0k

# Register webhook with secret
curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook \
  -d "url=https://your-url.com/api/v1/telegram/webhook" \
  -d "secret_token=K-_1jLk9mZ3p5xQr7vT0aB2cD4eF6gH8iJ0k"
```

---

## 📞 Support & Documentation

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Webhook Updates:** https://core.telegram.org/bots/webhooks
- **BotFather Commands:** https://core.telegram.org/bots#botfather
- **Google AI API:** https://ai.google.dev/

---

## ✨ Next Steps

1. **Set up the bot** (follow steps 1-4)
2. **Test it** (step 5)
3. **Deploy to production** (if needed)
4. **Monitor logs** and enjoy real-time AI responses!

🎉 **You're ready to make Jimmy work in real-time on Telegram!**

