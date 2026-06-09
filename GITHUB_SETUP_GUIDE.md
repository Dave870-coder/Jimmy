# GitHub Setup & Deployment Guide

## Step 1: Initialize Local Git Repository

```powershell
# Open terminal in project directory
cd "C:\Users\Dave\3D Objects\jimmy"

# Configure Git
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

# Initialize repository
git init

# Check status
git status
```

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `jimmy-ai-bot` (or your choice)
   - **Description:** "AI Bot Platform powered by Google Gemini, integrated with Telegram and WhatsApp"
   - **Public or Private:** Choose public (easier deployment) or private (more secure)
   - **Add .gitignore:** Python
   - **Add README:** No (we have one)
3. Click **"Create repository"**

## Step 3: Add Remote and Push Code

```powershell
# Add GitHub as remote (replace USERNAME and REPO)
git remote add origin https://github.com/YOUR_USERNAME/jimmy-ai-bot.git

# Verify remote
git remote -v

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Jimmy AI Bot production ready"

# Push to GitHub
git push -u origin main
```

**If you get error:** `fatal: not a valid object name`
```powershell
# Rename default branch to main
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

1. Go to your repo: `https://github.com/YOUR_USERNAME/jimmy-ai-bot`
2. You should see all files there
3. Check that `.env` is NOT shown (protected by .gitignore)

## Step 5: Add GitHub Secrets

These allow deployment platforms to access your API keys without exposing them.

**Steps:**
1. Go to GitHub repo
2. Click **Settings** (top right)
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **New repository secret**

**Add these secrets:**

### Secret 1: GOOGLE_API_KEY
- Name: `GOOGLE_API_KEY`
- Value: Your Google AI Studio key
- Click **Add secret**

### Secret 2: TELEGRAM_BOT_TOKEN
- Name: `TELEGRAM_BOT_TOKEN`
- Value: Your Telegram bot token
- Click **Add secret**

### Secret 3: WHATSAPP_ACCESS_TOKEN (Optional)
- Name: `WHATSAPP_ACCESS_TOKEN`
- Value: Your WhatsApp token
- Click **Add secret**

### Secret 4: SECRET_KEY
- Name: `SECRET_KEY`
- Value: Generate a strong key (or use the one from your .env)
- Click **Add secret**

## Verify Secrets Added

In GitHub:
- Go to **Settings → Secrets and variables → Actions**
- You should see all 4 secrets listed (values hidden)

---

## 🚀 Now Ready for Deployment!

Once you have:
- ✅ Code pushed to GitHub
- ✅ All secrets added
- ✅ .env file locally (not on GitHub)

You can deploy to:
- **Railway** (recommended): [See Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)
- **Render**: [See Render Deployment Guide](RENDER_DEPLOYMENT_GUIDE.md)
- **Heroku**: [See Heroku Deployment Guide](HEROKU_DEPLOYMENT_GUIDE.md)

---

## Troubleshooting

### Error: "fatal: cannot create directory"
- Make sure you're in the correct directory
- Run: `pwd` (Mac/Linux) or `cd` (Windows)
- Should show: `C:\Users\Dave\3D Objects\jimmy`

### Error: "permission denied"
- On Windows: Open PowerShell as Administrator
- On Mac/Linux: Use `sudo` if needed

### Error: "failed to push"
- Check remote: `git remote -v`
- Should show: `https://github.com/YOUR_USERNAME/jimmy-ai-bot.git`
- Check credentials: GitHub may ask for personal access token

### Create GitHub Personal Access Token

If GitHub asks for authentication:
1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Give it permissions: `repo, workflow`
4. Copy token
5. When Git asks for password, paste the token

---

## Next Steps

1. **Test locally:** `python run_bot.py`
2. **Push to GitHub:** `git push`
3. **Deploy to Railway/Render:** Follow deployment guide
4. **Test live:** Open Telegram, send message to bot
5. **Monitor:** Check logs in deployment platform

---

**Your bot is now version-controlled and ready for production!**
