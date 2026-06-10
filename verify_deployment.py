#!/usr/bin/env python3
"""
Verify that all systems are ready for Render deployment.
Run this before pushing to GitHub.
"""

import os
import sys
import subprocess
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check(name, condition, details=""):
    """Print check result."""
    status = f"{GREEN}✅{RESET}" if condition else f"{RED}❌{RESET}"
    msg = f"{status} {name}"
    if details and not condition:
        msg += f" - {details}"
    print(msg)
    return condition

def print_header(title):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def main():
    """Run all checks."""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print_header("🚀 RENDER DEPLOYMENT VERIFICATION")
    
    results = []
    
    # 1. Configuration Files
    print_header("1️⃣  Configuration Files")
    results.append(check("render.yaml exists", Path("render.yaml").exists()))
    results.append(check("Procfile exists", Path("Procfile").exists()))
    results.append(check("build.sh exists", Path("build.sh").exists()))
    results.append(check("run_bot.py exists", Path("run_bot.py").exists()))
    results.append(check(".python-version exists", Path(".python-version").exists()))
    results.append(check("requirements.txt exists", Path("requirements.txt").exists()))
    
    # 2. Python Version
    print_header("2️⃣  Python Version")
    py_version = sys.version.split()[0]
    is_3_12 = py_version.startswith('3.12')
    print(f"   Current: {BLUE}{py_version}{RESET}")
    results.append(check("Python 3.12+", is_3_12 or sys.version_info >= (3, 12)))
    
    # 3. Dependencies
    print_header("3️⃣  Core Dependencies")
    
    deps = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "sqlalchemy": "SQLAlchemy",
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            results.append(check(name, True))
        except ImportError as e:
            results.append(check(name, False, str(e)[:50]))
    
    # 4. Database Setup
    print_header("4️⃣  Database Setup")
    
    try:
        from src.config import get_settings
        settings = get_settings()
        db_url = settings.database_url
        results.append(check("Settings loaded", True))
        print(f"   Database URL: {BLUE}{db_url[:50]}...{RESET}")
        
        # Check if data directory exists and is writable
        if "sqlite://" in db_url:
            db_path = db_url.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir:
                dir_exists = os.path.isdir(db_dir)
                results.append(check(f"Database directory exists", dir_exists, db_dir))
                if dir_exists:
                    is_writable = os.access(db_dir, os.W_OK)
                    results.append(check("Database directory writable", is_writable))
            else:
                results.append(check("Database directory", True, "Current directory"))
    except Exception as e:
        results.append(check("Settings loaded", False, str(e)[:50]))
    
    # 5. FastAPI App
    print_header("5️⃣  FastAPI Application")
    
    try:
        from src.main import app
        results.append(check("FastAPI app created", True))
        print(f"   App name: {BLUE}{app.title}{RESET}")
        print(f"   Routes: {BLUE}{len(app.routes)}{RESET}")
        
        # Check for health endpoint
        has_health = any(route.path == "/health" for route in app.routes)
        results.append(check("Health endpoint exists", has_health))
    except Exception as e:
        results.append(check("FastAPI app created", False, str(e)[:50]))
    
    # 6. File Integrity
    print_header("6️⃣  File Integrity")
    
    # Check render.yaml has correct startCommand
    try:
        with open("render.yaml") as f:
            content = f.read()
            has_python_start = "python run_bot.py" in content
            results.append(check("render.yaml uses python run_bot.py", has_python_start))
    except Exception as e:
        results.append(check("render.yaml readable", False, str(e)[:50]))
    
    # Check Procfile
    try:
        with open("Procfile") as f:
            content = f.read()
            has_python_start = "python run_bot.py" in content
            results.append(check("Procfile uses python run_bot.py", has_python_start))
    except Exception as e:
        results.append(check("Procfile readable", False, str(e)[:50]))
    
    # Check build.sh is executable
    try:
        build_sh = Path("build.sh")
        is_exec = os.access(build_sh, os.X_OK)
        print(f"   build.sh permissions: {oct(build_sh.stat().st_mode)}")
        results.append(check("build.sh is executable", is_exec))
    except Exception as e:
        results.append(check("build.sh readable", False, str(e)[:50]))
    
    # 7. GitHub Configuration
    print_header("7️⃣  GitHub Configuration")
    
    git_exists = Path(".git").exists()
    results.append(check("Git repository initialized", git_exists))
    
    if git_exists:
        try:
            git_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True
            ).strip()
            is_main = git_branch == "main"
            results.append(check(f"On main branch", is_main, f"Current: {git_branch}"))
            print(f"   Current branch: {BLUE}{git_branch}{RESET}")
        except Exception as e:
            results.append(check("Git branch check", False, str(e)[:30]))
    
    # Check GitHub workflows
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        print(f"   Workflows found: {BLUE}{len(workflows)}{RESET}")
        results.append(check("GitHub workflows exist", len(workflows) > 0))
    
    # 8. Dashboard
    print_header("8️⃣  Dashboard Configuration")
    
    dashboard_exists = Path("dashboard").exists()
    results.append(check("Dashboard directory exists", dashboard_exists))
    
    if dashboard_exists:
        pkg_json = Path("dashboard/package.json").exists()
        results.append(check("dashboard/package.json exists", pkg_json))
        
        next_config = Path("dashboard/next.config.js").exists()
        results.append(check("dashboard/next.config.js exists", next_config))
        
        # Check if next.config.js has proper basePath
        try:
            with open("dashboard/next.config.js") as f:
                content = f.read()
                has_base_path = "/Jimmy" in content
                results.append(check("next.config.js has /Jimmy basePath", has_base_path))
        except Exception as e:
            results.append(check("next.config.js readable", False, str(e)[:50]))
    
    # Summary
    print_header("📊 SUMMARY")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Status: {BLUE}{passed}/{total} checks passed ({percentage:.0f}%){RESET}")
    
    if percentage == 100:
        print(f"\n{GREEN}✅ READY FOR DEPLOYMENT!{RESET}")
        print("Next steps:")
        print("  1. git add .")
        print("  2. git commit -m 'Ready for Render deployment'")
        print("  3. git push origin main")
        print("  4. Monitor at: https://dashboard.render.com")
        return 0
    elif percentage >= 80:
        print(f"\n{YELLOW}⚠️  MOSTLY READY (some warnings){RESET}")
        print("Review failed checks above and fix before deploying.")
        return 1
    else:
        print(f"\n{RED}❌ NOT READY FOR DEPLOYMENT{RESET}")
        print("Fix all failed checks before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
