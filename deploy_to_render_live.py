#!/usr/bin/env python3
"""
One-Click Deployment Script for Jimmy AI Bot Platform
Handles GitHub commit/push and generates Render deployment instructions
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description=""):
    """Run a shell command and return success status."""
    if description:
        print(f"\n📦 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            print(f"❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_git_installed():
    """Check if git is installed."""
    return run_command("git --version", "Checking git installation") or False

def check_git_config():
    """Check git configuration."""
    user_name = subprocess.run("git config user.name", shell=True, capture_output=True, text=True).stdout.strip()
    user_email = subprocess.run("git config user.email", shell=True, capture_output=True, text=True).stdout.strip()
    
    if not user_name or not user_email:
        print("\n⚠️ Git not configured. Setting up git...")
        
        user_name = input("Enter your GitHub username: ").strip()
        user_email = input("Enter your GitHub email: ").strip()
        
        subprocess.run(f"git config --global user.name \"{user_name}\"", shell=True)
        subprocess.run(f"git config --global user.email \"{user_email}\"", shell=True)
        print(f"✅ Git configured for {user_name}")
    else:
        print(f"\n✅ Git configured as: {user_name} <{user_email}>")

def check_github_url():
    """Get GitHub repository URL from user."""
    print("\n" + "="*70)
    print("🔗 GITHUB REPOSITORY SETUP")
    print("="*70)
    
    # Check if remote already exists
    existing = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True).stdout.strip()
    
    if existing and "github.com" in existing:
        print(f"\n✅ GitHub remote already configured: {existing}")
        update = input("Do you want to use this URL? (y/n): ").strip().lower()
        if update == 'y':
            return existing
    
    print("\n📝 Enter your GitHub repository HTTPS URL")
    print("   Example: https://github.com/YOUR_USERNAME/jimmy-ai-bot.git")
    github_url = input("GitHub URL: ").strip()
    
    if not github_url.startswith("https://github.com"):
        print("❌ Invalid GitHub URL")
        return None
    
    return github_url

def setup_git_repo(github_url):
    """Set up git repository with GitHub remote."""
    print(f"\n📦 Setting up git repository...")
    
    # Initialize git if needed
    if not os.path.exists(".git"):
        run_command("git init", "Initializing git repository")
    
    # Check if main branch exists
    current_branch = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, capture_output=True, text=True).stdout.strip()
    
    if current_branch != "main" and current_branch != "HEAD":
        run_command("git branch -M main", "Renaming branch to main")
    
    # Set up remote
    existing_remote = subprocess.run("git remote get-url origin 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
    
    if existing_remote:
        if existing_remote != github_url:
            run_command("git remote remove origin", "Removing old remote")
            run_command(f'git remote add origin "{github_url}"', "Adding GitHub remote")
    else:
        run_command(f'git remote add origin "{github_url}"', "Adding GitHub remote")
    
    return True

def commit_and_push():
    """Stage changes, commit, and push to GitHub."""
    print(f"\n" + "="*70)
    print("📤 PREPARING TO PUSH TO GITHUB")
    print("="*70)
    
    # Check for changes
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    
    if not status:
        print("\n✅ No changes to commit")
        return True
    
    print(f"\n📝 Changes detected:")
    print(status)
    
    # Stage all changes
    run_command("git add .", "Staging all changes")
    
    # Get commit message
    print("\n📝 Enter a commit message (describe your changes):")
    commit_msg = input("Commit message (default: 'Update Jimmy AI Bot Platform'): ").strip()
    
    if not commit_msg:
        commit_msg = "Update Jimmy AI Bot Platform - Real-Time Deployment"
    
    # Commit
    if not run_command(f'git commit -m "{commit_msg}"', f'Committing with message: "{commit_msg}"'):
        print("❌ Git commit failed")
        return False
    
    # Push to GitHub
    print("\n📤 Pushing to GitHub (you may be asked for credentials)...")
    if run_command("git push -u origin main", "Pushing to GitHub"):
        print("\n✅ Successfully pushed to GitHub!")
        return True
    else:
        print("\n❌ Push to GitHub failed")
        print("Common issues:")
        print("  - GitHub credentials not set up")
        print("  - Repository doesn't exist on GitHub")
        print("  - SSH key not configured")
        return False

def generate_render_instructions(github_url):
    """Generate Render deployment instructions."""
    repo_name = github_url.split('/')[-1].replace('.git', '')
    
    instructions = f"""
╔════════════════════════════════════════════════════════════════════╗
║         ✅ READY FOR RENDER DEPLOYMENT                            ║
╚════════════════════════════════════════════════════════════════════╝

Your code has been pushed to GitHub!
Repository: {github_url}

Now deploy to Render in 5 simple steps:

