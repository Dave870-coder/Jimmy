# 🚀 RAILWAY ONE-CLICK DEPLOYMENT

Your bot code is on GitHub: https://github.com/Dave870-coder/Jimmy

## 🔗 ONE-CLICK RAILWAY DEPLOYMENT

**Click this link to deploy to Railway:**

👉 **https://railway.app/new**

Then follow these steps:

---

## 📋 RAILWAY SETUP (Copy & Paste Instructions)

### Step 1: Click Login with GitHub
- Click **"Login with GitHub"** button
- Authorize Railway to access your GitHub account
- You'll be redirected to Railway dashboard

### Step 2: Create New Project
- Click **"Create New Project"** (or "New Project")
- Select **"Deploy from GitHub Repo"**
- Search for: **`Jimmy`**
- Select: **`Dave870-coder/Jimmy`**
- Click **"Deploy Now"**

### Step 3: Add These Environment Variables

Once deployment starts, go to **"Variables"** tab and add these exactly:

```
GOOGLE_API_KEY = AIzaSyBk563VvLColh0pnXFRjfzMbnZkV7Ghb0U
TELEGRAM_BOT_TOKEN = 7895886891:AAFHQFUrgeRdeA_LI5P9y5lAZfKO3Mbd_M8
DATABASE_URL = sqlite:///./data/bot.db
APP_ENV = production
DEBUG = False
SECRET_KEY = your-secret-key-12345
```

**Add each one:**
- Key in left box
- Value in right box
- Press Enter after each
- Railway will auto-update

### Step 4: Wait for Build Complete
- Watch the **"Build"** tab
- Should say "Deployment Successful" ✅
- Watch the **"Logs"** tab
- Should see "BOT READY" message

### Step 5: Get Your URL
- Look for **"Public URL"** or **"Service Domain"**
- Format: `https://your-app.railway.app`
- Copy it!

### Step 6: Test Health Endpoint
- Open browser
- Paste URL + `/health`
- Example: `https://your-app.railway.app/health`
- Should see: `{"status": "healthy"}`

### Step 7: Test Telegram
- Open Telegram
- Find your bot
- Send message
- Bot responds ✅

---

## ⚡ Quick Check Before Deploying

Let me verify everything is ready locally:
