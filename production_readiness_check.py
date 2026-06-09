#!/usr/bin/env python3
"""
Comprehensive Production Readiness Verification Script
Checks all components of the Jimmy Bot system
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

def check_imports() -> Tuple[bool, List[str]]:
    """Check all critical imports work"""
    issues = []
    success = True
    
    print("\n🔍 Checking imports...")
    
    critical_imports = [
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "uvicorn",
        "google.generativeai",
        "telegram",
    ]
    
    for module_name in critical_imports:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
            issues.append(f"Missing: {module_name}")
            success = False
    
    return success, issues

def check_file_structure() -> Tuple[bool, List[str]]:
    """Check critical files exist"""
    issues = []
    success = True
    
    print("\n📁 Checking file structure...")
    
    required_files = [
        "src/main.py",
        "src/db_init.py",
        "init_database.py",
        "requirements.txt",
        "render.yaml",
        "build.sh",
        "dashboard/next.config.js",
        ".github/workflows/deploy-dashboard.yml",
    ]
    
    base_path = Path(".")
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}: NOT FOUND")
            issues.append(f"Missing file: {file_path}")
            success = False
    
    return success, issues

def check_configuration() -> Tuple[bool, List[str]]:
    """Check critical configuration"""
    issues = []
    success = True
    
    print("\n⚙️  Checking configuration...")
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        print(f"  ✅ Config loaded: {settings.app_env}")
        
        # Check required env variables
        required_vars = {
            "app_env": "APP_ENV",
            "database_url": "DATABASE_URL",
            "api_host": "API_HOST",
            "api_port": "API_PORT",
        }
        
        for attr, var_name in required_vars.items():
            value = getattr(settings, attr, None)
            if value:
                if "password" in var_name.lower() or "key" in var_name.lower():
                    print(f"  ✅ {var_name}: [SET]")
                else:
                    print(f"  ✅ {var_name}: {value}")
            else:
                print(f"  ⚠️  {var_name}: Not set")
                
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        issues.append(f"Config error: {e}")
        success = False
    
    return success, issues

def check_database() -> Tuple[bool, List[str]]:
    """Check database configuration and initialization"""
    issues = []
    success = True
    
    print("\n💾 Checking database...")
    
    try:
        from src.db_init import init_db_safe, check_db_status
        
        # Try to check status without initializing
        status = check_db_status()
        print(f"  ✅ Database status: {status}")
        
        if status == "ready":
            print("  ✅ Database initialized and ready")
        elif status == "not_initialized":
            print("  ⚠️  Database not initialized (will initialize on first request)")
        else:
            print(f"  ⚠️  Database status: {status}")
            
    except Exception as e:
        print(f"  ⚠️  Database check error: {e}")
        issues.append(f"Database error: {e}")
    
    return success, issues

def check_fastapi() -> Tuple[bool, List[str]]:
    """Check FastAPI application loads"""
    issues = []
    success = True
    
    print("\n🚀 Checking FastAPI application...")
    
    try:
        from src.main import app
        
        print(f"  ✅ FastAPI app loaded")
        
        # Check routes
        routes = [route.path for route in app.routes]
        critical_routes = ["/", "/health", "/ready", "/api"]
        
        for route in critical_routes:
            if route in routes or any(route in r for r in routes):
                print(f"  ✅ Route {route} exists")
            else:
                print(f"  ⚠️  Route {route} not found")
                
    except Exception as e:
        print(f"  ❌ FastAPI error: {e}")
        issues.append(f"FastAPI error: {e}")
        success = False
        import traceback
        traceback.print_exc()
    
    return success, issues

def check_models() -> Tuple[bool, List[str]]:
    """Check database models load"""
    issues = []
    success = True
    
    print("\n📊 Checking database models...")
    
    try:
        import src.database.models  # noqa
        from src.database import Base
        
        model_count = len(Base.metadata.tables)
        print(f"  ✅ {model_count} database models loaded")
        
        if model_count > 0:
            print(f"  ✅ Models: {', '.join([t.name for t in Base.metadata.tables.values()][:5])}...")
        else:
            print(f"  ❌ No models found")
            issues.append("No database models loaded")
            success = False
            
    except Exception as e:
        print(f"  ❌ Models error: {e}")
        issues.append(f"Models error: {e}")
        success = False
        import traceback
        traceback.print_exc()
    
    return success, issues

def check_integrations() -> Tuple[bool, List[str]]:
    """Check external integrations are configured"""
    issues = []
    success = True
    
    print("\n🔗 Checking integrations...")
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        integrations = {
            "Google AI": hasattr(settings, 'google_api_key') and settings.google_api_key,
            "Telegram": hasattr(settings, 'telegram_bot_token') and settings.telegram_bot_token,
            "WhatsApp": hasattr(settings, 'whatsapp_token') and settings.whatsapp_token,
        }
        
        for integration, has_token in integrations.items():
            if has_token:
                print(f"  ✅ {integration}: Configured")
            else:
                print(f"  ℹ️  {integration}: Not configured (optional)")
                
    except Exception as e:
        print(f"  ⚠️  Integration check error: {e}")
    
    return success, issues

def check_deployment_files() -> Tuple[bool, List[str]]:
    """Check deployment configuration files"""
    issues = []
    success = True
    
    print("\n📦 Checking deployment files...")
    
    try:
        import yaml
        
        # Check render.yaml
        with open("render.yaml") as f:
            render_config = yaml.safe_load(f)
        
        print("  ✅ render.yaml valid")
        
        # Check GitHub Actions workflow
        workflow_path = Path(".github/workflows/deploy-dashboard.yml")
        if workflow_path.exists():
            with open(workflow_path) as f:
                workflow = yaml.safe_load(f)
            print("  ✅ GitHub Actions workflow valid")
        
    except Exception as e:
        print(f"  ❌ Deployment file error: {e}")
        issues.append(f"Deployment config error: {e}")
        success = False
    
    return success, issues

def check_documentation() -> Tuple[bool, List[str]]:
    """Check documentation files exist"""
    issues = []
    success = True
    
    print("\n📚 Checking documentation...")
    
    doc_files = [
        "PRODUCTION_FIX_APPLIED.md",
        "QUICK_ACTION_GUIDE.md",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
    ]
    
    for doc in doc_files:
        doc_path = Path(doc)
        if doc_path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ℹ️  {doc}: Not found (optional)")
    
    return success, issues

def print_summary(results: Dict[str, Tuple[bool, List[str]]]):
    """Print summary of all checks"""
    print("\n" + "=" * 60)
    print("PRODUCTION READINESS SUMMARY")
    print("=" * 60)
    
    all_issues = []
    total_checks = len(results)
    passed_checks = 0
    
    for check_name, (success, issues) in results.items():
        status = "✅ PASS" if success else "⚠️  WARN"
        print(f"{status}: {check_name}")
        if issues:
            for issue in issues:
                print(f"    • {issue}")
                all_issues.append(issue)
        if success:
            passed_checks += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_checks}/{total_checks} checks passed")
    print("=" * 60)
    
    if all_issues:
        print("\n⚠️  Issues found:")
        for issue in all_issues:
            print(f"  • {issue}")
    else:
        print("\n✅ All checks passed - READY FOR PRODUCTION")
    
    print("\n📋 Next Steps:")
    print("  1. Verify render.yaml is correctly set up")
    print("  2. Deploy to Render: git push origin main")
    print("  3. Check Render logs for database initialization")
    print("  4. Verify /health endpoint returns database: 'ready'")
    print("  5. Test dashboard connection to backend")
    print("\n✨ For detailed instructions, see QUICK_ACTION_GUIDE.md")
    
    return len(all_issues) == 0

def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("🚀 JIMMY BOT - PRODUCTION READINESS CHECK")
    print("=" * 60)
    
    results = {
        "File Structure": check_file_structure(),
        "Imports": check_imports(),
        "Configuration": check_configuration(),
        "Database": check_database(),
        "FastAPI App": check_fastapi(),
        "Models": check_models(),
        "Integrations": check_integrations(),
        "Deployment Files": check_deployment_files(),
        "Documentation": check_documentation(),
    }
    
    all_success = print_summary(results)
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
