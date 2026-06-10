#!/usr/bin/env python3
"""
Deploy to Production with Real-Time Configuration

This script helps deploy Jimmy to Render with proper Telegram and Google AI
configuration for real-time operation.

Usage:
    python deploy_realtime.py
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


class RealTimeDeployment:
    """Handles real-time deployment to production."""
    
    def __init__(self):
        """Initialize deployment helper."""
        self.config = {}
        self.env_file = ".env"
        self.render_config = "render.yaml"
    
    def check_git_setup(self) -> Tuple[bool, str]:
        """Check if Git repository is initialized."""
        logger.info("")
        logger.info("🔍 Checking Git setup...")
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Get current branch
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                branch = branch_result.stdout.strip()
                
                logger.info(f"   ✅ Git initialized, branch: {branch}")
                return True, branch
            else:
                logger.error("❌ Not a Git repository")
                return False, ""
        
        except Exception as e:
            logger.error(f"❌ Git check failed: {e}")
            return False, ""
    
    def check_render_config(self) -> Tuple[bool, str]:
        """Check if Render config exists."""
        logger.info("")
        logger.info("📋 Checking Render configuration...")
        
        if os.path.exists(self.render_config):
            logger.info(f"   ✅ Found {self.render_config}")
            return True, self.render_config
        else:
            logger.warning(f"   ⚠️  {self.render_config} not found")
            return False, ""
    
    def load_env_config(self) -> dict:
        """Load current .env configuration."""
        logger.info("")
        logger.info("📂 Loading configuration...")
        
        config = {}
        
        if os.path.exists(self.env_file):
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                
                logger.info(f"   ✅ Loaded {len(config)} variables from {self.env_file}")
            except Exception as e:
                logger.error(f"   ❌ Error loading .env: {e}")
        
        self.config = config
        return config
    
    def validate_production_config(self) -> Tuple[bool, list]:
        """Validate production configuration."""
        logger.info("")
        logger.info("✔️  Validating production configuration...")
        
        issues = []
        
        # Check Telegram token
        token = self.config.get('TELEGRAM_BOT_TOKEN', '')
        if not token or token.startswith('test_'):
            issues.append("❌ TELEGRAM_BOT_TOKEN: Must be real token (not test_token_123)")
        elif ':' not in token:
            issues.append("❌ TELEGRAM_BOT_TOKEN: Invalid format (should be: 123:ABC...)")
        else:
            logger.info("   ✅ Telegram token configured")
        
        # Check Google AI key
        google_key = self.config.get('GOOGLE_API_KEY', '')
        if not google_key or google_key.startswith('test_'):
            issues.append("❌ GOOGLE_API_KEY: Must be real key (not test_google_key)")
        else:
            logger.info("   ✅ Google AI key configured")
        
        # Check environment
        app_env = self.config.get('APP_ENV', 'development')
        if app_env != 'production':
            issues.append(f"⚠️  APP_ENV: Should be 'production' (currently '{app_env}')")
        else:
            logger.info("   ✅ APP_ENV set to production")
        
        # Check debug mode
        debug = self.config.get('DEBUG', 'True').lower()
        if debug == 'true':
            issues.append("⚠️  DEBUG: Should be False in production")
        else:
            logger.info("   ✅ DEBUG disabled")
        
        # Check webhook URL
        webhook_url = self.config.get('TELEGRAM_WEBHOOK_URL', '')
        if not webhook_url:
            issues.append("⚠️  TELEGRAM_WEBHOOK_URL: Not set (webhook may not work)")
        else:
            logger.info("   ✅ Webhook URL configured")
        
        # Check public URL
        public_url = self.config.get('PUBLIC_BASE_URL', '')
        if not public_url:
            issues.append("⚠️  PUBLIC_BASE_URL: Not set (optional but recommended)")
        else:
            logger.info("   ✅ Public base URL configured")
        
        return len(issues) == 0, issues
    
    def show_deployment_checklist(self) -> bool:
        """Show deployment checklist."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("📋 PRE-DEPLOYMENT CHECKLIST")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Before deploying to Render, verify:")
        logger.info("")
        logger.info("[ ] Real Telegram token from @BotFather")
        logger.info("[ ] Real Google AI key from makersuite.google.com")
        logger.info("[ ] Webhook URL set to Render URL")
        logger.info("[ ] APP_ENV=production")
        logger.info("[ ] DEBUG=False")
        logger.info("[ ] All dependencies in requirements.txt")
        logger.info("[ ] Git repository on main branch")
        logger.info("")
        
        proceed = input("Ready to deploy? (yes/no): ").strip().lower()
        return proceed == 'yes'
    
    def update_git_and_deploy(self) -> bool:
        """Update Git and trigger deployment."""
        logger.info("")
        logger.info("🚀 Deploying to Render...")
        logger.info("-" * 70)
        
        try:
            # Check Git status
            logger.info("📝 Checking Git status...")
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                logger.info("   Changes detected, staging...")
                subprocess.run(["git", "add", "."], check=True, timeout=10)
                
                logger.info("   Committing...")
                subprocess.run(
                    ["git", "commit", "-m", "Enable real-time Telegram integration"],
                    check=True,
                    timeout=10
                )
            
            # Push to main
            logger.info("📤 Pushing to GitHub...")
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Pushed to GitHub successfully")
                logger.info("")
                logger.info("🔄 Render deployment triggered!")
                logger.info("   Monitor at: https://dashboard.render.com")
                logger.info("")
                logger.info("⏱️  Expected deployment time: 2-5 minutes")
                logger.info("")
                logger.info("✅ Once deployed, test your bot on Telegram!")
                return True
            else:
                logger.error(f"❌ Git push failed: {result.stderr}")
                return False
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
    
    async def run_interactive_deployment(self) -> bool:
        """Run interactive deployment wizard."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("🚀 REAL-TIME DEPLOYMENT WIZARD")
        logger.info("=" * 70)
        logger.info("")
        
        # Step 1: Check Git
        git_ok, branch = self.check_git_setup()
        if not git_ok:
            logger.error("❌ Not a Git repository - cannot deploy")
            return False
        
        # Step 2: Check Render config
        self.check_render_config()
        
        # Step 3: Load configuration
        self.load_env_config()
        
        # Step 4: Validate configuration
        config_ok, issues = self.validate_production_config()
        
        if issues:
            logger.warning("")
            logger.warning("⚠️  Configuration issues found:")
            for issue in issues:
                logger.warning(f"   {issue}")
            logger.warning("")
            
            fix = input("Fix issues now? (y/n): ").strip().lower()
            if fix == 'y':
                logger.info("")
                logger.info("Edit .env file with correct values:")
                logger.info("  - TELEGRAM_BOT_TOKEN: from @BotFather")
                logger.info("  - GOOGLE_API_KEY: from makersuite.google.com")
                logger.info("  - APP_ENV: set to 'production'")
                logger.info("  - DEBUG: set to 'False'")
                logger.info("")
                input("Press Enter when done...")
                
                # Reload config
                self.load_env_config()
                config_ok, issues = self.validate_production_config()
                
                if issues:
                    logger.error("❌ Configuration still has issues")
                    return False
            else:
                logger.warning("⚠️  Skipping deployment - configuration incomplete")
                return False
        
        # Step 5: Show checklist
        if not self.show_deployment_checklist():
            logger.info("❌ Deployment cancelled")
            return False
        
        # Step 6: Deploy
        success = self.update_git_and_deploy()
        
        if success:
            logger.info("")
            logger.info("=" * 70)
            logger.info("🎉 DEPLOYMENT IN PROGRESS!")
            logger.info("=" * 70)
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Wait 2-5 minutes for Render to deploy")
            logger.info("2. Check status: https://dashboard.render.com")
            logger.info("3. Test bot on Telegram: @your_bot_username")
            logger.info("4. Send /start → you should get welcome message")
            logger.info("5. Send a message → you should get AI response")
            logger.info("")
            logger.info("📊 Monitor logs: Render Dashboard → Logs")
            logger.info("")
        
        return success


async def main():
    """Main entry point."""
    deployer = RealTimeDeployment()
    
    try:
        success = await deployer.run_interactive_deployment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n❌ Deployment cancelled")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