┌────────────────────────────────────────────────────────────────────┐
│ STEP 1: Get Your API Keys                                         │
└────────────────────────────────────────────────────────────────────┘

1. Google AI Studio API Key (FREE - Required for AI responses)
   → Go to: https://makersuite.google.com/app/apikey
   → Click "Get API key"
   → Copy your key and save it somewhere safe
   
2. (Optional) Telegram Bot Token
   → Open Telegram and find @BotFather
   → Send /newbot and follow prompts
   → Copy the token provided

┌────────────────────────────────────────────────────────────────────┐
│ STEP 2: Create Render Account                                     │
└────────────────────────────────────────────────────────────────────┘

1. Go to: https://render.com
2. Sign up (free account)
3. Authorize GitHub when prompted

┌────────────────────────────────────────────────────────────────────┐
│ STEP 3: Deploy Your App                                           │
└────────────────────────────────────────────────────────────────────┘

1. Go to: https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Select "Connect a repository"
4. Choose: {repo_name}
5. Keep default settings (render.yaml is pre-configured)
6. Click "Create Web Service"

┌────────────────────────────────────────────────────────────────────┐
│ STEP 4: Add Environment Variables (CRITICAL!)                     │
└────────────────────────────────────────────────────────────────────┘

In Render dashboard, go to Environment tab and add:

  Key: GOOGLE_API_KEY
  Value: [Paste your Google AI key from Step 1]
  
  Key: SECRET_KEY
  Value: [Generate a random 32-char string - example below]
  
  Key: PUBLIC_BASE_URL
  Value: https://your-service-name.onrender.com
  (Replace 'your-service-name' with actual Render service name)
  
  (Optional) Key: TELEGRAM_BOT_TOKEN
  Value: [Your Telegram token from Step 1]

Generate a random SECRET_KEY:
  Windows: powershell -c "[convert]::ToBase64String((1..32|%{{[byte](Get-Random -Max 256))}})|" -replace '=',''
  Mac/Linux: openssl rand -base64 32

┌────────────────────────────────────────────────────────────────────┐
│ STEP 5: Monitor Your Live App                                     │
└────────────────────────────────────────────────────────────────────┘

After deployment completes (2-5 minutes):

1. Dashboard: https://your-service-name.onrender.com
2. Health Check: https://your-service-name.onrender.com/health
3. Settings: https://your-service-name.onrender.com/settings
   → Configure Google API Key here
4. Logs: In Render dashboard under Logs tab

┌────────────────────────────────────────────────────────────────────┐
│ Optional: Connect Telegram Webhook                                 │
└────────────────────────────────────────────────────────────────────┘

If you created a Telegram bot:

1. Open Telegram, find @BotFather
2. Send /mybots → select your bot
3. Click "Edit Bot" → "Edit Webhook"
4. Enter: https://your-service-name.onrender.com/api/v1/telegram/webhook
5. Done! Your bot is now live!

Test it:
- Find your bot on Telegram
- Send /start
- Ask a question
- It responds using Google AI within 2-5 seconds!

═══════════════════════════════════════════════════════════════════════

🎉 You're ready to deploy! Visit https://dashboard.render.com now!

For more details, see: DEPLOY_REALTIME_LIVE.md
"""
    
    return instructions

def main():
    """Main deployment orchestration."""
    print("\n" + "="*70)
    print("🚀 JIMMY AI BOT PLATFORM - ONE-CLICK DEPLOYMENT")
    print("="*70)
    print(f"\n📍 Working directory: {os.getcwd()}")
    print(f"⏰ Deployment started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print("\n" + "="*70)
    print("✅ CHECKING PREREQUISITES")
    print("="*70)
    
    if not check_git_installed():
        print("\n❌ Git is not installed!")
        print("Download from: https://git-scm.com/download/win")
        sys.exit(1)
    
    check_git_config()
    
    # Get GitHub URL
    github_url = check_github_url()
    if not github_url:
        sys.exit(1)
    
    # Setup git repository
    if not setup_git_repo(github_url):
        sys.exit(1)
    
    # Commit and push
    if not commit_and_push():
        print("\n⚠️ Could not push to GitHub automatically")
        print("Please resolve the git issue and try again")
        sys.exit(1)
    
    # Generate Render instructions
    instructions = generate_render_instructions(github_url)
    print(instructions)
    
    # Save instructions to file
    with open("RENDER_DEPLOYMENT_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    print("\n" + "="*70)
    print("✅ DEPLOYMENT PREPARATION COMPLETE!")
    print("="*70)
    print("\n📄 Instructions saved to: RENDER_DEPLOYMENT_INSTRUCTIONS.txt")
    print(f"🌐 Repository: {github_url}")
    print("\nNext: Go to https://dashboard.render.com and deploy!")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
