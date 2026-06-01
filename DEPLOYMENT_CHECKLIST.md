# 📋 DEPLOYMENT EXECUTION CHECKLIST

Follow this checklist step-by-step to deploy your bot to GitHub and Railway.

---

## ✅ PRODUCTION HEALTH / STARTUP CHECKLIST

Before you hand traffic to a new deployment, verify these items:

- [ ] `python verify_production_startup.py` passes locally
- [ ] `python run_bot.py` or `python start_bot.py` starts cleanly
- [ ] `GOOGLE_API_KEY` is set in Google AI Studio and copied into Render
- [ ] `TELEGRAM_BOT_TOKEN` is set in Render for webhook delivery
- [ ] `/health` returns `200` on the deployed URL
- [ ] `/ready` returns ready after migrations complete
- [ ] Telegram webhook is registered on the public deployment URL
- [ ] WhatsApp QR connection returns both QR and barcode payloads
- [ ] `.env` stays local and secrets are configured in the host dashboard
- [ ] SQLite data is mounted on persistent storage, or a managed database is used
- [ ] Render logs show no repeated startup failures
- [ ] Telegram `/start` and WhatsApp message echo both respond successfully

---

## ✅ PHASE 1: LOCAL VERIFICATION (5 min)

### 1.1 Verify Production Setup
- [ ] Open PowerShell in project directory
- [ ] Run: `python verify_production_startup.py`
- [ ] **Expected**: 5/6 checks pass (environment variables are missing, which is OK)
- [ ] **Check log for**: 
  - ✅ Imports
  - ✅ Database
  - ✅ Configuration
  - ✅ Google AI
  - ✅ Telegram
 - [ ] **Confirm**: Google AI Studio key is the same one you plan to use in Render

### 1.2 Test Bot Locally
- [ ] Run: `python run_bot.py`
- [ ] **Expected**: App starts, shows "BOT READY" and listening on 0.0.0.0:8000
- [ ] **In another terminal**, test health endpoint:
  - Run: `curl http://localhost:8000/health`
  - **Expected**: Returns JSON with `"status": "healthy"`
- [ ] **Back in original terminal**, stop bot: `Ctrl+C`

### 1.3 Verify Git Setup
- [ ] Run: `git status`
- [ ] **Expected**: Shows modified/new files ready to commit
- [ ] Run: `git log --oneline | head -5`
- [ ] **Expected**: Shows previous commits (not empty)

---

## ✅ PHASE 2: GITHUB DEPLOYMENT (5 min)

### 2.1 Prepare Files
- [ ] `.env` file exists and is NOT tracked by Git
  - Check: `git status | grep -i env` (should NOT appear)
  - If appears, run: `git rm --cached .env` and commit
- [ ] `data/bot.db` file exists and IS tracked
  - Check: `git ls-files | grep bot.db` (should appear)
  - If not, run: `git add data/bot.db`
- [ ] `requirements.txt` exists
  - Check: `dir requirements.txt` (should exist)

### 2.2 Commit Changes
- [ ] Run: `git add .`
- [ ] Verify: `git status` (check what will be committed)
- [ ] Run: `git commit -m "🚀 Production deployment: AI bot with SQLite support and seamless online operation"`
- [ ] **Expected**: Commit shows 10-15+ files added/modified

### 2.3 Push to GitHub
- [ ] Run: `git push origin main`
- [ ] **Expected**: Output shows files uploaded
- [ ] **If fails** with authentication:
  - Check if GitHub CLI is installed: `gh --version`
  - Or configure SSH: `git config --global user.email "you@example.com"`

### 2.4 Verify on GitHub
- [ ] Go to: `https://github.com/yourusername/jimmy-ai-bot`
- [ ] Refresh page (F5)
- [ ] **Verify**:
  - [ ] Latest commit appears with your message
  - [ ] File count increased (new files visible in file list)
  - [ ] `.env` is NOT visible (secrets protected ✅)
  - [ ] `data/bot.db` is visible (database persisted ✅)
  - [ ] `requirements.txt` exists
  - [ ] `Procfile` exists and shows `web: python run_bot.py`
  - [ ] `verify_production_startup.py` exists
  - [ ] `run_bot.py` exists

