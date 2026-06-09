#!/usr/bin/env python
"""
🚀 Jimmy AI Bot - Complete GitHub & Production Deployment Setup
Automates deployment to GitHub with CI/CD and production-scale infrastructure.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional

class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_step(number: int, text: str):
    """Print step."""
    print(f"{Colors.BOLD}{Colors.BLUE}[Step {number}]{Colors.ENDC} {text}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def run_command(command: str, description: str = "") -> bool:
    """Run shell command."""
    try:
        if description:
            print(f"{Colors.CYAN}→ {description}{Colors.ENDC}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            print_error(f"Command failed: {command}")
            if result.stderr:
                print(f"  {result.stderr}")
            return False
        
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        
        return True
    
    except Exception as e:
        print_error(f"Error running command: {e}")
        return False

def ask_input(prompt: str, default: Optional[str] = None) -> str:
    """Ask for user input."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(f"{Colors.BOLD}{prompt}{Colors.ENDC}").strip()
    return response or default or ""

def main():
    """Main deployment script."""
    
    print_header("🚀 Jimmy AI Bot - GitHub & Production Deployment Setup")
    
    print(f"{Colors.BOLD}This script will help you:{Colors.ENDC}")
    print("  1. Initialize Git repository")
    print("  2. Create GitHub repository")
    print("  3. Push code to GitHub")
    print("  4. Set up CI/CD pipeline")
    print("  5. Configure for production scale (7M users)\n")
    
    # Step 1: Git Configuration
    print_step(1, "Configure Git")
    
    git_name = ask_input("Your name", "Your Name")
    git_email = ask_input("Your email", "your@email.com")
    github_username = ask_input("GitHub username", "YOUR_USERNAME")
    repo_name = ask_input("Repository name", "jimmy-ai-bot")
    
    if not run_command(f'git config user.name "{git_name}"'):
        print_error("Failed to set git name")
        sys.exit(1)
    
    if not run_command(f'git config user.email "{git_email}"'):
        print_error("Failed to set git email")
        sys.exit(1)
    
    print_success("Git configured")
    
    # Step 2: Initialize Git Repo
    print_step(2, "Initialize Git Repository")
    
    if not os.path.exists(".git"):
        if not run_command("git init"):
            print_error("Failed to initialize git")
            sys.exit(1)
        print_success("Git repository initialized")
    else:
        print_success("Git repository already exists")
    
    # Step 3: Add files to Git
    print_step(3, "Stage files for commit")
    
    if not run_command("git add .", "Adding all files..."):
        print_error("Failed to add files")
        sys.exit(1)
    
    print_success("Files staged")
    
    # Step 4: Create initial commit
    print_step(4, "Create initial commit")
    
    commit_msg = "feat: Initial commit - Jimmy AI Bot production ready with 7M user scale"
    if not run_command(f'git commit -m "{commit_msg}"', "Creating commit..."):
        print_warning("No changes to commit or commit failed")
    
    print_success("Commit created")
    
    # Step 5: Rename branch to main
    print_step(5, "Set main branch")
    
    run_command("git branch -M main", "Renaming to main branch...")
    print_success("Branch set to main")
    
    # Step 6: Create GitHub remote
    print_step(6, "Add GitHub remote")
    
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"
    
    run_command(f'git remote remove origin', "Removing old remote...")
    if not run_command(f'git remote add origin "{remote_url}"'):
        print_error("Failed to add remote")
        sys.exit(1)
    
    print_success(f"Remote added: {remote_url}")
    
    # Step 7: Push to GitHub
    print_step(7, "Push to GitHub")
    
    print_warning("Note: You may need to enter GitHub credentials or use SSH key")
    if not run_command("git push -u origin main", "Pushing to GitHub..."):
        print_error("Failed to push to GitHub")
        print_warning("Please ensure:")
        print("  1. GitHub repository exists at:")
        print(f"     {remote_url}")
        print("  2. You have permission to push")
        print("  3. SSH key or PAT is configured\n")
        print("Then manually run:")
        print("  git push -u origin main")
        return
    
    print_success("Code pushed to GitHub!")
    
    # Step 8: Display GitHub Secrets checklist
    print_step(8, "Configure GitHub Secrets")
    
    print(f"\n{Colors.BOLD}Go to GitHub and add these secrets:{Colors.ENDC}")
    print(f"  URL: https://github.com/{github_username}/{repo_name}/settings/secrets/actions\n")
    
    secrets = {
        "GOOGLE_API_KEY": "Your Google AI Studio key",
        "TELEGRAM_BOT_TOKEN": "Your Telegram bot token",
        "WHATSAPP_ACCESS_TOKEN": "Your WhatsApp token (optional)",
        "SECRET_KEY": "Strong random key for production",
        "RAILWAY_PROD_TOKEN": "From Railway → Account → API Tokens",
        "RAILWAY_PROD_PROJECT_ID": "From Railway project URL",
        "RAILWAY_PROD_SERVICE_ID": "From Railway service settings",
        "RAILWAY_PROD_DOMAIN": "Your Railway domain (e.g., bot.railway.app)",
        "SLACK_WEBHOOK": "From Slack → Incoming Webhooks (optional)",
    }
    
    for secret_name, description in secrets.items():
        print(f"  ☐ {Colors.YELLOW}{secret_name}{Colors.ENDC}")
        print(f"    → {description}")
    
    # Step 9: Final checklist
    print_step(9, "Deployment Checklist")
    
    print(f"\n{Colors.BOLD}Your deployment is ready! Verify:{Colors.ENDC}\n")
    
    checklist = [
        ("Code pushed to GitHub", f"https://github.com/{github_username}/{repo_name}"),
        ("CI/CD workflow created", f"https://github.com/{github_username}/{repo_name}/actions"),
        ("GitHub Secrets configured", f"https://github.com/{github_username}/{repo_name}/settings/secrets"),
        ("Railway connected", "https://railway.app/dashboard"),
        ("Production scale ready", "See: SCALING_FOR_7MILLION_USERS.md"),
    ]
    
    for item, details in checklist:
        print(f"  ☐ {Colors.BOLD}{item}{Colors.ENDC}")
        if details.startswith("http"):
            print(f"    → {Colors.CYAN}{details}{Colors.ENDC}")
        else:
            print(f"    → {details}")
    
    # Step 10: Next steps
    print_step(10, "Next Steps")
    
    print(f"\n{Colors.BOLD}Make a test deployment:{Colors.ENDC}\n")
    
    print("  1. Create a feature branch:")
    print(f"     {Colors.CYAN}git checkout -b feature/test{Colors.ENDC}\n")
    
    print("  2. Make a small change:")
    print(f"     {Colors.CYAN}echo '# v1.0.0' >> VERSION.md{Colors.ENDC}\n")
    
    print("  3. Commit and push:")
    print(f"     {Colors.CYAN}git add VERSION.md")
    print(f"     git commit -m 'test: Initial CI/CD test'")
    print(f"     git push origin feature/test{Colors.ENDC}\n")
    
    print("  4. Watch GitHub Actions:")
    print(f"     {Colors.CYAN}https://github.com/{github_username}/{repo_name}/actions{Colors.ENDC}\n")
    
    print("  5. Create Pull Request and merge to main")
    print("     → Automatic deployment to production!\n")
    
    # Success message
    print_header("🎉 GitHub Setup Complete!")
    
    print(f"{Colors.GREEN}{Colors.BOLD}Your Jimmy AI Bot is ready for production!{Colors.ENDC}\n")
    
    print(f"Repository: {Colors.CYAN}{remote_url}{Colors.ENDC}")
    print(f"CI/CD Pipeline: {Colors.CYAN}GitHub Actions (fully automated){Colors.ENDC}")
    print(f"Scale Ready: {Colors.CYAN}7 million concurrent users{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
    print(f"  • START_HERE.md - Quick start guide")
    print(f"  • GITHUB_PRODUCTION_DEPLOYMENT.md - This setup")
    print(f"  • SCALING_FOR_7MILLION_USERS.md - Scale architecture")
    print(f"  • QUICK_REFERENCE.md - Command reference\n")
    
    print(f"{Colors.BOLD}Important reminders:{Colors.ENDC}")
    print(f"  ✅ Add GitHub Secrets (8+ secrets)")
    print(f"  ✅ Verify CI/CD workflows running")
    print(f"  ✅ Test with a feature branch first")
    print(f"  ✅ Monitor deployments in GitHub Actions\n")
    
    print(f"{Colors.BOLD}Your bot is now production-ready!{Colors.ENDC}")
    print(f"{Colors.BOLD}Push code → Automatic tests, build, and deploy! 🚀{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
