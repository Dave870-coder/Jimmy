# 🚀 QUICK START: Enable Real-Time Telegram Bot

Get Jimmy working on Telegram in **5 minutes**!

---

## ⚡ Quick Summary

Jimmy's bot is **already built for real-time**, it just needs:
1. ✅ A real Telegram token (from @BotFather)
2. ✅ Your Google AI key (from makersuite.google.com)
3. ✅ Webhook registration (one-time setup)

Then users can **message your bot on Telegram and get AI responses instantly**.

---

## 🎯 5-Minute Setup

### Step 1: Create Telegram Bot (2 min)

Open Telegram, search for **@BotFather**, send:
```
/newbot
```

Choose a name and username. **Copy the token**, e.g.:
```
123456789:ABCdEF-ghijklmnopQrstuvWxyz_123456
```

### Step 2: Get Google AI Key (1 min)

1. Go to https://makersuite.google.com/app/apikey
2. Click **Create API Key**
3. **Copy the key**, e.g.: `AIza...`

### Step 3: Configure & Register (2 min)

Run the setup wizard:
```bash
python setup_telegram_webhook.py
```

It will:
- ✅ Ask for your token
- ✅ Ask for your public URL
- ✅ Register webhook with Telegram
- ✅ Save to `.env`

### Step 4: Test It!

Open Telegram, find your bot, send `/start`. 

You should see:
```
👋 Hi Friend! Welcome to AI Bot Platform!
🤖 I'm powered by Google AI and ready to help.
📚 Use /help for available commands.
```

Send any message → **Get an AI response in seconds!** ✨

---

## 🔧 Manual Configuration (Alternative)

If the setup wizard doesn't work, edit `.env` manually:

```env
# Replace test_token_123 with your real token
TELEGRAM_BOT_TOKEN=123456789:ABCdEF-ghijklmnopQrstuvWxyz_123456

# Replace test_google_key with your real key
GOOGLE_API_KEY=AIza...

# Your public URL (where Jimmy is deployed)
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhook

# Optional: random secret token
TELEGRAM_WEBHOOK_SECRET=my-secret-token-xyz
```

Then restart the bot:
```bash
python run_bot.py
```

---

## 🧪 Verify Setup

Check if everything is working:

```bash
python test_telegram_integration.py
```

You should see:
```
✅ Token Validity
✅ Webhook Registration  
✅ Webhook Endpoint
✅ Google AI Configuration
✅ Database Configuration

🎉 ALL TESTS PASSED!
```

---

## 📊 How It Works (Real-Time Flow)

```
User on Telegram
      ↓ (sends message)
Telegram Server
      ↓ (webhooks to)
Your Jimmy Backend
      ↓ (sends to)
Google AI
      ↓ (generates response)
Response → Telegram → User
      
⏱️ Total time: 1-5 seconds
```

---

## 🎮 Available Commands

Once set up, users can:

```
/start    - Welcome message
/help     - Show all commands
/status   - Check if bot is online
/clear    - Clear conversation
/search   - Search knowledge base
/memory   - View memories
/tasks    - View tasks
/settings - Configure bot

[Any message] → Get AI response
```

---

## 🚀 Deployment Checklist

- [ ] Real Telegram token set (not test_token_123)
- [ ] Real Google AI key set (not test_google_key)
- [ ] Webhook registered (`setup_telegram_webhook.py` ran)
- [ ] Bot tested on Telegram
- [ ] Response received in < 5 seconds
- [ ] Ready for production! 🎉

---

## 🆘 Troubleshooting

### "Invalid token"
- Check @BotFather for correct token
- No spaces!
- Format: `123456789:ABCdEF...`

### "Bot not responding"
- Check `.env` has real token & Google key
- Run: `python test_telegram_integration.py`
- Check logs: `tail -f logs/bot.log`

### "Webhook not registered"
- Run: `python setup_telegram_webhook.py`
- Verify public URL is correct
- For local testing, use ngrok: `ngrok http 8000`

### "API key not working"
- Get new key from https://makersuite.google.com/app/apikey
- Ensure it's in `.env` as `GOOGLE_API_KEY`
- Restart bot after setting

---

## 📚 Full Documentation

For more details, see:
- **Full setup guide:** [TELEGRAM_REALTIME_SETUP.md](TELEGRAM_REALTIME_SETUP.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API reference:** Generated from FastAPI docs at `/docs`

---

## ✨ You're All Set!

Your bot is now **live on Telegram** with **real-time AI responses**! 🎉

**Next steps:**
1. Invite friends to your bot
2. Watch real conversations happen
3. Monitor in the dashboard
4. Enjoy! 🚀

Questions? Check the troubleshooting section or read the full guide.

