# Deployment Environment Templates

## 🚀 Heroku Deployment

### 1. Procfile
```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
worker: python -c "from src.bot.telegram.handler import get_telegram_bot; import asyncio; asyncio.run(get_telegram_bot().run_polling())"
```

### 2. runtime.txt
```
python-3.12.0
```

### 3. Setup Commands
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0
heroku config:set GOOGLE_API_KEY=your-key
heroku config:set TELEGRAM_BOT_TOKEN=your-token
git push heroku main
heroku run alembic upgrade head
```

## 🚀 Railway Deployment

### 1. railway.json
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### 2. Setup Commands
```bash
railway init
railway link
railway up
```

### 3. Environment Variables
- Set via Railway Dashboard
- GOOGLE_API_KEY
- TELEGRAM_BOT_TOKEN
- WHATSAPP_ACCESS_TOKEN (if applicable)
- DATABASE_URL (auto-set if using Railway PostgreSQL)

## 🚀 AWS EC2 Deployment

### 1. Instance Setup
```bash
# Connect to EC2 instance
ssh -i key.pem ubuntu@<public-ip>

# Install dependencies
sudo apt update
sudo apt install python3.12 python3-pip postgresql redis-server

# Clone repository
git clone https://github.com/your-repo/ai-bot-platform.git
cd ai-bot-platform

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Systemd Service
Create `/etc/systemd/system/aibot.service`:
```ini
[Unit]
Description=AI Bot Platform
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-bot-platform
Environment="PATH=/home/ubuntu/ai-bot-platform/.venv/bin"
ExecStart=/home/ubuntu/ai-bot-platform/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable aibot
sudo systemctl start aibot
```

### 4. Nginx Configuration
```nginx
upstream aibot {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://aibot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚀 Docker Deployment

### 1. Build and Run Locally
```bash
docker build -t ai-bot-platform .
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your-key \
  -e TELEGRAM_BOT_TOKEN=your-token \
  ai-bot-platform
```

### 2. Docker Compose
```bash
docker-compose up -d
```

## 🚀 GCP Cloud Run

### 1. Deploy
```bash
gcloud run deploy aibot \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your-key,TELEGRAM_BOT_TOKEN=your-token
```

### 2. Environment Variables
Set via Cloud Run console or CLI

## 🚀 Azure Container Instances

### 1. Build Image
```bash
az acr build --registry <registry-name> --image aibot:latest .
```

### 2. Deploy
```bash
az container create \
  --resource-group <group-name> \
  --name aibot \
  --image <registry>.azurecr.io/aibot:latest \
  --environment-variables GOOGLE_API_KEY=your-key TELEGRAM_BOT_TOKEN=your-token
```

## 📋 Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Logs directory created
- [ ] Secrets properly encrypted
- [ ] API keys validated
- [ ] Health check endpoints working
- [ ] CORS settings configured for domain
- [ ] SSL/HTTPS enabled
- [ ] Monitoring/logging configured (Sentry, etc.)
- [ ] Backup strategy in place
- [ ] Rate limiting configured
- [ ] Database backups scheduled

## 🔒 Security Checklist

- [ ] All secrets in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] API keys rotated
- [ ] Database password strong
- [ ] HTTPS enforced
- [ ] CORS origins whitelisted
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention (using parameterized queries)
- [ ] CSRF protection enabled

## 📊 Monitoring Setup

### Sentry (Error Tracking)
```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

### Prometheus (Metrics)
- Configured on port 9090
- Metrics available at `/metrics`

### Logs
- All logs written to `./logs/`
- Configure log rotation in production
- Use centralized logging (CloudWatch, Stackdriver, etc.)

## 🚨 Troubleshooting

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify database is running
   - Check network connectivity

2. **API Keys Not Working**
   - Verify key format
   - Check for whitespace in .env
   - Confirm API quotas not exceeded

3. **Telegram Bot Not Responding**
   - Verify TELEGRAM_BOT_TOKEN
   - Check webhook URL is correct
   - Ensure firewall allows connections

4. **High Memory Usage**
   - Check for memory leaks in agent code
   - Review database connection pool settings
   - Monitor Redis memory usage
