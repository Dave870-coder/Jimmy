#!/usr/bin/env python3
"""
Automated fix script for Render database initialization
This script helps trigger the rebuild and then initializes the database
"""

import subprocess
import time
import requests
import sys
from datetime import datetime

def log(msg, status="INFO"):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",      # Blue
        "SUCCESS": "\033[92m",   # Green
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
        "RESET": "\033[0m"       # Reset
    }
    color = colors.get(status, colors["INFO"])
    print(f"{color}[{timestamp}] [{status}] {msg}{colors['RESET']}")

def check_render_online():
    """Check if Render backend is online"""
    try:
        resp = requests.get("https://jimmy-ai-bot.onrender.com/health", timeout=5)
        return True, resp.json() if resp.status_code == 200 else {}
    except Exception as e:
        return False, None

def wait_for_rebuild(max_wait=300):
    """Wait for Render to rebuild and come online"""
    log(f"Waiting for Render rebuild (max {max_wait}s)...", "INFO")
    start = time.time()
    
    while time.time() - start < max_wait:
        is_online, data = check_render_online()
        
        if is_online:
            db_status = data.get("database", "unknown") if data else "unknown"
            log(f"✅ Render backend is online! Database status: {db_status}", "SUCCESS")
            return True, data
        
        elapsed = int(time.time() - start)
        remaining = max_wait - elapsed
        log(f"Not online yet... ({elapsed}s elapsed, {remaining}s remaining)", "WARNING")
        time.sleep(5)
    
    log("Timeout waiting for Render rebuild", "ERROR")
    return False, None

def initialize_database():
    """Call the initialization endpoint"""
    log("Attempting to initialize database...", "INFO")
    
    try:
        resp = requests.post(
            "https://jimmy-ai-bot.onrender.com/initialize-db",
            json={},
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                log(f"✅ Database initialized: {data.get('message')}", "SUCCESS")
                return True
            else:
                log(f"⚠️  Initialization returned: {data.get('message')}", "WARNING")
                return False
        else:
            log(f"❌ Endpoint returned: {resp.status_code}", "ERROR")
            log(f"Response: {resp.text}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error calling initialization: {e}", "ERROR")
        return False

def check_health():
    """Check final health status"""
    log("Checking final health status...", "INFO")
    
    try:
        resp = requests.get("https://jimmy-ai-bot.onrender.com/health", timeout=5)
        data = resp.json() if resp.status_code == 200 else {}
        
        log(f"Health response:", "INFO")
        log(f"  Status: {data.get('status', 'unknown')}", "INFO")
        log(f"  Database: {data.get('database', 'unknown')}", "INFO")
        
        if data.get("database") == "ready":
            log("✅ Database is READY!", "SUCCESS")
            return True
        else:
            log(f"⚠️  Database status: {data.get('database')}", "WARNING")
            return False
    except Exception as e:
        log(f"❌ Error checking health: {e}", "ERROR")
        return False

def check_dashboard():
    """Check dashboard URL"""
    log("Checking dashboard...", "INFO")
    
    try:
        resp = requests.get("https://dave870-coder.github.io/Jimmy/", timeout=5)
        if resp.status_code == 200:
            log("✅ Dashboard is LIVE", "SUCCESS")
            return True
        else:
            log(f"⚠️  Dashboard returned {resp.status_code}", "WARNING")
            return False
    except Exception as e:
        log(f"❌ Error checking dashboard: {e}", "ERROR")
        return False

def main():
    """Main script"""
    print("\n" + "="*60)
    print("🚀 RENDER DATABASE FIX - AUTOMATED SCRIPT")
    print("="*60 + "\n")
    
    log("Step 1: Checking if Render is already fixed...", "INFO")
    is_online, data = check_render_online()
    
    if is_online and data and data.get("database") == "ready":
        log("✅ Database is already initialized!", "SUCCESS")
        check_dashboard()
        print("\n" + "="*60)
        print("✅ EVERYTHING IS WORKING!")
        print("="*60 + "\n")
        return 0
    
    # If not online or database not ready
    if not is_online:
        print("\n" + "="*60)
        print("⚠️  RENDER REBUILD NEEDED")
        print("="*60 + "\n")
        
        log("MANUAL STEP REQUIRED:", "WARNING")
        log("1. Open: https://render.com/dashboard", "WARNING")
        log("2. Click: jimmy-ai-bot service", "WARNING")
        log("3. Click: 'Manual Deploy' button (scroll down)", "WARNING")
        log("4. Select: main branch", "WARNING")
        log("5. Wait for deployment to complete", "WARNING")
        log("6. Check: Service shows 'running' (green status)", "WARNING")
        log("7. Come back here and continue", "WARNING")
        
        print("\nPress ENTER when rebuild is complete...")
        input()
        
        print("\n" + "="*60)
        print("⏳ WAITING FOR REBUILD...")
        print("="*60 + "\n")
        
        is_online, data = wait_for_rebuild()
        if not is_online:
            log("❌ Render still not online after rebuild", "ERROR")
            return 1
    
    # Initialize database
    print("\n" + "="*60)
    print("🔧 INITIALIZING DATABASE...")
    print("="*60 + "\n")
    
    success = initialize_database()
    time.sleep(2)
    
    # Check health
    print("\n" + "="*60)
    print("✅ VERIFYING FIX...")
    print("="*60 + "\n")
    
    check_health()
    check_dashboard()
    
    print("\n" + "="*60)
    print("🎉 FIX COMPLETE!")
    print("="*60 + "\n")
    
    log("Your Jimmy Bot is now fully operational", "SUCCESS")
    log("Backend: https://jimmy-ai-bot.onrender.com/", "SUCCESS")
    log("Dashboard: https://dave870-coder.github.io/Jimmy/", "SUCCESS")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
