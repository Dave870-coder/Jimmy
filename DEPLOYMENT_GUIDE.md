# 🚀 Deployment Instructions - Google AI + Telegram + WhatsApp Bot

This guide will help you deploy your AI Bot Platform to production on various cloud platforms.

---

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ Google API Key configured
- ✅ Telegram Bot Token configured
- ✅ WhatsApp credentials (if using WhatsApp)
- ✅ Docker knowledge
- ✅ Git repository set up

---

## 🌍 Deployment Options

Choose the platform that best fits your needs:

| Platform | Ease | Cost | Scale | Notes |
|----------|------|------|-------|-------|
| **Heroku** | ⭐⭐⭐⭐⭐ | Free-$25/mo | 10K users | Best for quick deployment |
| **Railway** | ⭐⭐⭐⭐⭐ | $5-50/mo | 10K users | Modern alternative to Heroku |
| **Render** | ⭐⭐⭐⭐ | Free-$25/mo | 10K users | Good free tier |
| **AWS** | ⭐⭐⭐ | Pay-as-you-go | 100K+ users | Most flexible, steeper learning |
| **DigitalOcean** | ⭐⭐⭐⭐ | $5-300+/mo | 100K+ users | Simple VPS + App Platform |
| **Google Cloud** | ⭐⭐⭐ | Pay-as-you-go | 100K+ users | Native GCP integration |

---

## 🚀 Option 1: Heroku (Easiest - Recommended for Beginners)

### 1.1 Install Heroku CLI
```bash
# Windows (with Scoop)
scoop install heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### 1.2 Login and Create App
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-bot-name

# Verify
git remote -v
```

### 1.3 Add PostgreSQL and Redis
```bash
# Add PostgreSQL (free tier)
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis (free tier)
heroku addons:create heroku-redis:premium-0
```

### 1.4 Set Environment Variables
```bash
heroku config:set GOOGLE_API_KEY=your-api-key
heroku config:set TELEGRAM_BOT_TOKEN=your-token
heroku config:set GOOGLE_MODEL=gemini-pro
heroku config:set SECRET_KEY=your-secret-key
```

### 1.5 Create Procfile
Create file `Procfile` in repo root:
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
worker: python run_telegram_bot.py
```

### 1.6 Deploy
```bash
git push heroku main
```

### 1.7 Run Migrations
```bash
heroku run alembic upgrade head
```

### 1.8 Start Telegram Bot
```bash
heroku ps:scale worker=1
```

### 1.9 Verify
```bash
heroku logs --tail
```

---

## 🚀 Option 2: Railway.app (Modern & Easy)

### 2.1 Create Account
Visit: https://railway.app

### 2.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub"
3. Choose your repo

### 2.3 Add PostgreSQL Service
1. Click "Add Service"
2. Select "PostgreSQL"
3. Railway creates the DB automatically

### 2.4 Add Redis Service
1. Click "Add Service"
2. Select "Redis"
3. Railway creates the cache automatically

### 2.5 Configure Environment
1. Go to "Variables" tab
2. Add your environment variables:
   - `GOOGLE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `SECRET_KEY`

3. Railway will auto-set:
   - `DATABASE_URL`
   - `REDIS_URL`

### 2.6 Deploy
1. Click "Deploy"
2. Railway automatically detects and deploys

### 2.7 View Logs
```bash
# In Railway dashboard
Logs → API
```

---

## 🚀 Option 3: Render.com (Free Tier Available)

### 3.1 Create Account
Visit: https://render.com

### 3.2 Create Web Service
1. Click "New +"
2. Select "Web Service"
3. Connect GitHub repo

### 3.3 Configure
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### 3.4 Add Database
1. Create PostgreSQL instance
2. Copy connection string to environment

### 3.5 Add Redis
1. Create Redis instance
2. Copy URL to environment

### 3.6 Set Environment Variables
- `GOOGLE_API_KEY=...`
- `TELEGRAM_BOT_TOKEN=...`
- `DATABASE_URL=...` (from PostgreSQL)
- `REDIS_URL=...` (from Redis)

### 3.7 Deploy
Click "Create Web Service" to deploy

---

## ☁️ Option 4: AWS (For Scale)

### 4.1 Setup Elastic Beanstalk
```bash
# Install AWS CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 my-bot

# Create environment
eb create production --instance-type t3.micro
```

### 4.2 Add RDS PostgreSQL
```bash
# Via AWS Console
RDS → Create DB → PostgreSQL → Free tier
```

### 4.3 Add ElastiCache Redis
```bash
# Via AWS Console
ElastiCache → Create → Redis → Free tier
```

### 4.4 Configure Environment
```bash
# In .ebextensions/env.config
environment:
  GOOGLE_API_KEY: your-key
  TELEGRAM_BOT_TOKEN: your-token
  DATABASE_URL: postgres://...
  REDIS_URL: redis://...
```

### 4.5 Deploy
```bash
git add .
git commit -m "Deploy to AWS"
eb deploy
```

---

## 🐳 Option 5: Docker + VPS (DigitalOcean, Linode, etc.)

### 5.1 Create VPS
- DigitalOcean: $5/month (1GB RAM, 25GB SSD)
- Choose Ubuntu 22.04

