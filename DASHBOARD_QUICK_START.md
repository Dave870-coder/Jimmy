# 🎯 Jimmy Bot Dashboard - Quick Start Guide

## 🚀 Access Your Dashboard

**Live URL:** https://Dave870-coder.github.io/Jimmy/

---

## ⚙️ Step 1: Configure API Connection

The dashboard needs to connect to your Jimmy Bot backend API.

### Option A: Local Development (Localhost)
If running the bot locally on your computer:

1. Open the dashboard settings
2. Set **API Base URL** to: `http://localhost:8000`
3. The dashboard will auto-connect

### Option B: Production (Render/Railway)
If you deployed the bot to Render or Railway:

1. Get your bot's deployment URL (e.g., `https://jimmy-bot-abc123.onrender.com`)
2. In dashboard settings, set **API Base URL** to your deployment URL
3. Click **Save** and refresh

### Option C: GitHub Actions (Recommended)
Set `NEXT_PUBLIC_API_BASE` environment variable:

```bash
# In .env.local (local development)
NEXT_PUBLIC_API_BASE=http://localhost:8000

# In GitHub repo settings
Secrets > New repository secret
Name: NEXT_PUBLIC_API_BASE
Value: https://your-bot-url.onrender.com
```

---

## 📊 Step 2: Understand Dashboard Sections

### 🏠 Home Tab
- Real-time analytics overview
- Active users count
- Total messages processed
- Average response time
- Bot connection status

### 📈 Analytics Tab (NEW)
- Message trends over time
- User growth chart
- Response time metrics
- Workflow completion rates
- Export analytics as CSV/JSON

### 👥 Users Tab (NEW)
- Complete user management
- User activity history
- Block/unblock users
- User preferences
- Search and filter users

### 💬 Messages Tab (NEW)
- View all bot messages
- Search message history
- Filter by user/channel
- Message export
- Conversation threads

### 📊 Performance Tab (NEW)
- Real-time performance metrics
- API response times
- Database query performance
- Cache hit rates
- Error tracking

### ⚙️ Settings Tab
- Add API keys (Telegram, Google AI, OpenAI, WhatsApp)
- Configure webhook URLs
- Database connection settings
- Toggle features on/off
- View integration status

### 📱 Integrations Tab
- Telegram webhook setup
- WhatsApp QR code scanner
- Connection status
- Integration health checks

---

## 🔑 Step 3: Add API Keys

Navigate to **Settings** tab and fill in:

| Key | Where to Get | Required? |
|-----|--------------|-----------|
| **Telegram Bot Token** | [@BotFather](https://t.me/botfather) on Telegram | ✅ Yes |
| **Google AI API Key** | [Google AI Studio](https://aistudio.google.com) | ✅ Yes |
| **OpenAI API Key** | [OpenAI Platform](https://platform.openai.com) | ⚠️ Optional |
| **WhatsApp Access Token** | WhatsApp Business API dashboard | ⚠️ Optional |
| **Telegram Webhook Secret** | Generate any strong random string | ⚠️ Optional |
| **Public Base URL** | Your deployed bot URL | ✅ Yes |
| **Database URL** | SQLite path or PostgreSQL URL | ✅ Yes |

Click **Save Production Settings** when done.

---

## 🔄 Step 4: Connect Telegram Bot

1. Go to **Integrations** tab
2. Copy the Telegram webhook URL
3. Open [@BotFather](https://t.me/botfather) on Telegram
4. Send: `/setwebhook`
5. Follow the prompts and paste the URL

---

## 💬 Step 5: Connect WhatsApp (QR Code)

1. Go to **Integrations** tab
2. Click **Start WhatsApp Connection**
3. A QR code will appear
4. Open WhatsApp on your phone
5. Go to **Settings** → **Linked Devices** → **Link a Device**
6. Scan the QR code from dashboard
7. Wait for connection confirmation

---

## 📊 Features Overview

### Real-Time Analytics
- Live user activity tracking
- Message volume graphs
- Response time trends
- Workflow performance metrics
- Export capabilities

### User Management
- View all connected users
- Track user activity
- Manage user permissions
- Export user list
- User segmentation

### Message History
- Complete chat history
- Search across all messages
- Filter by date/user/channel
- Export conversations
- Analytics per conversation

### Performance Monitoring
- API response times
- Database performance
- Cache efficiency
- Error rates
- System resource usage

---

## 🔧 Troubleshooting

### "API status: Loading..." keeps showing
- Check if backend is running
- Verify `NEXT_PUBLIC_API_BASE` is set correctly
- Check browser console for errors (F12)
- Ensure backend `/health` endpoint is accessible

### Settings won't save
- Check if API key is correct
- Verify settings endpoint `/api/v1/admin/settings` exists
- Check for CORS errors in browser console
- Try saving without special characters first

### WhatsApp QR not appearing
- Ensure WhatsApp integration is enabled in `.env`
- Check backend logs for QR generation errors
- Try refreshing the page
- Clear browser cache if needed

### Telegram webhook not connecting
- Verify bot token is correct
- Check webhook URL is publicly accessible
- Ensure HTTPS is being used (not HTTP)
- Test webhook with: `curl -X POST https://your-url/api/v1/telegram/webhook`

---

## 📚 Next Steps

1. ✅ Configure API connection
2. ✅ Add your API keys
3. ✅ Connect Telegram bot
4. ✅ Set up WhatsApp (optional)
5. ✅ Monitor analytics
6. ✅ Manage users

Your Jimmy Bot is now fully operational! 🚀

---

## 📞 Support

- **Issues?** Check [Configuration Guide](DASHBOARD_CONFIG.md)
- **Deployment issues?** See [Backend Deployment](BACKEND_DEPLOYMENT.md)
- **Feature requests?** Open an issue on GitHub
