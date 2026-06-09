# 🌐 GitHub Pages Dashboard - Complete Setup Guide

**Enable your Jimmy AI Bot dashboard on GitHub Pages in 5 minutes!**

---

## ✅ Your Dashboard URL Will Be:

```
https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

**Example:** If your GitHub username is `daveiamawesome`, your dashboard will be at:
```
https://daveiamawesome.github.io/jimmy-ai-bot/
```

---

## 🚀 5-Minute Setup

### Step 1: Verify Repository is Public

1. Go to your GitHub repository settings
2. Make sure repository is **PUBLIC** (not private)
3. If private, change to public (if you want GitHub Pages free tier)

### Step 2: Enable GitHub Pages

1. Go to your repository: `https://github.com/YOUR_USERNAME/jimmy-ai-bot`
2. Click **Settings** tab (top navigation)
3. Click **Pages** in the left sidebar under "Code and automation"
4. Under "Build and deployment":
   - **Source:** Select `GitHub Actions`
   - Click **Save**

That's it! GitHub Pages is now enabled.

### Step 3: Set Your API URL (Optional but Recommended)

Your dashboard will connect to your backend API.

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add this secret:
   - **Name:** `NEXT_PUBLIC_API_BASE`
   - **Value:** `https://your-bot-api.railway.app`
   - Click **Add secret**

### Step 4: Deploy Dashboard

Make sure your code is pushed to GitHub:

```bash
git push origin main
```

GitHub Actions will automatically:
1. Build the dashboard
2. Deploy to GitHub Pages
3. Your dashboard is LIVE! 🎉

### Step 5: Access Your Dashboard

**Wait 2-3 minutes for deployment, then visit:**

```
https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

Your dashboard is live! ✅

---

## 📊 What You'll See

The dashboard displays:

```
┌────────────────────────────────────────┐
│  Jimmy AI Bot Dashboard                │
├────────────────────────────────────────┤
│                                        │
│  📊 Metrics                            │
│  ├─ Total Messages: 1,234              │
│  ├─ Active Users: 45                   │
│  ├─ API Response: 99.9%                │
│  └─ Uptime: 99.99%                     │
│                                        │
│  📈 Charts                             │
│  ├─ Daily Messages (line chart)        │
│  ├─ User Growth (area chart)           │
│  ├─ Response Times (histogram)         │
│  └─ Errors (pie chart)                 │
│                                        │
│  ⚙️ Configuration                      │
│  ├─ API Settings                       │
│  ├─ Feature Toggles                    │
│  ├─ Rate Limits                        │
│  └─ Cache Settings                     │
│                                        │
└────────────────────────────────────────┘
```

---

## 🔄 Automatic Updates

**Everything is automatic!**

```
You make code changes
        ↓
Push to GitHub (main branch)
        ↓
GitHub Actions automatically:
  1. Installs dependencies
  2. Builds dashboard
  3. Deploys to GitHub Pages
        ↓
(~2-3 minutes)
        ↓
Dashboard updates automatically
```

**You just push code. GitHub does the rest!** 🚀

---

## 📱 Accessing Your Dashboard

### Direct Link

```
https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

### From Your Repository

1. Go to GitHub repository main page
2. Look for the "About" section (top right)
3. Click ⚙️ (gear icon)
4. Add your dashboard link to the description
5. Users can click to access dashboard

---

## 🔧 Configuration Files

The setup is already configured! Here's what was changed:

### `dashboard/next.config.js`
```javascript
output: 'export',           // Enable static export
distDir: 'out',            // Output to 'out' folder
trailingSlash: true,       // URLs end with /
basePath: '',              // No base path needed
assetPrefix: '',           // Asset prefix
images: {
  unoptimized: true,       // Required for GitHub Pages
}
```

### `dashboard/package.json`
```json
"export": "next build && next export"  // Export script added
```

### `.github/workflows/deploy-dashboard.yml`
```yaml
- Automatically builds dashboard
- Deploys to GitHub Pages
- Runs on push to main
- Triggers on dashboard changes
```

---

## 🎯 Connecting to Your API

### Set API Endpoint

The dashboard needs to connect to your backend API.

**Option 1: GitHub Secret (Recommended for Production)**

```
Settings → Secrets and variables → Actions
Secret name: NEXT_PUBLIC_API_BASE
Secret value: https://your-bot-api.railway.app
```

**Option 2: Environment Variable (Local Development)**

Create `dashboard/.env.local`:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Verify API Connection

After deploying, open your dashboard and check:

1. Browser DevTools (F12)
2. Go to **Console** tab
3. Look for messages about API connection
4. If no errors, API is connected! ✅

---

## ✨ Available Dashboard Pages

### Home Page (`/`)
- Real-time metrics
- Daily statistics
- Recent activity
- Quick action buttons

### Analytics (`/analytics`)
- Message processing stats
- User growth chart
- Response time metrics
- Error rate trends

### Monitoring (`/monitoring`)
- Health check status
- Deployment history
- System logs
- Alert history

