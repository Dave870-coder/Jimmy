# 🚀 GitHub Hosting & Deployment Guide

This guide explains how to host the AI Bot Platform on GitHub and deploy it to production.

## 📋 Table of Contents
1. [GitHub Setup](#github-setup)
2. [Local Development](#local-development)
3. [Cloud Deployment](#cloud-deployment)
4. [GitHub Actions CI/CD](#github-actions-cicd)
5. [Troubleshooting](#troubleshooting)

---

## GitHub Setup

### 1. Create GitHub Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI Bot Platform with Google AI integration"

# Add remote repository
git remote add origin https://github.com/yourusername/ai-bot-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

```
GOOGLE_API_KEY          # Your Google AI API key
TELEGRAM_BOT_TOKEN      # Your Telegram bot token
WHATSAPP_ACCESS_TOKEN   # WhatsApp token (if using)
DATABASE_URL            # Production database URL
REDIS_URL              # Production Redis URL
SECRET_KEY             # Random secure key for JWT
```

### 3. Update `.gitignore`

The project includes `.gitignore` but verify it contains:

```
.env
.env.local
.env.*.local
.venv/
venv/
__pycache__/
*.pyc
.DS_Store
.idea/
.vscode/
dist/
build/
*.egg-info/
```

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-bot-platform.git
cd ai-bot-platform
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 3. Configure Environment Variables

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your credentials
nano .env  # Or use your editor
```

**Required variables:**
```
GOOGLE_API_KEY=your-google-ai-key
TELEGRAM_BOT_TOKEN=your-telegram-token
APP_ENV=development
DEBUG=True
```

### 4. Run Locally

```bash
# Start development server
uvicorn src.main:app --reload

# In another terminal, start Telegram bot
python run_telegram_bot.py

# Or run tests
pytest tests/

# Run local test suite
python local_test.py
```

---

## Cloud Deployment

### Option 1: Railway (⭐ Recommended - Easiest)

**Railway** is the easiest for hosting. It auto-detects Python apps and handles deployments.

#### Setup:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # In GitHub repo, go to Settings → Deploy keys
   # Add Railway's deploy key
   ```

3. **Configure Environment Variables**
   - Go to Railway Project
   - Click "Variables"
   - Add all variables from `.env.production`:
     ```
     GOOGLE_API_KEY=your-key
     TELEGRAM_BOT_TOKEN=your-token
     APP_ENV=production
     DEBUG=False
     DATABASE_URL=postgresql://...
     REDIS_URL=redis://...
     SECRET_KEY=generate-random-key
     ```

4. **Deploy**
   ```bash
   # Push to main branch
   git push origin main
   
   # Railway auto-deploys
   # Check status in Railway dashboard
   ```

5. **View Logs**
   ```bash
   # In Railway dashboard, click "Logs"
   ```

---

### Option 2: Heroku

#### Setup:

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-ai-bot
   ```

3. **Add PostgreSQL & Redis**
   ```bash
   heroku addons:create heroku-postgresql:standard-0
   heroku addons:create heroku-redis:premium-0
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set GOOGLE_API_KEY=your-key
   heroku config:set TELEGRAM_BOT_TOKEN=your-token
   heroku config:set SECRET_KEY=random-secure-key
   # ... set all other variables
   ```

5. **Create Procfile** (already exists in repo)
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Run Migrations**
   ```bash
   heroku run alembic upgrade head
   ```

---

### Option 3: AWS EC2

#### Setup:

1. **Launch EC2 Instance**
   - Use Ubuntu 22.04 LTS
   - Allow ports 80, 443, 8000

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3.12 python3-pip postgresql redis-server
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/ai-bot-platform.git
   cd ai-bot-platform
   ```

5. **Setup Python Environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

6. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Add production values
   ```

7. **Run with Systemd** (create `/etc/systemd/system/aibot.service`)
   ```ini
   [Unit]
   Description=AI Bot Platform
   After=network.target

   [Service]
   Type=notify
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ai-bot-platform
   Environment="PATH=/home/ubuntu/ai-bot-platform/venv/bin"
   ExecStart=/home/ubuntu/ai-bot-platform/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

8. **Start Service**
   ```bash
   sudo systemctl enable aibot
   sudo systemctl start aibot
   ```

---

### Option 4: Docker Hub & GitHub Container Registry

#### Build & Push Image

```bash
# Build image
docker build -t yourusername/ai-bot-platform:latest .

# Tag for Docker Hub
docker tag yourusername/ai-bot-platform:latest yourusername/ai-bot-platform:latest

# Push to Docker Hub
docker push yourusername/ai-bot-platform:latest

# Or push to GitHub Container Registry
docker tag yourusername/ai-bot-platform:latest ghcr.io/yourusername/ai-bot-platform:latest
docker push ghcr.io/yourusername/ai-bot-platform:latest
```

#### Run from Docker

```bash
docker run \
  -e GOOGLE_API_KEY=your-key \
  -e TELEGRAM_BOT_TOKEN=your-token \
  -p 8000:8000 \
  yourusername/ai-bot-platform:latest
```

---

## GitHub Actions CI/CD

The repository includes GitHub Actions workflow (`.github/workflows/tests.yml`) that:

✅ Runs tests on every push
✅ Checks code style and formatting
✅ Builds Docker image on main branch
✅ Reports test coverage

### View Test Results

1. Go to GitHub repository
2. Click **Actions** tab
3. See workflow runs and results

### Add More Secrets

The workflow requires these GitHub Secrets (for testing):

```
GOOGLE_API_KEY
TELEGRAM_BOT_TOKEN
```

Without them, tests that need API calls will be skipped.

---

## Production Best Practices

### 1. Environment Variables

**Never commit `.env`!** Use platform-specific secret management:

- **Railway**: Environment variables in dashboard
- **Heroku**: `heroku config:set`
- **AWS**: Parameter Store or Secrets Manager
- **Docker**: Docker Compose `env_file` or secrets

### 2. Database Backups

```bash
# Backup PostgreSQL
pg_dump -h host -U user -d database > backup.sql

# Restore
psql -h host -U user -d database < backup.sql
```

### 3. Monitoring

- Add Sentry for error tracking: `heroku config:set SENTRY_DSN=your-dsn`
- View logs: `heroku logs --tail` or platform dashboard
- Set up alerts for failures

### 4. Security

```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to production secrets
```

### 5. Rate Limiting

Set appropriate limits in `.env.production`:
```
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

---

## Troubleshooting

### Issue: "GOOGLE_API_KEY not configured"

**Solution:**
1. Check `.env` file exists and has the key
2. Verify API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Check for whitespace in `.env`

### Issue: "Telegram bot not responding"

**Solution:**
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check bot is running: `python run_telegram_bot.py`
3. Check firewall allows webhooks
4. Enable polling mode if webhook fails

### Issue: "Database connection failed"

**Solution:**
1. Check `DATABASE_URL` format
2. Verify database is running and accessible
3. For Railway: Add PostgreSQL addon, connection string auto-sets

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -e . --force-reinstall

# Or in venv
source venv/bin/activate
pip install -e . --force-reinstall
```

### Issue: "Gemini model not available"

**Solution:**
1. Check API key limits not exceeded
2. Update model in `.env`:
   ```
   GOOGLE_MODEL=gemini-2.0-flash-exp
   GOOGLE_MODEL=gemini-1.5-pro
   ```
3. Verify API key has Gemini access

---

## Support & Resources

- **Google AI Studio**: https://makersuite.google.com
- **Telegram Bot API**: https://core.telegram.org/bots
- **Railway Docs**: https://docs.railway.app
- **Heroku Docs**: https://devcenter.heroku.com

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Configure repository secrets
3. ✅ Choose hosting platform (Railway recommended)
4. ✅ Deploy and test
5. ✅ Monitor logs and errors
6. ✅ Set up backups

Your AI Bot is now ready to serve the world! 🚀