---

## ✅ PHASE 3: RAILWAY DEPLOYMENT (10-15 min)

### 3.1 Create Railway Account
- [ ] Go to: https://railway.app
- [ ] Click "Login" or "Get Started"
- [ ] Click "Sign up with GitHub"
- [ ] Authorize Railway to access your GitHub account
- [ ] After login, you're in Railway dashboard

### 3.2 Create New Project
- [ ] In Railway dashboard, click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Search for: `jimmy-ai-bot` (or your repo name)
- [ ] Click on your repository
- [ ] Click "Deploy Now"
- [ ] **Wait**: Railway starts building (1-2 minutes)
- [ ] **Check**: Build logs appear in "Build" tab
  - Should see: Python dependencies installing
  - Should see: No errors in build

### 3.3 Add Environment Variables
- [ ] In Railway dashboard, find your project
- [ ] Click "Variables" tab
- [ ] Click "Add Variable" and add each one:

**Required Variables (copy exactly):**

```
Key: GOOGLE_API_KEY
Value: <paste your Google AI Studio key>

Key: TELEGRAM_BOT_TOKEN
Value: <paste your Telegram bot token>

Key: DATABASE_URL
Value: sqlite:////opt/data/bot.db

Key: APP_ENV
Value: production

Key: DEBUG
Value: False

Key: SECRET_KEY
Value: <generate a long random secret>
```

- [ ] After each variable, Railway auto-saves
- [ ] After all variables added, Railway auto-redeploys
- [ ] Wait for deployment to complete (2-3 minutes)

### 3.4 Monitor Deployment
- [ ] In Railway dashboard, watch "Logs" tab
- [ ] **Expected to see**:
  - `BOT READY`
  - `Listening on 0.0.0.0:8000`
  - No error messages (only INFO logs)
- [ ] **If Google AI fails**: verify the key in Render matches the one from Google AI Studio
- [ ] If you see errors:
  - Check "Build" tab for build errors
  - Check variable names for typos
  - Check .env file locally for reference values

### 3.5 Verify Deployment
- [ ] Find your deployment URL at top of Railway dashboard
  - Format: `https://your-app.railway.app`
- [ ] In browser, visit: `https://your-app.railway.app/health`
- [ ] **Expected response**:
  ```json
  {
    "status": "healthy",
    "environment": "production",
    ...
  }
  ```
- [ ] If you see error:
  - Wait 30 seconds (app might still starting)
  - Refresh (F5)
  - Check Railway logs for errors

---

## ✅ PHASE 4: TELEGRAM INTEGRATION (2 min)

### 4.1 Test Telegram Bot
- [ ] Open Telegram app
- [ ] Search for your bot (e.g., `@yourbotname`)
- [ ] Click "START"
- [ ] **Expected**: Bot responds with greeting message
- [ ] Send: `hello`
- [ ] **Expected**: Bot responds with message using Google AI
- [ ] If the bot replies with a fallback message, recheck `GOOGLE_API_KEY` in the host dashboard

### 4.2 If Bot Doesn't Respond
- [ ] Check Railway logs: see if message was received
- [ ] Verify Telegram token in Railway dashboard: matches `.env`
- [ ] Check Google AI API key is working: visit `/health` endpoint
- [ ] Restart Railway deployment:
  - Go to Railway → Deployments
  - Click "Restart"
  - Wait 30 seconds
  - Try Telegram again

---

## ✅ PHASE 5: POST-DEPLOYMENT (5 min)

### 5.1 Set Up Monitoring
- [ ] In Railway dashboard, go to "Monitor" tab
- [ ] **Check**:
  - [ ] CPU usage: 5-15% (idle) or 20-50% (active)
  - [ ] Memory: 100-300MB
  - [ ] Status: All green ✅