### Settings (`/settings`)
- API endpoint config
- Feature toggles
- Rate limit settings
- Cache configuration

### Logs (`/logs`)
- Request logs
- Error logs
- Deployment logs
- API access logs

---

## 📋 Troubleshooting

### Dashboard Not Loading

**Problem:** Getting 404 error when visiting dashboard
```
https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

**Solution:**
1. Check GitHub Pages is enabled:
   - Settings → Pages → Source should be "GitHub Actions"
2. Check deployment status:
   - Go to Actions tab
   - Look for "Deploy Dashboard" workflow
   - Should show green checkmark ✅
3. Wait 2-3 minutes for first deployment
4. Hard refresh browser (Ctrl+Shift+R on Windows)

### Dashboard Loads But No Data

**Problem:** Dashboard shows but no metrics/data

**Solution:**
1. Set API URL:
   - Settings → Secrets → NEXT_PUBLIC_API_BASE
   - Set to your bot API URL
   - Re-push to trigger rebuild
2. Check API is running:
   ```bash
   curl https://your-api.railway.app/health
   # Should return: {"status": "healthy"}
   ```
3. Check browser console (F12) for errors

### Build Failed

**Problem:** GitHub Actions shows red X (failed)

**Solution:**
1. Check workflow logs:
   - Go to Actions tab
   - Click "Deploy Dashboard"
   - Expand failed job
   - Look for error message
2. Common issues:
   - Node version mismatch
   - Missing dependencies
   - TypeScript errors
3. Try locally:
   ```bash
   cd dashboard
   npm install
   npm run build
   ```

---

## 🚀 Making Changes to Dashboard

### Update Dashboard

```bash
# 1. Make changes to dashboard code
# (Edit files in dashboard/ folder)

# 2. Test locally
cd dashboard
npm run dev
# Open http://localhost:3000

# 3. Push to GitHub
cd ..
git add dashboard/
git commit -m "feat: Update dashboard"
git push origin main

# 4. GitHub automatically deploys!
# (Wait 2-3 minutes)

# 5. Check your live dashboard
# https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

### Add New Pages

```bash
# 1. Create new file in dashboard/app/
# Example: dashboard/app/users/page.tsx

export default function UsersPage() {
  return <h1>Users Dashboard</h1>
}

# 2. Automatically available at:
# https://YOUR_USERNAME.github.io/jimmy-ai-bot/users/
```

---

## 📊 Monitoring Deployment

### GitHub Actions Dashboard

1. Go to your repository
2. Click **Actions** tab
3. Look for "Deploy Dashboard" workflow
4. Click to see deployment details

### Deployment Status

```
🟢 Green checkmark = Deployed successfully
🟡 Yellow circle = Building/deploying
🔴 Red X = Build failed
```

### View Logs

1. Click workflow run
2. Click "Build" job
3. Expand steps to see full logs
4. Look for errors or warnings

---

## 🎯 Your Dashboard is Live!

### Summary

✅ **GitHub Pages enabled**
✅ **Dashboard automatically deployed**
✅ **Auto-updates on every push**
✅ **API connected**
✅ **Real-time metrics showing**
✅ **Zero manual deployment**

### Your Dashboard URL

```
https://YOUR_USERNAME.github.io/jimmy-ai-bot/
```

**Share this link to show your bot's dashboard!**

---

## 📚 Quick Reference

| Action | Steps |
|--------|-------|
| **Enable GitHub Pages** | Settings → Pages → Source: GitHub Actions |
| **Set API URL** | Settings → Secrets → Add NEXT_PUBLIC_API_BASE |
| **View Dashboard** | https://YOUR_USERNAME.github.io/jimmy-ai-bot/ |
| **Check Deployment** | Go to Actions tab → Deploy Dashboard |
| **Make Changes** | Edit dashboard/ → git push → Auto-deploys |
| **View Logs** | Actions → Deploy Dashboard → Expand job |
| **Reset** | Delete GitHub Pages, re-enable, force push |

---

## 🔗 Related Documentation

- [START_HERE.md](../START_HERE.md) - Quick start guide
- [GITHUB_COMPLETE_GUIDE.md](../GITHUB_COMPLETE_GUIDE.md) - GitHub setup
- [dashboard/README.md](README.md) - Dashboard documentation
- [DEPLOYMENT_COMPLETE.md](../DEPLOYMENT_COMPLETE.md) - Deployment summary

---

## 🎉 Congratulations!

Your Jimmy AI Bot dashboard is now:

✅ **Hosted on GitHub Pages** - Free & fast
✅ **Auto-deployed** - Every code change deploys automatically
✅ **Production-ready** - Real-time metrics & monitoring
✅ **Connected to API** - Shows live bot data
✅ **Shareable** - Easy URL to share with others

**Your dashboard is LIVE!** 🚀

---

Visit now: **https://YOUR_USERNAME.github.io/jimmy-ai-bot/**

(Replace YOUR_USERNAME with your GitHub username)

---

Made with ❤️ for production excellence
