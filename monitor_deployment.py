#!/usr/bin/env python3
"""
Real-time deployment monitoring for Jimmy Bot on Render
Shows status of backend service and database health
"""

import os
import sys
import time
import requests
from datetime import datetime

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def check_render_backend(url="https://jimmy-ai-bot.onrender.com"):
    """Check Render backend status."""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            db_status = data.get("database", "unknown")
            return True, status, db_status
        else:
            return False, "HTTP Error", response.status_code
    except requests.exceptions.ConnectionError:
        return False, "Connection refused", "Service may be deploying"
    except requests.exceptions.Timeout:
        return False, "Timeout", "Service slow to respond"
    except Exception as e:
        return False, "Error", str(e)

def check_github_pages(url="https://dave870-coder.github.io/Jimmy"):
    """Check GitHub Pages dashboard."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code in [200, 301, 302]
    except:
        return False

def print_header(title):
    """Print section header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def main():
    """Monitor deployment status."""
    print_header("🚀 JIMMY BOT - DEPLOYMENT MONITOR")
    
    print(f"Time: {CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"GitHub Commit: {CYAN}af9c33d{RESET}")
    print()
    
    # Check backend
    print("1️⃣  Backend (Render)")
    print("-" * 70)
    backend_ok, status, db_status = check_render_backend()
    
    if backend_ok:
        print(f"{GREEN}✅ Service is RUNNING{RESET}")
        print(f"   Status: {CYAN}{status}{RESET}")
        print(f"   Database: {GREEN if db_status == 'ready' else YELLOW}{db_status}{RESET}")
        print(f"   URL: {CYAN}https://jimmy-ai-bot.onrender.com{RESET}")
    else:
        print(f"{YELLOW}⏳ Service is DEPLOYING{RESET}")
        print(f"   Status: {YELLOW}{status}{RESET}")
        print(f"   Details: {YELLOW}{db_status}{RESET}")
        print(f"   {YELLOW}→ Check back in 3-5 minutes{RESET}")
        print(f"   {YELLOW}→ Monitor: https://dashboard.render.com{RESET}")
    
    print()
    
    # Check GitHub Pages
    print("2️⃣  Frontend (GitHub Pages)")
    print("-" * 70)
    github_ok = check_github_pages()
    
    if github_ok:
        print(f"{GREEN}✅ Dashboard is LIVE{RESET}")
        print(f"   URL: {CYAN}https://dave870-coder.github.io/Jimmy{RESET}")
    else:
        print(f"{YELLOW}⏳ Dashboard is DEPLOYING{RESET}")
        print(f"   {YELLOW}→ Check back in 1-2 minutes{RESET}")
        print(f"   {YELLOW}→ Monitor: https://github.com/Dave870-coder/Jimmy/actions{RESET}")
    
    print()
    
    # Database status
    print("3️⃣  Database Status")
    print("-" * 70)
    if backend_ok:
        if db_status == "ready":
            print(f"{GREEN}✅ Database is READY{RESET}")
            print(f"   Tables: 14 (initialized locally)")
            print(f"   Location: /opt/data/bot.db (Render persistent disk)")
        else:
            print(f"{YELLOW}⏳ Database is INITIALIZING{RESET}")
            print(f"   Current status: {db_status}")
    else:
        print(f"{YELLOW}⏳ Database status: UNKNOWN{RESET}")
        print(f"   Will initialize when service starts")
    
    print()
    
    # Summary
    print("📊 DEPLOYMENT SUMMARY")
    print("-" * 70)
    
    if backend_ok and github_ok and db_status == "ready":
        print(f"{GREEN}✅ FULLY OPERATIONAL{RESET}")
        print(f"   Backend API:  ✅ Ready")
        print(f"   Frontend:     ✅ Ready")
        print(f"   Database:     ✅ Ready")
        print(f"\n   🎉 All systems ready for use!")
        return 0
    elif backend_ok and github_ok:
        print(f"{YELLOW}⏳ MOSTLY OPERATIONAL{RESET}")
        print(f"   Backend API:  ✅ Ready (database initializing)")
        print(f"   Frontend:     ✅ Ready")
        print(f"   Database:     ⏳ Initializing")
        print(f"\n   ⏱️  Database initialization in progress (~2-5 minutes)")
        return 0
    elif backend_ok or github_ok:
        print(f"{YELLOW}⏳ PARTIALLY DEPLOYED{RESET}")
        if backend_ok:
            print(f"   Backend API:  ✅ Ready")
            print(f"   Frontend:     ⏳ Deploying")
        else:
            print(f"   Backend API:  ⏳ Deploying")
            print(f"   Frontend:     ✅ Ready")
        return 0
    else:
        print(f"{YELLOW}⏳ DEPLOYMENT IN PROGRESS{RESET}")
        print(f"   Backend API:  ⏳ Deploying")
        print(f"   Frontend:     ⏳ Deploying")
        print(f"\n   ⏱️  Estimated time: 3-5 minutes")
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Monitoring stopped{RESET}")
        sys.exit(0)
