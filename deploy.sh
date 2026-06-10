#!/bin/bash
# Quick Deploy Script for Jimmy AI Bot
# This script prepares your project for Render + GitHub Pages deployment

set -e

echo "=============================================="
echo "🚀 JIMMY AI BOT - QUICK DEPLOY"
echo "=============================================="

# Step 1: Verify everything is ready
echo ""
echo "Step 1: Verifying deployment readiness..."
python3 verify_deployment.py
if [ $? -ne 0 ]; then
    echo "❌ Verification failed. Please fix issues above."
    exit 1
fi

# Step 2: Show status
echo ""
echo "Step 2: Git status..."
git status --short

# Step 3: Commit changes
echo ""
echo "Do you want to commit and deploy? (yes/no)"
read -r proceed

if [ "$proceed" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "Enter commit message (or press Enter for default):"
read -r commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="🚀 Deploy: Seamless Render + GitHub Pages deployment"
fi

git add .
git commit -m "$commit_msg" || echo "No changes to commit"

# Step 4: Push to GitHub
echo ""
echo "Step 4: Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment triggered!"
echo ""
echo "🎯 What's happening now:"
echo "1. Backend (Render):"
echo "   - Service rebuilding with latest code"
echo "   - Database initializing"
echo "   - Available at: https://jimmy-ai-bot.onrender.com"
echo ""
echo "2. Frontend (GitHub Pages):"
echo "   - Dashboard building and deploying"
echo "   - Available at: https://YOUR_USERNAME.github.io/Jimmy"
echo ""
echo "📝 Required Render Environment Variables:"
echo "   □ GOOGLE_API_KEY"
echo "   □ TELEGRAM_BOT_TOKEN"
echo "   □ SECRET_KEY"
echo "   Set these in: https://dashboard.render.com"
echo ""
echo "✅ Verify deployment:"
echo "   Backend:  curl https://jimmy-ai-bot.onrender.com/health"
echo "   Frontend: https://YOUR_USERNAME.github.io/Jimmy"
echo ""
echo "📚 Full guide: DEPLOYMENT_SEAMLESS.md"