### 5.2 Configure Alerts (Optional)
- [ ] Click on "Settings" in Railway project
- [ ] Look for notification options
- [ ] Consider enabling alerts for:
  - Deployment failure
  - High CPU usage
  - Memory warnings

### 5.3 Plan Backup
- [ ] Download local backup of `data/bot.db` (if populated)
- [ ] Store safely in your local project folder
- [ ] Note: Railway provides auto-backups (included in service)
- [ ] If you move to Render-only hosting, keep the SQLite disk mount configured or switch to managed Postgres

### 5.4 Document Access
- [ ] Note your Railway URL: `https://your-app.railway.app`
- [ ] Bookmark health endpoint: `https://your-app.railway.app/health`
- [ ] Keep `.env` file safe (never commit!)

---

## ❌ TROUBLESHOOTING

### Bot won't start locally
```
Error: Module not found 'X'
→ Solution: pip install -r requirements.txt
```

### Build fails on Railway
```
Error in logs: ModuleNotFoundError
→ Solution: Check requirements.txt exists and is valid
→ Command: pip freeze > requirements.txt (then git push)
```

### Environment variables not working
```
Error: GOOGLE_API_KEY not found
→ Solution: Check variable names in Railway are EXACT (case-sensitive)
→ Check no typos: GOOGLE_API_KEY (not GOOGLE_API or GOOGLE_AI_KEY)
```

### Bot doesn't respond to Telegram
```
No response when sending message
→ Check: Railway health endpoint working (/health)
→ Check: Telegram token correct in Railway variables
→ Action: Restart deployment in Railway dashboard
```

### Database not persisting
```
Data lost after restart
→ Check: DATABASE_URL is correct: sqlite:///./data/bot.db
→ Check: data/bot.db is committed to GitHub
→ Action: Remove DATABASE_URL override if using PostgreSQL
```

### High memory usage
```
Memory > 500MB
→ Solution 1: Restart deployment (Deployments → Restart)
→ Solution 2: Check for memory leak in code
→ Solution 3: Upgrade Railway plan for more memory
```

---

## ✅ FINAL VERIFICATION

After deployment, verify everything works:

- [ ] **GitHub**: Code is pushed and visible at your repo
- [ ] **Railway**: Deployment shows "Success" status
- [ ] **Health**: `curl https://your-app.railway.app/health` returns 200
- [ ] **Telegram**: Bot responds to messages
- [ ] **Logs**: No error messages in Railway dashboard
- [ ] **Uptime**: Monitor tab shows healthy metrics
- [ ] **Data**: Database file exists and is accessible

---

## 🎉 SUCCESS INDICATORS

✅ When you see these, deployment is successful:

- Telegram bot responds to messages
- Health endpoint returns `{"status": "healthy"}`
- Railway shows no errors in logs
- Monitor tab shows normal CPU/memory usage
- Bot remains responsive for 5+ minutes (stability test)

---

## 📞 QUICK REFERENCE

| Task | Command | Expected |
|------|---------|----------|
| Verify | `python verify_production_startup.py` | 5/6 ✅ |
| Test Locally | `python run_bot.py` | "BOT READY" |
| Commit | `git commit -m "Deploy"` | Shows files |
| Push | `git push origin main` | Files uploaded |
| Deploy | Create Railway project | Build starts |
| Test Online | `curl .../health` | 200 OK |

---

## 📝 NOTES

- If something goes wrong, **check the logs first** (always tells you what's wrong)
- Railway provides free HTTPS - you don't need to configure SSL
- SQLite database will persist across restarts (stored in Railway volume)
- You can update your bot by: edit code → git push → Railway auto-deploys
- Keep `.env` file locally, never commit it (contains secrets)

---

**Your bot is ready to go live! 🚀**

Follow this checklist and you'll have a production-grade bot running 24/7 on Railway.

Need help? Check `DEPLOYMENT_READY.md` for more detailed instructions.
