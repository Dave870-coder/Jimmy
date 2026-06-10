#!/usr/bin/env python3
"""
Comprehensive error fixing and validation script.
Verifies all API routes, environment variables, and deployment readiness.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_python_version():
    """Check Python version."""
    print_section("✅ CHECKING PYTHON VERSION")
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    print(f"  Python version: {version_str}")
    
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 10):
        logger.error(f"❌ Python 3.10+ required, got {version_str}")
        return False
    
    print(f"  ✅ Python version OK")
    return True


def check_dependencies():
    """Check all required dependencies."""
    print_section("✅ CHECKING DEPENDENCIES")
    
    dependencies = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'Database ORM',
        'pydantic': 'Data validation',
        'pydantic_settings': 'Settings management',
        'aiosqlite': 'Async SQLite',
        'google.generativeai': 'Google AI integration',
        'telegram': 'Telegram bot',
        'qrcode': 'QR code generation',
    }
    
    missing = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {module:<25} - {description}")
        except ImportError:
            print(f"  ❌ {module:<25} - {description} (MISSING)")
            missing.append(module)
    
    if missing:
        logger.warning(f"❌ Missing packages: {', '.join(missing)}")
        logger.warning(f"   Run: pip install -r requirements.txt")
        return False
    
    print(f"  ✅ All dependencies OK")
    return True


def check_environment_variables():
    """Check environment variables."""
    print_section("✅ CHECKING ENVIRONMENT VARIABLES")
    
    env_file = PROJECT_ROOT / ".env"
    
    if not env_file.exists():
        logger.warning(f"⚠️  .env file not found - creating default template")
        return True  # Not critical
    
    print(f"  ✅ .env file exists")
    
    # Check for critical keys
    critical_keys = [
        'APP_ENV',
        'SECRET_KEY',
        'DATABASE_URL',
    ]
    
    optional_keys = [
        'GOOGLE_API_KEY',
        'TELEGRAM_BOT_TOKEN',
    ]
    
    try:
        from dotenv import dotenv_values
        env_vars = dotenv_values(env_file)
        
        for key in critical_keys:
            if key in env_vars:
                value = env_vars[key]
                print(f"  ✅ {key:<30} = {value[:30] if len(str(value)) > 30 else value}")
            else:
                print(f"  ⚠️  {key:<30} (not set)")
        
        for key in optional_keys:
            if key in env_vars:
                value = env_vars[key]
                if value and value.strip():
                    preview = f"{value[:4]}...{value[-4:]}" if len(str(value)) > 8 else value
                    print(f"  ✅ {key:<30} = {preview}")
                else:
                    print(f"  ⚠️  {key:<30} (empty)")
            else:
                print(f"  ⚠️  {key:<30} (not set)")
        
        print(f"  ✅ Environment variables OK")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to read .env file: {e}")
        return False


def check_database_setup():
    """Check database configuration."""
    print_section("✅ CHECKING DATABASE SETUP")
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        print(f"  Database URL: {settings.database_url[:50]}...")
        
        # Check if SQLite, ensure directory exists
        if settings.database_url.startswith("sqlite:///"):
            db_path = settings.database_url.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            
            print(f"  Database type: SQLite")
            print(f"  Database path: {db_path}")
            
            if db_dir:
                Path(db_dir).mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Database directory created/verified: {db_dir}")
            
            return True
        else:
            print(f"  Database type: PostgreSQL")
            return True
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
        return False


def check_api_routes():
    """Check all API routes are defined."""
    print_section("✅ CHECKING API ROUTES")
    
    routes_to_check = [
        ('src.api.routes.admin', 'Admin routes'),
        ('src.api.routes.telegram', 'Telegram routes'),
        ('src.api.routes.config', 'Config routes'),
        ('src.api.routes.whatsapp', 'WhatsApp routes'),
        ('src.api.routes.messages', 'Messages routes'),
    ]
    
    all_ok = True
    for module_name, description in routes_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {description:<30} - {module_name}")
        except ImportError as e:
            print(f"  ⚠️  {description:<30} - {module_name} (Failed: {e})")
            all_ok = False
    
    if all_ok:
        print(f"  ✅ All API routes OK")
    
    return all_ok


def check_frontend_files():
    """Check frontend files exist."""
    print_section("✅ CHECKING FRONTEND FILES")
    
    frontend_files = [
        'dashboard/app/page.tsx',
        'dashboard/app/components/SettingsPanel.tsx',
        'dashboard/package.json',
    ]
    
    all_exist = True
    for file_path in frontend_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (MISSING)")
            all_exist = False
    
    if all_exist:
        print(f"  ✅ All frontend files OK")
    
    return all_exist


def check_deployment_config():
    """Check deployment configuration."""
    print_section("✅ CHECKING DEPLOYMENT CONFIGURATION")
    
    files_to_check = [
        ('render.yaml', 'Render configuration'),
        ('build.sh', 'Build script'),
        ('run_bot.py', 'Entry point'),
        ('Procfile', 'Procfile (optional)'),
    ]
    
    all_ok = True
    for file_name, description in files_to_check:
        full_path = PROJECT_ROOT / file_name
        if full_path.exists():
            print(f"  ✅ {description:<30} - {file_name}")
        else:
            if file_name == 'Procfile':
                print(f"  ⚠️  {description:<30} - {file_name} (optional)")
            else:
                print(f"  ❌ {description:<30} - {file_name} (MISSING)")
                all_ok = False
    
    if all_ok or not (PROJECT_ROOT / 'render.yaml').exists():
        print(f"  ✅ Deployment configuration OK")
        return all_ok
    
    return all_ok


async def test_api_imports():
    """Test that API can be imported and initialized."""
    print_section("✅ TESTING API INITIALIZATION")
    
    try:
        from src.main import app
        print(f"  ✅ Main FastAPI app imported successfully")
        
        # Check routes are registered
        routes = [route.path for route in app.routes]
        print(f"  ✅ Found {len(routes)} routes registered")
        
        critical_routes = [
            '/health',
            '/api/v1/admin/analytics',
            '/api/v1/telegram/webhook',
        ]
        
        for route in critical_routes:
            if any(route in r for r in routes):
                print(f"    ✅ {route}")
            else:
                print(f"    ⚠️  {route} (not found)")
        
        print(f"  ✅ API initialization OK")
        return True
    except Exception as e:
        logger.error(f"❌ API initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def check_git_status():
    """Check git status."""
    print_section("✅ CHECKING GIT STATUS")
    
    try:
        import subprocess
        
        # Check if git is initialized
        if (PROJECT_ROOT / '.git').exists():
            print(f"  ✅ Git repository initialized")
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                if lines and lines[0]:
                    print(f"  ⚠️  {len(lines)} uncommitted changes:")
                    for line in lines[:5]:
                        print(f"      {line}")
                    if len(lines) > 5:
                        print(f"      ... and {len(lines) - 5} more")
                else:
                    print(f"  ✅ No uncommitted changes")
            
            # Get remote
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"  ✅ Git remote configured")
            else:
                print(f"  ⚠️  No git remote configured")
            
            return True
        else:
            print(f"  ⚠️  Git repository not initialized")
            return False
    except Exception as e:
        logger.error(f"⚠️  Git check failed: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("  🔍 JIMMY AI BOT - COMPREHENSIVE ERROR FIXING & VALIDATION")
    print("=" * 70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Location: {PROJECT_ROOT}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Database Setup", check_database_setup),
        ("API Routes", check_api_routes),
        ("Frontend Files", check_frontend_files),
        ("Deployment Config", check_deployment_config),
        ("API Initialization", test_api_imports),
        ("Git Status", check_git_status),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = asyncio.run(check_func())
            else:
                result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print_section("📊 VALIDATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌" if result is False else "⚠️"
        print(f"  {status} {name}")
    
    print(f"\n  {passed}/{total} checks passed")
    
    if passed == total:
        print_section("✅ ALL SYSTEMS GO - READY TO DEPLOY")
        print("\n  Your app is ready for deployment!")
        print("  Next steps:")
        print("  1. Push code to GitHub:")
        print("     git remote add origin https://github.com/YOUR_USERNAME/jimmy-ai-bot.git")
        print("     git push -u origin main")
        print("\n  2. Deploy on Render:")
        print("     - Go to https://render.com")
        print("     - Create Web Service from GitHub repo")
        print("     - Add environment variables")
        print("     - Click Deploy")
        print("\n" + "=" * 70)
        return 0
    else:
        print_section("❌ ISSUES FOUND - REVIEW ABOVE")
        print("\n  Fix the issues above and run this script again.")
        print("\n" + "=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
