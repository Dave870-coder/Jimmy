# 🚀 Seamless Deployment Guide - Render + GitHub Pages

**Status: READY FOR DEPLOYMENT** ✅

This guide covers deploying your Jimmy AI Bot with:
- **Backend**: Render (FREE tier - runs 24/7)
- **Frontend Dashboard**: GitHub Pages (FREE)

---

## 📋 Pre-Deployment Checklist

### 1. GitHub Repository Setup ✅
- [ ] Repository is public (required for GitHub Pages)
- [ ] `main` branch is protected
- [ ] All code is committed to `main` branch
- [ ] `.python-version` file exists (contains `3.12`)
- [ ] `runtime.txt` exists (contains `python-3.12.7`)

### 2. Environment Variables ✅
Set these in Render Dashboard under **Environment**:

**Essential (Required):**
```
GOOGLE_API_KEY=your-google-ai-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
SECRET_KEY=your-secure-secret-key
```

**Optional (Auto-configured):**
```
PUBLIC_BASE_URL=https://jimmy-ai-bot.onrender.com
DATABASE_URL=sqlite:////opt/data/bot.db
APP_ENV=production
DEBUG=False
```

### 3. Render Configuration ✅
- [ ] Service connected to GitHub repository
- [ ] Service name: `jimmy-ai-bot`
- [ ] Python version: `3.12`
- [ ] Region: Oregon (or your choice)
- [ ] Plan: Free tier
- [ ] Build command: `bash ./build.sh`
- [ ] Start command: `python run_bot.py`

### 4. GitHub Pages Configuration ✅
- [ ] GitHub Actions enabled in repository settings
- [ ] Pages source set to "GitHub Actions"
- [ ] Workflow files in `.github/workflows/`

---

## 🚀 Deployment Steps

### Step 1: Deploy Backend to Render (5 minutes)

**If using Render Blueprint (Recommended):**
1. Click: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/Jimmy)
2. Authorize with GitHub
3. Add environment variables (see Pre-Deployment Checklist)
4. Click "Create Web Service"
5. Wait for build to complete (~3-5 minutes)
6. Service URL: `https://jimmy-ai-bot.onrender.com`

**If using manual setup:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "+ New" → "Web Service"
3. Select your GitHub repository
4. Configure as per Pre-Deployment Checklist
5. Deploy

### Step 2: Deploy Dashboard to GitHub Pages (1 minute)

The dashboard deploys automatically when you:
1. Push changes to `dashboard/**` folder to `main` branch
2. Or manually trigger from GitHub Actions
3. Watch deployment at: https://github.com/YOUR_USERNAME/Jimmy/actions

After deployment, your dashboard is live at:
```
https://YOUR_USERNAME.github.io/Jimmy
```

### Step 3: Verify Both Deployments

**Backend (Render):**
```bash
# Check health endpoint
curl https://jimmy-ai-bot.onrender.com/health

# Expected response:
# {"status": "healthy", "database": "ready", ...}
```

**Frontend (GitHub Pages):**
```
Visit: https://YOUR_USERNAME.github.io/Jimmy
```

---

## 🔧 Configuration Files Explained

### render.yaml
- **Build Command**: `bash ./build.sh` - Installs dependencies and initializes database
- **Start Command**: `python run_bot.py` - Starts FastAPI with proper error handling
- **Health Check**: `/health` endpoint - Render pings every 10 seconds
- **Auto Restart**: Enabled - Service restarts on crash

### run_bot.py
- Handles PORT environment variable from Render
- Sets WEB_CONCURRENCY to 1 (free tier memory constraint)
- Creates fallback app if initialization fails
- Logs startup progress

### build.sh
- Upgrades pip, setuptools, wheel
- Installs requirements.txt
- Verifies all core dependencies
- Initializes database (safe to fail)

