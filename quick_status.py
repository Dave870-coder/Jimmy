#!/usr/bin/env python3
"""
Quick Status Check - Run this to see deployment progress
"""

import os
import sys
import subprocess
from pathlib import Path

def run_cmd(cmd):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except:
        return None

def main():
    print("\n" + "="*70)
    print("🚀 JIMMY BOT - QUICK STATUS CHECK".center(70))
    print("="*70 + "\n")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 1. Git Status
    print("📝 Git Status:")
    last_commit = run_cmd("git log -1 --oneline")
    if last_commit:
        print(f"   Last Commit: {last_commit}")
    
    branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    if branch:
        print(f"   Branch: {branch}")
    
    # 2. Database
    print("\n💾 Database:")
    db_path = Path("data/bot.db")
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"   ✅ File exists: {db_path}")
        print(f"   Size: {size_kb:.1f} KB")
    else:
        print(f"   ❌ File not found: {db_path}")
    
    # 3. Configuration Files
    print("\n⚙️  Configuration Files:")
    configs = ["render.yaml", "Procfile", "build.sh", "run_bot.py"]
    for config in configs:
        exists = "✅" if Path(config).exists() else "❌"
        print(f"   {exists} {config}")
    
    # 4. Deployment Info
    print("\n📊 Deployment URLs:")
    print(f"   🔵 Backend (Render): https://jimmy-ai-bot.onrender.com")
    print(f"   📊 Dashboard: https://dave870-coder.github.io/Jimmy")
    print(f"   🔧 Health: https://jimmy-ai-bot.onrender.com/health")
    
    # 5. Environment Variables
    print("\n🔐 Environment Variables (set in Render):")
    print(f"   GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    print(f"   TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Not set'}")
    print(f"   SECRET_KEY: {'✅ Set' if os.getenv('SECRET_KEY') else '❌ Not set'}")
    
    print("\n" + "="*70)
    print("Next Steps:".ljust(70))
    print("="*70)
    print("""
1. Set environment variables in Render Dashboard:
   → Go to https://dashboard.render.com
   → Select 'jimmy-ai-bot' service
   → Environment tab → Add variables

2. Monitor deployment:
   → Run: python monitor_deployment.py
   → Or check: https://dashboard.render.com

3. Verify when ready:
   → Backend: curl https://jimmy-ai-bot.onrender.com/health
   → Frontend: https://dave870-coder.github.io/Jimmy

4. Full guide:
   → Read: DEPLOYMENT_LIVE.md
""")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
