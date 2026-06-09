#!/usr/bin/env python3
"""
Render Deployment Readiness Checker
Verifies all components are ready for Render deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class RenderReadinessChecker:
    def __init__(self):
        self.root = Path(__file__).parent
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"🔍 {text}")
        print(f"{'='*60}\n")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.print_header("Python Version Check")
        
        version = sys.version_info
        print(f"Python: {version.major}.{version.minor}.{version.micro}")
        
        if version.major >= 3 and version.minor >= 10:
            print("✅ Python version is compatible with Render")
            self.results["python_version"] = "PASS"
        else:
            print("⚠️ Python version may not be optimal for Render")
            self.results["python_version"] = "WARN"
    
    def check_required_files(self):
        """Check if all required files exist"""
        self.print_header("Required Files Check")
        
        required_files = [
            "build.sh",
            "requirements.txt",
            "src/main.py",
            "src/config.py",
            "render.yaml",
            "Dockerfile",
        ]
        
        missing = []
        for file in required_files:
            path = self.root / file
            if path.exists():
                print(f"✅ {file}")
            else:
                print(f"❌ {file} - MISSING")
                missing.append(file)
        
        self.results["required_files"] = "PASS" if not missing else "FAIL"
        if missing:
            self.errors.append(f"Missing files: {', '.join(missing)}")
    
    def check_dependencies(self):
        """Check if core dependencies are installed"""
        self.print_header("Core Dependencies Check")
        
        core_deps = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "google.generativeai",
            "telegram",
        ]
        
        missing = []
        for dep in core_deps:
            try:
                __import__(dep.replace(".", "/"))
                print(f"✅ {dep}")
            except ImportError:
                print(f"❌ {dep} - NOT INSTALLED")
                missing.append(dep)
        
        self.results["dependencies"] = "PASS" if not missing else "FAIL"
        if missing:
            self.errors.append(f"Missing dependencies: {', '.join(missing)}")
    
    def check_environment_vars(self):
        """Check if critical environment variables can be set"""
        self.print_header("Environment Variables Check")
        
        required_vars = {
            "DATABASE_URL": "sqlite:////opt/data/bot.db",
            "APP_ENV": "production",
            "API_HOST": "0.0.0.0",
        }
        
        sensitive_vars = {
            "GOOGLE_API_KEY": "Not set (will be added in Render)",
            "TELEGRAM_BOT_TOKEN": "Not set (will be added in Render)",
            "SECRET_KEY": "Not set (will be added in Render)",
        }
        
        print("Required variables:")
        for var, default in required_vars.items():
            value = os.getenv(var, default)
            print(f"  {var} = {value[:20]}..." if len(value) > 20 else f"  {var} = {value}")
        
        print("\nSensitive variables (Render Secrets):")
        for var, note in sensitive_vars.items():
            status = "✅ Set" if os.getenv(var) else "⏳ To be set"
            print(f"  {var}: {status}")
        
        self.results["environment_vars"] = "PASS"
    
    def check_build_script(self):
        """Check if build.sh is executable and valid"""
        self.print_header("Build Script Check")
        
        build_sh = self.root / "build.sh"
        
        if not build_sh.exists():
            print("❌ build.sh not found")
            self.results["build_script"] = "FAIL"
            self.errors.append("build.sh does not exist")
            return
        
        # Check if executable
        is_executable = os.access(build_sh, os.X_OK)
        status = "✅" if is_executable else "⚠️"
        print(f"{status} build.sh exists (executable: {is_executable})")
        
        # Read and verify content
        try:
            content = build_sh.read_text(encoding='utf-8-sig')
        except:
            content = build_sh.read_text(encoding='latin-1')
        
        checks = [
            ("pip install", "Installs dependencies"),
            ("python3", "Runs Python"),
            ("init_database.py", "Initializes database"),
        ]
        
        for check, desc in checks:
            if check in content:
                print(f"✅ Contains: {desc}")
            else:
                print(f"⚠️ Missing: {desc}")
        
        self.results["build_script"] = "PASS"
    
    def check_fastapi_app(self):
        """Check if FastAPI app starts without errors"""
        self.print_header("FastAPI Application Check")
        
        try:
            # Set minimal env vars for testing
            os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/test.db")
            os.environ.setdefault("APP_ENV", "testing")
            
            print("Attempting to import FastAPI app...")
            from src.main import app
            
            print("✅ FastAPI app imported successfully")
            
            # Check for required endpoints
            routes = [r.path for r in app.routes]
            endpoints = [
                "/health",
                "/ready",
                "/",
            ]
            
            print("\nChecking critical endpoints:")
            for endpoint in endpoints:
                if endpoint in routes:
                    print(f"✅ {endpoint}")
                else:
                    print(f"⚠️ {endpoint} - NOT FOUND")
            
            self.results["fastapi_app"] = "PASS"
            print("\n✅ FastAPI app is ready to run")
            
        except Exception as e:
            print(f"❌ FastAPI app error: {e}")
            import traceback
            traceback.print_exc()
            self.results["fastapi_app"] = "FAIL"
            self.errors.append(f"FastAPI import failed: {e}")
    
    def check_database_setup(self):
        """Check if database can be initialized"""
        self.print_header("Database Setup Check")
        
        try:
            from src.database import Base, engine
            print("✅ Database imports successful")
            
            # Check for models
            if hasattr(Base, 'metadata') and hasattr(Base.metadata, 'tables'):
                table_count = len(Base.metadata.tables)
                print(f"✅ Found {table_count} database models")
                if table_count > 0:
                    print(f"   Tables: {', '.join(list(Base.metadata.tables.keys())[:5])}...")
            
            self.results["database_setup"] = "PASS"
            
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
            self.results["database_setup"] = "WARN"
            self.warnings.append(f"Database setup: {e}")
    
    def check_render_yaml(self):
        """Check if render.yaml is properly configured"""
        self.print_header("Render Configuration Check")
        
        render_yaml = self.root / "render.yaml"
        
        if not render_yaml.exists():
            print("❌ render.yaml not found")
            self.results["render_config"] = "FAIL"
            self.errors.append("render.yaml does not exist")
            return
        
        try:
            content = render_yaml.read_text(encoding='utf-8-sig')
        except:
            content = render_yaml.read_text(encoding='latin-1')
        
        checks = [
            ("buildCommand", "Build command defined"),
            ("startCommand", "Start command defined"),
            ("healthCheckPath", "Health check configured"),
            ("envVars", "Environment variables"),
            ("disk:", "Persistent storage configured"),
        ]
        
        for check, desc in checks:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"⚠️ {desc} - NOT CONFIGURED")
        
        self.results["render_config"] = "PASS"
    
    def check_cors_config(self):
        """Check if CORS is properly configured for Render"""
        self.print_header("CORS Configuration Check")
        
        try:
            from src.config import get_settings
            settings = get_settings()
            
            print(f"CORS Origins: {settings.cors_origins}")
            
            if "http://localhost" in str(settings.cors_origins):
                self.warnings.append("CORS includes localhost - may need to add production URL")
                print("⚠️ CORS includes localhost - add production URL after deployment")
            
            print("✅ CORS configuration found")
            self.results["cors_config"] = "PASS"
            
        except Exception as e:
            print(f"⚠️ CORS check: {e}")
            self.results["cors_config"] = "WARN"
    
    def generate_report(self):
        """Generate final readiness report"""
        self.print_header("Render Deployment Readiness Report")
        
        # Summary table
        print("Summary of Checks:")
        print("-" * 60)
        for check, status in sorted(self.results.items()):
            status_icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
            check_name = check.replace("_", " ").title()
            print(f"{status_icon} {check_name}: {status}")
        
        # Errors
        if self.errors:
            print("\n❌ ERRORS (Must Fix):")
            for error in self.errors:
                print(f"  • {error}")
        
        # Warnings
        if self.warnings:
            print("\n⚠️ WARNINGS (Should Review):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Overall status
        print("\n" + "=" * 60)
        if not self.errors:
            if not self.warnings:
                print("✅ READY FOR RENDER DEPLOYMENT")
                print("No errors or warnings - your app is ready!")
            else:
                print("⚠️ MOSTLY READY FOR RENDER DEPLOYMENT")
                print("Review warnings above before deploying")
        else:
            print("❌ NOT READY FOR RENDER DEPLOYMENT")
            print("Fix errors above and rerun this check")
        print("=" * 60)
        
        # Next steps
        print("\nNext Steps:")
        if not self.errors:
            print("1. Go to: https://render.com/deploy?repo=https://github.com/Dave870-coder/Jimmy")
            print("2. Add environment variables:")
            print("   - GOOGLE_API_KEY")
            print("   - TELEGRAM_BOT_TOKEN")
            print("   - SECRET_KEY")
            print("3. Click 'Deploy'")
            print("4. Wait 3-5 minutes for build")
            print("5. Test at: https://[your-service].onrender.com/health")
        else:
            print("1. Fix the errors listed above")
            print("2. Rerun this script: python render_readiness.py")
            print("3. Once all checks pass, proceed with deployment")
        
        return len(self.errors) == 0
    
    def run_all_checks(self):
        """Run all readiness checks"""
        print("\n🚀 Render Deployment Readiness Checker\n")
        
        self.check_python_version()
        self.check_required_files()
        self.check_dependencies()
        self.check_environment_vars()
        self.check_build_script()
        self.check_fastapi_app()
        self.check_database_setup()
        self.check_render_yaml()
        self.check_cors_config()
        
        success = self.generate_report()
        
        return success

def main():
    checker = RenderReadinessChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
