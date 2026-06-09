# GitHub Secrets Configuration Guide

## Overview

GitHub Secrets are used to:
1. Store sensitive API keys securely
2. Connect the dashboard to your backend
3. Trigger automatic rebuilds when updated

---

## Step 1: Access GitHub Secrets

### Method A: GitHub Web Interface
1. Go to: https://github.com/Dave870-coder/Jimmy/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret below

### Method B: GitHub CLI
```bash
# Install GitHub CLI: https://cli.github.com

# Login to GitHub
gh auth login

# Add secrets:
gh secret set NEXT_PUBLIC_API_BASE --body "https://jimmy-ai-bot.onrender.com"
gh secret set GOOGLE_API_KEY --body "YOUR_KEY"
gh secret set TELEGRAM_BOT_TOKEN --body "YOUR_TOKEN"
```

---

## Step 2: Required Secrets

### 1. NEXT_PUBLIC_API_BASE (CRITICAL)
**Purpose:** Tells dashboard where the backend API is located

**Steps:**
1. Deploy backend to Render (see RENDER_QUICK_DEPLOY.md)
2. Get your Render URL (e.g., `https://jimmy-ai-bot.onrender.com`)
3. Add to GitHub Secrets:
   - Name: `NEXT_PUBLIC_API_BASE`
   - Value: `https://jimmy-ai-bot.onrender.com` (no trailing slash!)

**Triggers:** Dashboard rebuild on change

### 2. GOOGLE_API_KEY (Required for AI)
**Purpose:** Google AI (Gemini) API key for intelligent responses

**How to get:**
1. Go to: https://aistudio.google.com
2. Click "Get API key"
3. Click "Create API key in new project"
4. Copy the key (format: `AIzaSy...`)

**Add to GitHub Secrets:**
- Name: `GOOGLE_API_KEY`
- Value: `AIzaSy...`

**Usage:** Backend only (not in dashboard)

### 3. TELEGRAM_BOT_TOKEN (Required for Telegram)
**Purpose:** Telegram bot authentication token

**How to get:**
1. Open Telegram and search for: `@BotFather`
2. Send: `/newbot`
3. Follow the instructions:
   - Give your bot a name
   - Give your bot a username (must end with "bot")
4. @BotFather will send you a token (format: `123456:ABCDefGHIjklmNOpqrsTUVwxyz`)
5. Copy it

**Add to GitHub Secrets:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: `123456:ABCDefGHIjklmNOpqrsTUVwxyz`

**Usage:** Backend only

### 4. SECRET_KEY (Required for Security)
**Purpose:** Encryption key for sessions and tokens

**How to generate:**
```bash
# Option 1: Using OpenSSL
openssl rand -hex 32

# Option 2: Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 3: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Example output:
# a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
```

**Add to GitHub Secrets:**
- Name: `SECRET_KEY`
- Value: (paste your generated key)

**Usage:** Backend only

---

## Step 3: Optional Secrets

### OPENAI_API_KEY (Optional)
If you want GPT-4 as fallback:
- Get from: https://platform.openai.com/api-keys
- Name: `OPENAI_API_KEY`
- Value: `sk-...`

### WHATSAPP_ACCESS_TOKEN (Optional)
If you use WhatsApp Business API:
- Get from: WhatsApp Business Platform
- Name: `WHATSAPP_ACCESS_TOKEN`
- Value: (your token)

---

## Step 4: Verify Secrets Are Set

### Check GitHub
1. Go to: https://github.com/Dave870-coder/Jimmy/settings/secrets/actions
2. Should see these secrets listed:
   - ✓ NEXT_PUBLIC_API_BASE
   - ✓ GOOGLE_API_KEY
   - ✓ TELEGRAM_BOT_TOKEN
   - ✓ SECRET_KEY

### Check Render
1. Go to: https://render.com/dashboard
2. Select: `jimmy-ai-bot`
3. Go to: Environment
4. Should see these variables:
   - GOOGLE_API_KEY (from GitHub Secrets)
   - TELEGRAM_BOT_TOKEN (from GitHub Secrets)
   - SECRET_KEY (from GitHub Secrets)

---

