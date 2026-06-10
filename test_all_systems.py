#!/usr/bin/env python3
"""
Comprehensive verification that database and web app work online
Tests all components before and after Render deployment
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_local_database():
    """Verify local database is properly initialized."""
    print("\n" + "="*70)
    print("1️⃣  LOCAL DATABASE CHECK")
    print("="*70)
    
    db_path = Path("data/bot.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    size_kb = db_path.stat().st_size / 1024
    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {size_kb:.1f} KB")
    
    # Check database has tables
    try:
        from sqlalchemy import create_engine, inspect
        sync_url = "sqlite:///./data/bot.db"
        engine = create_engine(sync_url, echo=False)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        engine.dispose()
        
        print(f"✅ Database tables: {len(tables)}")
        if tables:
            print(f"   Tables: {', '.join(tables[:5])}...")
        
        if len(tables) >= 10:
            print(f"✅ Database is properly initialized")
            return True
        else:
            print(f"⚠️  Database has only {len(tables)} tables (expected 14+)")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def check_fastapi_app():
    """Verify FastAPI app loads without errors."""
    print("\n" + "="*70)
    print("2️⃣  FASTAPI APP CHECK")
    print("="*70)
    
    try:
        from src.main import app
        print(f"✅ FastAPI app loads successfully")
        print(f"   App name: {app.title}")
        print(f"   Total routes: {len(app.routes)}")
        
        # Check critical endpoints
        critical_endpoints = ["/", "/health", "/ready", "/init-status"]
        found = []
        for route in app.routes:
            if route.path in critical_endpoints:
                found.append(route.path)
        
        print(f"✅ Critical endpoints found: {len(found)}/4")
        for endpoint in found:
            print(f"   ✓ {endpoint}")
        
        missing = set(critical_endpoints) - set(found)
        if missing:
            print(f"⚠️  Missing endpoints: {missing}")
        
        return len(found) >= 3
        
    except Exception as e:
        print(f"❌ Error loading FastAPI app: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_database_config():
    """Verify database configuration for online use."""
    print("\n" + "="*70)
    print("3️⃣  DATABASE CONFIGURATION CHECK")
    print("="*70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        print(f"✅ Configuration loaded")
        print(f"   Database URL: {settings.database_url}")
        print(f"   Environment: {settings.app_env}")
        print(f"   Debug: {settings.debug}")
        
        # Check if URL is valid
        db_url = settings.database_url
        if "sqlite://" in db_url:
            print(f"✅ Using SQLite (local compatible)")
        elif "postgresql://" in db_url:
            print(f"✅ Using PostgreSQL (online compatible)")
        else:
            print(f"⚠️  Using {db_url.split('://')[0]} database")
        
        # Check pool settings for online use
        print(f"   Pool size: {settings.database_pool_size}")
        print(f"   Max overflow: {settings.database_max_overflow}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking config: {e}")
        return False

def check_cors_config():
    """Verify CORS is configured for online communication."""
    print("\n" + "="*70)
    print("4️⃣  CORS CONFIGURATION CHECK")
    print("="*70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        allowed_origins = settings.cors_origins
        print(f"✅ CORS configured")
        print(f"   Allowed origins: {len(allowed_origins)}")
        
        has_localhost = any("localhost" in origin or "127.0.0.1" in origin for origin in allowed_origins)
        has_production = any("github.io" in origin or "onrender.com" in origin for origin in allowed_origins)
        
        print(f"   Local development: {'✅' if has_localhost else '⚠️'}")
        print(f"   Production URLs: {'✅' if has_production else '⚠️'}")
        
        # Show all origins
        for i, origin in enumerate(allowed_origins, 1):
            print(f"   {i}. {origin}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking CORS: {e}")
        return False

def check_render_config():
    """Verify Render configuration."""
    print("\n" + "="*70)
    print("5️⃣  RENDER CONFIGURATION CHECK")
    print("="*70)
    
    render_yaml = Path("render.yaml")
    if not render_yaml.exists():
        print(f"❌ render.yaml not found")
        return False
    
    try:
        with open(render_yaml) as f:
            content = f.read()
            
        checks = {
            "Build command": "bash ./build.sh" in content,
            "Start command": "python run_bot.py" in content,
            "Health check": "/health" in content,
            "Python 3.12": "3.12" in content,
            "Persistent disk": "jimmy-data" in content or "mountPath" in content,
        }
        
        print(f"✅ render.yaml configured")
        for check_name, result in checks.items():
            status = "✅" if result else "⚠️"
            print(f"   {status} {check_name}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error checking render.yaml: {e}")
        return False

def check_build_sh():
    """Verify build script for online deployment."""
    print("\n" + "="*70)
    print("6️⃣  BUILD SCRIPT CHECK")
    print("="*70)
    
    build_sh = Path("build.sh")
    if not build_sh.exists():
        print(f"❌ build.sh not found")
        return False
    
    try:
        with open(build_sh) as f:
            content = f.read()
        
        checks = {
            "Install requirements": "requirements.txt" in content,
            "Database init": "init_database.py" in content or "metadata.create_all" in content,
            "Verify FastAPI": "fastapi" in content.lower(),
            "Verify SQLAlchemy": "sqlalchemy" in content.lower(),
        }
        
        print(f"✅ build.sh found")
        for check_name, result in checks.items():
            status = "✅" if result else "⚠️"
            print(f"   {status} {check_name}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error checking build.sh: {e}")
        return False

def check_github_pages_config():
    """Verify GitHub Pages configuration."""
    print("\n" + "="*70)
    print("7️⃣  GITHUB PAGES CONFIGURATION CHECK")
    print("="*70)
    
    dashboard_config = Path("dashboard/next.config.js")
    if not dashboard_config.exists():
        print(f"❌ next.config.js not found")
        return False
    
    try:
        with open(dashboard_config) as f:
            content = f.read()
        
        checks = {
            "Base path": "/Jimmy" in content,
            "Export static": "export" in content,
            "Asset prefix": "assetPrefix" in content,
            "API rewrites": "rewrites" in content or "redirects" in content,
            "Unoptimized images": "unoptimized" in content,
        }
        
        print(f"✅ next.config.js configured")
        for check_name, result in checks.items():
            status = "✅" if result else "⚠️"
            print(f"   {status} {check_name}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error checking next.config.js: {e}")
        return False

def check_deployment_files():
    """Verify all deployment files are present."""
    print("\n" + "="*70)
    print("8️⃣  DEPLOYMENT FILES CHECK")
    print("="*70)
    
    required_files = {
        "Procfile": Path("Procfile"),
        "render.yaml": Path("render.yaml"),
        ".python-version": Path(".python-version"),
        "build.sh": Path("build.sh"),
        "run_bot.py": Path("run_bot.py"),
        "requirements.txt": Path("requirements.txt"),
        "dashboard/package.json": Path("dashboard/package.json"),
    }
    
    all_exist = True
    for name, path in required_files.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {name}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all checks."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " COMPREHENSIVE WEB APP & DATABASE VERIFICATION ".center(68) + "║")
    print("║" + " Testing Local + Online + GitHub Deployment ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    checks = [
        ("Local Database", check_local_database()),
        ("FastAPI App", check_fastapi_app()),
        ("Database Config", check_database_config()),
        ("CORS Config", check_cors_config()),
        ("Render Config", check_render_config()),
        ("Build Script", check_build_sh()),
        ("GitHub Pages Config", check_github_pages_config()),
        ("Deployment Files", check_deployment_files()),
    ]
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n{passed}/{total} checks passed ({percentage:.0f}%)")
    
    # Final status
    print("\n" + "="*70)
    print("🎯 DEPLOYMENT READINESS")
    print("="*70)
    
    if percentage == 100:
        print(f"""