### 5.2 SSH into Server
```bash
ssh root@your_server_ip
```

### 5.3 Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
bash get-docker.sh
```

### 5.4 Clone Repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 5.5 Create .env File
```bash
nano .env
# Paste your configuration
```

### 5.6 Deploy
```bash
docker-compose up -d
```

### 5.7 Setup Reverse Proxy (Nginx)
```bash
# Install Nginx
apt-get update && apt-get install -y nginx

# Create config
nano /etc/nginx/sites-available/bot

# Content:
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}

# Enable
ln -s /etc/nginx/sites-available/bot /etc/nginx/sites-enabled/
systemctl restart nginx
```

### 5.8 Setup SSL (Let's Encrypt)
```bash
apt-get install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## 📱 Setup Telegram Webhook (Production)

### For Heroku/Railway/Render:

```bash
# Set webhook URL
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-deployment-url/api/v1/telegram/webhook"}'

# Verify
curl -X POST https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

### Remove Webhook (to use polling)
```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": ""}'
```

---

## 📱 Setup WhatsApp Webhook (Production)

### 1. Get Public Domain
- Option A: Purchase domain (namecheap.com, etc.)
- Option B: Free domain (if using free tier)
- Your webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`

### 2. Facebook Setup
1. Go to your Facebook App
2. Go to WhatsApp → Configuration
3. Enter webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`
4. Enter verify token (the one in `.env`)

### 3. Test Webhook
```bash
# Verify token endpoint
curl -X GET "https://yourdomain.com/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.challenge=TEST_STRING&hub.verify_token=your_token"

# Should return: TEST_STRING
```

---

## 🔍 Monitoring in Production

### Add Prometheus & Grafana

### Create `docker-compose.prod.yml`
```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
```

### Start Monitoring
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Access
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

---

## 📊 Performance Tips

### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_messages_user_created ON messages(user_id, created_at);
CREATE INDEX idx_memories_user_id ON memories(user_id);

-- Run VACUUM
VACUUM ANALYZE;
```

### 2. Redis Optimization
```bash
# Monitor Redis
redis-cli INFO stats

# Clear old data
redis-cli FLUSHDB
```

### 3. API Optimization
```python
# In production, increase rate limits
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600  # per hour
```

---

## 🚨 Production Checklist

Before going live:

- [ ] All API keys configured securely
- [ ] Database encrypted
- [ ] Redis enabled
- [ ] Rate limiting configured
- [ ] Logging enabled
- [ ] Monitoring setup
- [ ] SSL/TLS certificate installed
- [ ] Backup system configured
- [ ] Error monitoring (Sentry, etc.)
- [ ] Load testing completed
- [ ] Security audit done
- [ ] Database migrations applied
- [ ] Telegram webhook verified
- [ ] WhatsApp webhook verified (if using)

---

## 🔐 Security in Production

### Environment Variables
```bash
# Use secure secrets manager
# DO NOT commit .env to Git
echo ".env" >> .gitignore
git rm --cached .env
```

### Database Security
```bash
# Use strong passwords
# Change default credentials
# Enable encryption at rest
```

### API Security
```python
# In config.py
CORS_ORIGINS = ["https://yourdomain.com"]
DEBUG = False
```

### Monitoring
```bash
# Monitor for suspicious activity
docker-compose logs -f | grep -i error
```

---

## 📞 Troubleshooting Deployment

### Issue: "Database connection failed"
```bash
# Check database is running
heroku ps  # or railway ps

# Check connection string
heroku config | grep DATABASE_URL
```

### Issue: "Telegram bot not responding"
```bash
# Check webhook is set
curl -X POST https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Check logs
heroku logs --tail
```

### Issue: "Port already in use"
```bash
# Kill process
lsof -i :8000
kill -9 <PID>
```

### Issue: "Out of memory"
```bash
# Scale up
heroku dyno:type premium-1x

# Or optimize code
# Reduce batch sizes
# Clear old data
```

---

## 💰 Cost Estimation

### Monthly Costs

| Component | Heroku | Railway | AWS | VPS |
|-----------|--------|---------|-----|-----|
| Web Server | $7 | $5 | $0-30 | $5 |
| Database | Free | $5 | $0-50 | $0 |
| Redis | Free | $5 | $0-30 | $0 |
| Domain | - | - | - | $1-3 |
| **Total** | **$7+** | **$15+** | **$0-110+** | **$6+** |

---

## 🚀 Next Steps

1. Choose your deployment platform
2. Follow the guide for that platform
3. Deploy your bot
4. Test in Telegram/WhatsApp
5. Monitor logs and performance
6. Scale as needed

---

## 📚 Additional Resources

- **Heroku Docs**: https://devcenter.heroku.com
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **AWS Docs**: https://docs.aws.amazon.com
- **Docker Docs**: https://docs.docker.com

---

**Happy deploying!** 🎉

Once deployed, your bot will:
- ✅ Run 24/7 in the cloud
- ✅ Scale automatically
- ✅ Handle thousands of users
- ✅ Use Google AI for responses
- ✅ Connect to Telegram and WhatsApp
