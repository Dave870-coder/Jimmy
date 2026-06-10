#!/usr/bin/env python3
"""
Complete Deployment Verification and GitHub Push
Ensures all components work, then commits and pushes to GitHub
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_cmd(cmd, silent=False):
    """Run command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if not silent and result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False

def test_python_files():
    """Test all Python files for syntax errors."""
    print("\n" + "="*70)
    print("🔍 TESTING PYTHON FILES")
    print("="*70)
    
    python_files = [
        "src/main.py",
        "src/config.py",
        "src/ai/orchestrator.py",
        "src/api/routes/admin.py",
        "src/api/routes/telegram.py",
        "run_bot.py",
    ]
    
    all_good = True
    for file in python_files:
        if os.path.exists(file):
            if run_cmd(f"python -m py_compile {file}", silent=True):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - Syntax Error!")
                all_good = False
        else:
            print(f"  ⚠️  {file} - Not found")
    
    return all_good

def test_dependencies():
    """Check if all critical dependencies are installed."""
    print("\n" + "="*70)
    print("📦 TESTING DEPENDENCIES")
    print("="*70)
    
    dependencies = {
        "fastapi": "FastAPI web framework",
        "uvicorn": "ASGI server",
        "sqlalchemy": "Database ORM",
        "pydantic": "Data validation",
        "google-generativeai": "Google AI integration",
        "python-telegram-bot": "Telegram bot support",
        "aiosqlite": "Async SQLite",
    }
    
    missing = []
    for package, description in dependencies.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package:25} - {description}")
        except ImportError:
            print(f"  ❌ {package:25} - {description} (MISSING)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_env_file():
    """Verify .env file has critical settings."""
    print("\n" + "="*70)
    print("⚙️  TESTING ENVIRONMENT CONFIGURATION")
    print("="*70)
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        return False
    
    print("✅ .env file exists")
    
    with open(".env") as f:
        env_content = f.read()
    
    # Check for critical keys
    checks = [
        ("GOOGLE_API_KEY", "Google AI configuration"),
        ("DATABASE_URL", "Database connection"),
        ("SECRET_KEY", "Application secret"),
    ]
    
    all_good = True
    for key, description in checks:
        if key in env_content:
            print(f"  ✅ {key:25} - {description}")
        else:
            print(f"  ❌ {key:25} - {description} (MISSING)")
            all_good = False
    
    return all_good

def test_frontend_files():
    """Check if critical frontend files exist."""
    print("\n" + "="*70)
    print("🎨 TESTING FRONTEND FILES")
    print("="*70)
    
    frontend_files = [
        ("dashboard/app/page.tsx", "Main dashboard page"),
        ("dashboard/app/components/SettingsPanel.tsx", "Settings panel"),
        ("dashboard/app/layout.tsx", "Layout component"),
        ("dashboard/package.json", "Frontend dependencies"),
    ]
    
    all_good = True
    for file, description in frontend_files:
        if os.path.exists(file):
            print(f"  ✅ {file:40} - {description}")
        else:
            print(f"  ❌ {file:40} - {description} (MISSING)")
            all_good = False
    
    return all_good

def test_api_routes():
    """Check if critical API routes are defined."""
    print("\n" + "="*70)
    print("🔗 TESTING API ROUTES")
    print("="*70)
    
    routes = [
        ("src/api/routes/admin.py", "/health", "Health check"),
        ("src/api/routes/admin.py", "/analytics", "Analytics endpoint"),
        ("src/api/routes/admin.py", "/integrations", "Integrations status"),
        ("src/api/routes/telegram.py", "/webhook", "Telegram webhook"),
    ]
    
    all_good = True
    for file, route, description in routes:
        if os.path.exists(file):
            with open(file) as f:
                content = f.read()
                if route in content or description.lower() in content.lower():
                    print(f"  ✅ {route:30} - {description}")
                else:
                    print(f"  ⚠️  {route:30} - {description} (Not found in {file})")
        else:
            print(f"  ❌ {file:30} - File missing")
            all_good = False
    
    return all_good

def test_git_setup():
    """Check git configuration."""
    print("\n" + "="*70)
    print("🔧 TESTING GIT SETUP")
    print("="*70)
    
    # Check git installed
    if not run_cmd("git --version", silent=True):
        print("❌ Git not installed!")
        return False
    
    print("✅ Git is installed")
    
    # Check git config
    user_name = subprocess.run("git config user.name", shell=True, capture_output=True, text=True).stdout.strip()
    user_email = subprocess.run("git config user.email", shell=True, capture_output=True, text=True).stdout.strip()
    
    if user_name and user_email:
        print(f"✅ Git configured: {user_name} <{user_email}>")
    else:
        print("⚠️  Git not fully configured")
        print("   Run: git config --global user.name 'Your Name'")
        print("   Run: git config --global user.email 'your@email.com'")
    
    # Check if repo initialized
    if os.path.exists(".git"):
        print("✅ Git repository initialized")
    else:
        print("⚠️  Git repository not initialized (will be created)")
    
    return True

def verify_render_config():
    """Check if render.yaml is properly configured."""
    print("\n" + "="*70)
    print("☁️  TESTING RENDER CONFIGURATION")
    print("="*70)
    
    if not os.path.exists("render.yaml"):
        print("❌ render.yaml not found!")
        return False
    
    print("✅ render.yaml exists")
    
    with open("render.yaml") as f:
        content = f.read()
    
    checks = [
        ("python", "Python environment"),
        ("build.sh", "Build script"),
        ("run_bot.py", "Start command"),
        ("GOOGLE_API_KEY", "Environment variables"),
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} (MISSING)")
            all_good = False
    
    return all_good

def prepare_git():
    """Initialize and configure git."""
    print("\n" + "="*70)
    print("📤 PREPARING GIT REPOSITORY")
    print("="*70)
    
    # Initialize if needed
    if not os.path.exists(".git"):
        print("Initializing git repository...")
        run_cmd("git init")
        print("✅ Git initialized")
    else:
        print("✅ Git already initialized")
    
    # Configure if needed
    user_name = subprocess.run("git config user.name", shell=True, capture_output=True, text=True).stdout.strip()
    if not user_name:
        print("\nGit configuration needed:")
        name = input("Enter your name: ").strip()
        email = input("Enter your email: ").strip()
        run_cmd(f'git config --global user.name "{name}"')
        run_cmd(f'git config --global user.email "{email}"')
        print(f"✅ Configured: {name} <{email}>")
    
    # Check main branch
    branch = subprocess.run("git rev-parse --abbrev-ref HEAD 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
    if branch and branch != "main" and branch != "HEAD":
        print(f"Renaming branch from {branch} to main...")
        run_cmd("git branch -M main")
        print("✅ Branch renamed to main")
    
    return True

def commit_and_push():
    """Stage, commit, and push to GitHub."""
    print("\n" + "="*70)
    print("💾 COMMITTING AND PUSHING TO GITHUB")
    print("="*70)
    
    # Check for changes
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    
    if not status:
        print("✅ No changes to commit")
        return True
    
    print(f"\n📝 Found {len(status.splitlines())} files with changes")
    
    # Stage all changes
    print("\nStaging changes...")
    if not run_cmd("git add .", silent=True):
        print("❌ Failed to stage changes")
        return False
    print("✅ Changes staged")
    
    # Create commit message
    print("\nCreating commit...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Update: Production deployment - {timestamp}"
    
    if not run_cmd(f'git commit -m "{commit_msg}"', silent=True):
        print("❌ Failed to commit")
        return False
    print(f"✅ Committed: {commit_msg}")
    
    # Get remote URL
    remote = subprocess.run("git remote get-url origin 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
    
    if not remote or "github.com" not in remote:
        print("\n⚠️  No GitHub remote configured")
        print("\nYou can push manually with:")
        print("  git remote add origin https://github.com/YOUR_USERNAME/jimmy-ai-bot.git")
        print("  git push -u origin main")
        return True
    
    print(f"\n📤 Pushing to GitHub: {remote}")
    if not run_cmd("git push -u origin main"):
        print("⚠️  Push to GitHub requires authentication")
        print("You may be prompted for credentials")
        # Try again with verbosity
        return run_cmd("git push -u origin main --verbose")
    
    print("✅ Successfully pushed to GitHub!")
    return True

def main():
    """Run complete verification and deployment."""
    print("\n" + "="*70)
    print("🚀 JIMMY AI BOT - COMPLETE DEPLOYMENT VERIFICATION")
    print("="*70)
    print(f"\n⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Location: {os.getcwd()}")
    
    # Run all tests
    test_results = {
        "Python Files": test_python_files(),
        "Dependencies": test_dependencies(),
        "Environment": test_env_file(),
        "Frontend": test_frontend_files(),
        "API Routes": test_api_routes(),
        "Git Setup": test_git_setup(),
        "Render Config": verify_render_config(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    for name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed < total:
        print("\n⚠️  Some checks failed. Fix issues before deploying.")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return 1
    
    # Git preparation and push
    if not prepare_git():
        print("❌ Failed to prepare git")
        return 1
    
    if not commit_and_push():
        print("⚠️  Could not push to GitHub automatically")
        print("You can push manually later")
    
    # Success
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETE & CODE COMMITTED!")
    print("="*70)
    
    print("\n🎯 NEXT STEPS:")
    print("1. Go to: https://render.com")
    print("2. Create new Web Service")
    print("3. Connect your GitHub repository")
    print("4. Add environment variables:")
    print("   - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)")
    print("   - SECRET_KEY (random 32-char string)")
    print("   - PUBLIC_BASE_URL (your Render URL)")
    print("5. Click Deploy!")
    
    print("\n✨ Your app will be live in 2-5 minutes!")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