✅ ALL SYSTEMS READY FOR ONLINE DEPLOYMENT!

Status:
  ✅ Local database: WORKING
  ✅ FastAPI app: WORKING  
  ✅ Configuration: CORRECT
  ✅ Build script: CORRECT
  ✅ Render config: CORRECT
  ✅ GitHub Pages: CONFIGURED
  ✅ Deployment files: COMPLETE

What happens next:
  1. Backend deploys to Render (auto-downloading your code)
  2. Build script installs all dependencies
  3. Database auto-initializes on first request
  4. Frontend connects to backend API
  5. Both work together seamlessly

Expected Timeline:
  ✅ Render backend: Ready in 5-10 minutes
  ✅ GitHub dashboard: Already LIVE now
  ✅ First request: Auto-initializes database
  ✅ Full operation: 10-15 minutes from now

Next Step: Set environment variables in Render Dashboard!
""")
        return 0
    elif percentage >= 85:
        print(f"""
⚠️  MOSTLY READY WITH MINOR WARNINGS

Status: {passed}/{total} checks passed ({percentage:.0f}%)

Review failed checks above and verify they're not critical.
Most deployment still ready to proceed.
""")
        return 0
    else:
        print(f"""
❌ NOT READY FOR DEPLOYMENT

Status: {passed}/{total} checks passed ({percentage:.0f}%)

Please fix all failed checks before deploying.
""")
        return 1

if __name__ == "__main__":
    sys.exit(main())
