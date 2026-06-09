# 🚀 Jimmy Bot Backend - Render/Railway Deployment Guide

## Quick Deploy (1-Click)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Dave870-coder/Jimmy)

---

## Option 1: Deploy to Render (Recommended)

### Step 1: Click Deploy Button
- Link above will auto-redirect to Render
- Authorize with GitHub
- Review pre-filled environment variables

### Step 2: Add Your API Keys

In the deployment form, set these environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `GOOGLE_API_KEY` | From [Google AI Studio](https://aistudio.google.com) | ✅ Yes |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/botfather) | ✅ Yes |
| `SECRET_KEY` | Generate strong random key | ✅ Yes |
| `OPENAI_API_KEY` | From OpenAI (optional) | ⚠️ Optional |
| `WHATSAPP_ACCESS_TOKEN` | From WhatsApp Business | ⚠️ Optional |

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Deploy
- Click "Create Web Service"
- Render will build and deploy automatically
- Wait 3-5 minutes for deployment
- Your bot URL will be: `https://your-service-name.onrender.com`

### Step 4: Configure Telegram Webhook

After deployment completes:

```bash
# Replace with your bot token and service URL
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -d "url=https://your-service-name.onrender.com/api/v1/telegram/webhook"
```

### Step 5: Test

```bash
# Test health endpoint
curl https://your-service-name.onrender.com/health

# Should return: {"status":"ok"}
```

---

## Option 2: Deploy to Railway

### Step 1: Connect GitHub Repository

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway with GitHub
5. Select `Dave870-coder/Jimmy` repository

### Step 2: Configure Environment

Railway will detect `railway.toml` and auto-configure.

Manual configuration (if needed):

```bash
# In Railway dashboard, add variables:
GOOGLE_API_KEY=your-key
TELEGRAM_BOT_TOKEN=your-token
SECRET_KEY=generated-secret
OPENAI_API_KEY=optional
```

### Step 3: Deploy

- Click "Deploy"
- Railway will build and start container
- Wait 2-3 minutes for deployment
- Your URL will be shown in dashboard

### Step 4: Configure Telegram

```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d "url=https://your-railway-url.railway.app/api/v1/telegram/webhook"
```

---

## Option 3: Manual Docker Deployment

### Prerequisites
- Docker installed
- Docker Hub account (or private registry)

### Step 1: Build Docker Image

```bash
# From project root
docker build -t your-username/jimmy-bot:latest .

# Or use multi-platform build:
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-username/jimmy-bot:latest --push .
```

### Step 2: Push to Registry

```bash
# Login to Docker Hub
docker login

# Push image
docker push your-username/jimmy-bot:latest
```

### Step 3: Deploy on Cloud

#### On Render (via Docker):
1. Go to [Render.com](https://render.com)
2. Click "New Web Service"
3. Select "Docker"
4. Connect GitHub
5. Set environment variables
6. Deploy

#### On Railway (via Docker):
1. Push to GitHub
2. Connect to Railway
3. Railway auto-builds from Dockerfile
4. Deploy

#### On AWS ECS/Fargate:
1. Push image to ECR
2. Create ECS task definition
3. Deploy to Fargate cluster
4. Configure load balancer

---

## Post-Deployment Configuration

### Update Dashboard API URL

1. Go to GitHub repository settings
2. Navigate to: Settings > Secrets and variables > Actions
3. Create new secret:
   ```
   Name: NEXT_PUBLIC_API_BASE
   Value: https://your-deployed-url.onrender.com
   ```
4. Push a change to trigger dashboard rebuild
5. Wait for GitHub Pages deployment (~1 minute)

### Enable Telegram Webhook

After your bot is deployed:

```bash
# Set webhook (REQUIRED for Telegram to send updates)
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -d "url=https://your-bot-url.onrender.com/api/v1/telegram/webhook"

# Verify webhook
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "url": "https://your-bot-url.onrender.com/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "ip_address": "1.2.3.4",
    "last_error_date": null
  }
}
```

### Test Bot in Telegram

1. Message your bot on Telegram: `/start`
2. Should receive response from deployed bot
3. Test with: "hello" or any text
4. Bot should process and respond

---

## Environment Variables Reference

### Required
```env
GOOGLE_API_KEY=AIza...your-key...
TELEGRAM_BOT_TOKEN=123456:ABCdef...
SECRET_KEY=long-random-secure-string-here
```

### Optional but Recommended
```env
APP_ENV=production
DEBUG=False
PUBLIC_BASE_URL=https://your-deployed-url.onrender.com
OPENAI_API_KEY=sk-...optional...
WHATSAPP_ACCESS_TOKEN=optional
```

### Database
```env
# Use PostgreSQL for production (Render includes free database)
DATABASE_URL=postgresql://user:password@host:5432/database_name

# Or SQLite on persistent volume
DATABASE_URL=sqlite:////data/bot.db
```

### Render-Specific
```env
RENDER=true
RENDER_GIT_COMMIT=auto-set-by-render
RENDER_GIT_BRANCH=auto-set-by-render
```

---

## Monitoring & Logs

### View Logs on Render
```
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. See real-time logs
```

### View Logs on Railway
```
1. Go to Railway dashboard  
2. Select project
3. Click "Deployments"
4. Select deployment → "View Logs"
```

### Monitor Health

```bash
# Check if backend is running
curl https://your-deployed-url.onrender.com/health

# Check if ready for requests
curl https://your-deployed-url.onrender.com/ready

# Get status
curl https://your-deployed-url.onrender.com/status
```

---

## Troubleshooting Deployment

### Build Fails: "Missing dependencies"

**Solution:**
```bash
# Ensure requirements.txt is up-to-date:
pip freeze > requirements.txt
# Commit and push, redeploy
```

### Build Fails: "Python version not found"

**Solution:**
```bash
# Create runtime.txt in root:
echo "python-3.12.7" > runtime.txt
# Push and redeploy
```

### Service won't start: "Port already in use"

**Solution:**
- Render/Railway auto-assigns port
- Don't hardcode port, use environment variable
- Update code:
```python
import os
PORT = int(os.getenv("PORT", 8000))
```

### Service crashes after deployment

**Solution:**
1. Check logs for errors
2. Test locally: `python run_bot.py`
3. Verify environment variables set
4. Check database connection

### Webhook not receiving updates

**Solution:**
1. Verify webhook URL is accessible:
   ```bash
   curl https://your-url.onrender.com/api/v1/telegram/webhook
   ```

2. Check webhook is registered:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```

3. Re-register webhook:
   ```bash
   # Delete old
   curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook -d "url="
   
   # Register new
   curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
     -d "url=https://your-deployed-url.onrender.com/api/v1/telegram/webhook"
   ```

---

## Performance Optimization

### Database
- Use PostgreSQL for production (not SQLite)
- Enable connection pooling
- Add indexes on frequently queried columns

### Caching
- Enable Redis caching
- Cache analytics for 30 seconds
- Cache user data for 60 seconds

### API Rate Limiting
- Render/Railway have built-in rate limiting
- Implement in code for additional protection:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/admin/analytics")
@limiter.limit("100/minute")
async def get_analytics(request: Request):
    return {...}
```

---

## Cost Optimization

### Render
- Free tier: 1 web service + 1 database
- Paid tier: $7/month per service
- Auto-suspend after 15 min inactivity (free only)

### Railway
- Free tier: $5 credit/month
- Paid tier: pay-as-you-go ($0.50/GB RAM, etc.)
- No auto-suspend

### Database
- Render: PostgreSQL 100MB free
- Railway: included in credits
- Both auto-scale if needed

---

## Scaling for 7M Users

For production at scale:

1. **Use PostgreSQL** (not SQLite)
2. **Enable Redis caching** (Render/Railway add-on)
3. **Scale horizontally** with multiple instances
4. **Use CDN** for static assets (Cloudflare, etc.)
5. **Monitor performance** with Prometheus + Grafana
6. **Set up database replication** for high availability
7. **Use message queues** (Redis/RabbitMQ) for async tasks

---

## Next Steps

1. ✅ Deploy bot to Render/Railway
2. ✅ Set webhook for Telegram
3. ✅ Update dashboard API URL
4. ✅ Test in Telegram
5. ✅ Monitor logs
6. ✅ Scale as needed

Your Jimmy Bot is now live! 🚀

---

## Support

- **Render support:** support@render.com
- **Railway support:** support@railway.app
- **Project issues:** GitHub Issues
