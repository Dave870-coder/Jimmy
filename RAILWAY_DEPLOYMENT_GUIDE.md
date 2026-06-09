# Railway Deployment Guide (⭐ Recommended)

**Why Railway?**
- Free $5/month credit (enough for hobby bot)
- Auto-deploy from GitHub
- Zero configuration for Python
- Auto SSL/HTTPS
- 24/7 uptime
- Easy monitoring

---

## Prerequisites

- ✅ Code pushed to GitHub
- ✅ GitHub Secrets added (GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN, etc.)
- ✅ Bot tested locally
- ✅ Railway account (free at railway.app)

---

## Step 1: Connect to Railway

1. Go to: https://railway.app
2. Click **Login** (or create free account)
3. Click **New Project**
4. Select **"Deploy from GitHub repo"**

---

## Step 2: Authorize & Select Repository

1. **GitHub Authorization**: Click **"Connect GitHub"**
   - Authorize Railway to access your GitHub
   - Select which repos Railway can access (or allow all)
2. **Select Repository**: Choose `jimmy-ai-bot`
3. Click **"Deploy"**

---

## Step 3: Configure Environment

Railway auto-detects Python and creates a service!

**Wait for deployment to start**, then:

1. Click your **Service** (appears on page)
2. Click **"Variables"** tab
3. Add these environment variables:

```
GOOGLE_API_KEY = [your Google AI key]
TELEGRAM_BOT_TOKEN = [your Telegram token]
WHATSAPP_ACCESS_TOKEN = [your WhatsApp token] (optional)
SECRET_KEY = [generate strong key]
APP_ENV = production
DEBUG = False
DATABASE_URL = sqlite:///./data/bot.db
```

4. Click **"Add Variable"** for each one
5. Variables auto-sync to deployment

---

## Step 4: Verify Deployment

Wait ~3-5 minutes for deployment to complete.

**Check deployment status:**
1. Click **Deployments** tab
2. Look for green checkmark (✓ = success)
3. Click on deployment → see logs

**Get your public URL:**
1. Click **"Deployments"** tab
2. Look at the domain (e.g., `jimmy-ai-bot-production.up.railway.app`)
3. This is your bot's public URL!

---

## Step 5: Test Live Bot

### Test 1: Health Check
```powershell
curl https://your-railway-url.up.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test 2: Telegram Bot
1. Open Telegram
2. Find your bot (from @BotFather)
3. Send: `/start`
4. **Bot should respond from the cloud!**

### Test 3: Send Message
1. In Telegram: "What's 2+2?"
2. Bot responds: "Based on my calculations, 2+2 equals 4"

---

## Step 6: Set Up Telegram Webhook (Optional but Recommended)

For better Telegram integration:

1. In BotFather:
   - Send: `/mybots`
   - Select your bot
   - Select "API Token"
   
2. Send: `/setwebhook`

3. Enter your Railway URL:
   ```
   https://your-railway-url.up.railway.app/api/v1/telegram/webhook
   ```

4. BotFather confirms: "Webhook was set"

Now Telegram sends updates directly to your bot (faster)!

---

## Step 7: Monitor in Real-Time

1. Go to Railway dashboard
2. Click your project
3. Click **Logs** tab
4. See all bot activity in real-time!

**Look for lines like:**
```
INFO: Message from user: "Hello bot"
INFO: AI response generated
INFO: Message sent to Telegram
```

---

## Auto-Deploy on Code Changes

Once set up, Railway automatically:
- Watches your GitHub repo
- Detects new commits
- Rebuilds and redeploys
- Zero downtime!

**To trigger auto-deploy:**
```bash
# Make a change locally
echo "# Updated" >> README.md

# Commit and push
git add .
git commit -m "Update README"
git push origin main
```

Railway detects the push and redeploys automatically! ⚡

---

## Troubleshooting

### Problem: Deployment fails during build

**Solution:**
1. Check logs for error messages
2. Common issue: Python version mismatch
   - Add to repo: `.python-version` with: `3.12.7`
3. Commit and push
4. Railway auto-rebuilds

### Problem: Bot not responding

**Solution:**
1. Check `/health` endpoint (should return 200)
2. Check logs for errors
3. Verify all environment variables are set
4. Restart service: Click restart button on dashboard

### Problem: Database file not found

**Solution:**
1. Create `data` directory in repo: `mkdir data`
2. Create placeholder file: `touch data/.gitkeep`
3. Commit and push
4. Railway mounts the directory automatically

### Problem: WhatsApp/Telegram not connecting

**Solution:**
1. Verify tokens in **Variables** tab
2. Check for typos (copy from local .env)
3. Restart deployment
4. Check logs for auth errors

---

## Performance Tips

- ✅ Use persistent volume for database
- ✅ Enable caching for AI responses
- ✅ Monitor memory usage in logs
- ✅ Scale up if needed ($5 → $10/month)

---

## Cost & Billing

- **Free tier:** $5/month credit (included)
- **Beyond $5:** You only pay what you use
- **Typical hobby bot:** $2-4/month
- **Upgrade anytime:** Slider in settings

---

## Going Live at Custom Domain

Want your own domain (e.g., jimmybot.com)?

1. Buy domain from: GoDaddy, Namecheap, etc.
2. Go to Railway → **Settings** → **Custom Domain**
3. Point domain to Railway's DNS
4. Wait ~24 hours for DNS propagation

Now you have: `https://jimmybot.com` running on Railway!

---

## Next Steps

- ✅ Deployment complete!
- ✅ Bot running 24/7 online
- ✅ Auto-deploys from GitHub

**Now:**
1. Monitor logs daily
2. Add more features
3. Scale when needed
4. Share your bot with users!

---

**🎉 Your AI Bot is now LIVE!**

For help: Check Railway docs at https://docs.railway.app
