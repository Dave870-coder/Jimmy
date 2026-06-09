#!/usr/bin/env python
"""
Jimmy AI Bot - Quick Startup Verification Script
Tests all components and gets the bot ready for production
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_step(number, text):
    """Print a numbered step."""
    print(f"[{number}] {text}")

def check_env_file():
    """Check if .env file exists with required keys."""
    print_step(1, "Checking .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("  ❌ .env file not found!")
        print("  Create it: cp .env.example .env")
        return False
    
    with open(".env") as f:
        content = f.read()
        
    required_keys = ["GOOGLE_API_KEY", "TELEGRAM_BOT_TOKEN"]
    found_keys = []
    
    for key in required_keys:
        if key in content:
            value = [line.split("=")[1].strip() for line in content.split("\n") if line.startswith(key + "=")][0]
            if value and not value.startswith("test_") and value != "your-*":
                found_keys.append(key)
                print(f"  ✅ {key}: Found (configured)")
            else:
                print(f"  ⚠️  {key}: Placeholder value (not configured for production)")
        else:
            print(f"  ❌ {key}: Missing!")
    
    return len(found_keys) > 0

def check_python_version():
    """Check Python version."""
    print_step(2, "Checking Python version...")
    
    version = sys.version_info
    min_version = (3, 12)
    
    if version >= min_version:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (required: {min_version[0]}.{min_version[1]}+)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} is too old!")
        print(f"     Required: Python {min_version[0]}.{min_version[1]}+")
        return False

def check_imports():
    """Check if all required packages are importable."""
    print_step(3, "Checking required packages...")
    
    packages = {
        "fastapi": "FastAPI",
        "sqlalchemy": "SQLAlchemy",
        "telegram": "Telegram Bot",
        "google.generativeai": "Google AI",
        "pydantic": "Pydantic",
        "uvicorn": "Uvicorn",
        "aiosqlite": "aiosqlite",
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name} (missing)")
            all_ok = False
    
    return all_ok

def check_database():
    """Check if database is ready."""
    print_step(4, "Checking database...")
    
    db_path = Path("data/bot.db")
    db_dir = db_path.parent
    
    if not db_dir.exists():
        print(f"  📁 Creating data directory...")
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Database directory ready")
    else:
        print(f"  ✅ Database directory exists")
    
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"  ✅ Database file exists ({size_kb:.1f} KB)")
    else:
        print(f"  ℹ️  Database will auto-create on first run")
    
    return True

def check_main_files():
    """Check if main files exist."""
    print_step(5, "Checking project files...")
    
    files = {
        "src/main.py": "Main FastAPI app",
        "src/config.py": "Configuration",
        "src/ai/orchestrator.py": "AI Orchestrator",
        "src/bot/telegram/handler.py": "Telegram Handler",
        "run_bot.py": "Bot entry point",
        ".env": "Environment config",
    }
    
    all_ok = True
    for filepath, name in files.items():
        if Path(filepath).exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} (missing: {filepath})")
            all_ok = False
    
    return all_ok

def check_api_keys():
    """Check if API keys are configured."""
    print_step(6, "Checking API Keys...")
    
    from pathlib import Path
    import os
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = {
        "GOOGLE_API_KEY": "Google AI",
        "TELEGRAM_BOT_TOKEN": "Telegram",
        "WHATSAPP_ACCESS_TOKEN": "WhatsApp (optional)",
    }
    
    configured = 0
    for key_name, display_name in keys.items():
        value = os.getenv(key_name, "").strip()
        if not value or value.startswith("test_") or "your-" in value or "placeholder" in value.lower():
            print(f"  ⚠️  {display_name}: Not configured (placeholder)")
        else:
            print(f"  ✅ {display_name}: Configured")
            configured += 1
    
    return configured >= 1  # At least Google API key required

def main():
    """Run all checks."""
    print_header("🤖 Jimmy AI Bot - Startup Verification")
    
    checks = [
        check_env_file,
        check_python_version,
        check_imports,
        check_database,
        check_main_files,
        check_api_keys,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    # Summary
    print_header("📊 Summary")
    passed = sum(results)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All systems ready!")
        print("\nTo start the bot:")
        print("  1. Windows: .\\run_bot.py")
        print("  2. Mac/Linux: python run_bot.py")
        print("\nThen open: http://localhost:8000/docs")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Most checks passed, but API keys may need configuration.")
        print("\nNext steps:")
        print("  1. Add API keys to .env file")
        print("  2. Run: python quick_startup_check.py")
        print("  3. Then: python run_bot.py")
        return 1
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