### dashboard/next.config.js
- **basePath**: `/Jimmy` for GitHub Pages routing
- **output**: `export` for static HTML export
- **API rewrites**: Routes API calls to backend
- **Environment**: Uses NEXT_PUBLIC_* variables

---

## 📊 Monitoring & Debugging

### View Logs in Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service
3. Click "Logs" tab

### Common Issues & Solutions

**Issue: Service won't start**
```
❌ Solution:
1. Check logs for Python import errors
2. Verify all requirements.txt packages installed
3. Check environment variables set correctly
```

**Issue: Database initialization fails**
```
❌ Solution:
1. Check /opt/data directory has write permissions
2. Verify DATABASE_URL is correct
3. Check disk space (Render free tier limited)
```

**Issue: Dashboard not loading**
```
❌ Solution:
1. Check basePath is /Jimmy in next.config.js
2. Verify workflow deployed successfully
3. Clear browser cache and refresh
```

**Issue: API calls fail from dashboard**
```
❌ Solution:
1. Verify backend is running (check /health endpoint)
2. Check NEXT_PUBLIC_API_BASE in workflow secrets
3. Verify CORS enabled in src/main.py
```

---

## 🎯 What Happens During Deployment

### Render Build Process
```
1. Checkout code from GitHub
2. Set Python 3.12
3. Run: bash ./build.sh
   - Upgrade pip/setuptools/wheel
   - Install requirements.txt
   - Verify FastAPI, SQLAlchemy, Pydantic
   - Initialize SQLite database
4. Ready for start
```

### Render Start Process
```
1. Run: python run_bot.py
   - Load configuration
   - Create FastAPI app
   - Initialize database (lazy if needed)
   - Start uvicorn on PORT
2. Render health checks /health every 10s
3. If unhealthy 3+ times: restart service
4. Service ready at: https://jimmy-ai-bot.onrender.com
```

### GitHub Pages Build Process
```
1. Detect change in dashboard/
2. Run: npm ci (clean install)
3. Run: npm run build (Next.js static export)
4. Deploy /dashboard/out to GitHub Pages
5. Available at: https://USERNAME.github.io/Jimmy
```

---

## 🔐 Security Best Practices

### 1. Never commit secrets
```bash
# ✅ GOOD: Use .env (in .gitignore)
GOOGLE_API_KEY=xxx

# ❌ BAD: Hardcode in source
API_KEY = "secret"
```

### 2. Use GitHub Secrets for CI/CD
```
Settings → Secrets and variables → Actions
- NEXT_PUBLIC_API_BASE (optional)
```

### 3. Environment variables in Render
```
Dashboard → Environment → Environment Variables
Only add sensitive vars (API keys, tokens)
```

---

## 📈 Scaling & Performance

### Current Setup (Free Tier)
- **Backend**: 1 Python process, 512MB RAM
- **Database**: SQLite on 1GB persistent disk
- **Frontend**: Static files on GitHub Pages CDN
- **Connections**: Limited by Render free tier

### To Scale Up
1. Upgrade Render plan (paid tiers available)
2. Switch to PostgreSQL database
3. Add Redis caching layer
4. Use multiple backend instances

---

## ✅ Final Checklist Before Going Live

- [ ] Environment variables set in Render
- [ ] Backend service deployed and healthy
- [ ] Dashboard deployed to GitHub Pages
- [ ] Both URLs accessible from browser
- [ ] API calls work from dashboard to backend
- [ ] Telegram webhook configured (if using bot)
- [ ] Google AI key working
- [ ] No errors in Render logs
- [ ] No errors in GitHub Actions

---

## 🎉 You're Ready!

**Backend API**: https://jimmy-ai-bot.onrender.com
**Dashboard**: https://YOUR_USERNAME.github.io/Jimmy

Both services will automatically:
- ✅ Restart on failure
- ✅ Deploy on code push
- ✅ Scale as needed (paid plans)
- ✅ Maintain persistent data

Happy deploying! 🚀