## Step 5: Trigger Dashboard Rebuild

After setting secrets, rebuild dashboard to apply API connection:

### Option A: GitHub Web
1. Go to: https://github.com/Dave870-coder/Jimmy/actions
2. Click: "Deploy Dashboard to GitHub Pages"
3. Click: "Run workflow"
4. Wait 1-2 minutes

### Option B: GitHub CLI
```bash
gh workflow run deploy-dashboard.yml
```

### Option C: Manual Commit
```bash
# Make a small commit to trigger workflow
git commit --allow-empty -m "chore: trigger dashboard rebuild"
git push
```

---

## Step 6: Verify Connection Works

### Test Dashboard
```bash
# Open in browser:
https://dave870-coder.github.io/Jimmy/

# Check if "API status" shows:
- "Connected" = ✓ Working
- "Error" or "Loading" = Check settings
```

### Test with Python Script
```bash
# Run verification script:
cd /path/to/jimmy
python verify_urls.py

# Should show:
# ✓ GitHub Pages Dashboard: LIVE
# ✓ Render Backend: HEALTHY
# ✓ API Connection: CONNECTED
```

---

## Secret Rotation (Security)

### Every 90 Days:
1. Generate new `SECRET_KEY`
2. Update in GitHub Secrets
3. Rebuild dashboard
4. Restart backend

### If Compromised:
1. Immediately update the compromised key
2. Regenerate in source API service
3. Update GitHub Secret
4. Trigger rebuild

---

## Troubleshooting

### Issue: "API Error" in Dashboard
**Solution:**
1. Check NEXT_PUBLIC_API_BASE in secrets
2. Verify it's the correct Render URL
3. No trailing slash!
4. Trigger rebuild

### Issue: Backend Can't Start
**Solution:**
1. Check GOOGLE_API_KEY is valid
2. Check TELEGRAM_BOT_TOKEN is valid
3. Check SECRET_KEY is set
4. Restart deployment in Render

### Issue: Secrets Not Applied
**Solution:**
1. GitHub Secrets were added/updated
2. Need to rebuild dashboard for it to apply
3. Run workflow in Actions tab

### Issue: Can't See Secrets
**Solution:**
1. You must have admin access to repo
2. Go to: Settings → Secrets → Actions
3. Click "New repository secret"

---

## Security Best Practices

✓ **DO:**
- Use unique keys for production
- Rotate keys every 90 days
- Use strong SECRET_KEY (32+ chars)
- Only share URLs, never keys

✗ **DON'T:**
- Commit keys to Git (always use Secrets)
- Share keys via email
- Use same key for multiple services
- Log keys in console/files
- Commit `.env` files

---

## Complete Setup Checklist

- [ ] Deployed backend to Render
- [ ] Got Render URL: `https://jimmy-ai-bot.onrender.com`
- [ ] Added NEXT_PUBLIC_API_BASE to GitHub Secrets
- [ ] Got Google API Key from AI Studio
- [ ] Added GOOGLE_API_KEY to GitHub Secrets
- [ ] Got Telegram Bot Token from @BotFather
- [ ] Added TELEGRAM_BOT_TOKEN to GitHub Secrets
- [ ] Generated SECRET_KEY with openssl/python
- [ ] Added SECRET_KEY to GitHub Secrets
- [ ] Triggered dashboard rebuild
- [ ] Verified "API Connected" in dashboard
- [ ] Tested backend health endpoint
- [ ] Ran verify_urls.py script
- [ ] Set Telegram webhook

---

## Quick Reference

```bash
# View all secrets (command line):
gh secret list

# Update a secret:
gh secret set SECRET_NAME --body "new_value"

# Delete a secret:
gh secret delete SECRET_NAME
```

---

## Next Steps

1. ✅ **Deploy Backend** → Follow RENDER_QUICK_DEPLOY.md
2. ✅ **Add Secrets** → This document
3. ✅ **Rebuild Dashboard** → GitHub Actions
4. ✅ **Configure Telegram** → Set webhook
5. ✅ **Test Everything** → Run verify_urls.py

---

## Support

- GitHub Docs: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Telegram Docs: https://core.telegram.org/bots/api

