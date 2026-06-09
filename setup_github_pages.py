#!/usr/bin/env python3
"""
GitHub Pages Dashboard Setup - Automated Configuration
Enables GitHub Pages for your Jimmy AI Bot dashboard.
"""

import subprocess
import sys
import os
from pathlib import Path

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

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def print_step(number: int, text: str):
    """Print step."""
    print(f"{Colors.BOLD}{Colors.BLUE}[Step {number}]{Colors.ENDC} {text}")

def main():
    """Main setup function."""
    
    print_header("🌐 GitHub Pages Dashboard Setup")
    
    print(f"{Colors.BOLD}This will configure your Jimmy AI Bot dashboard for GitHub Pages!{Colors.ENDC}\n")
    
    # Step 1: Check if in right directory
    print_step(1, "Verify project structure")
    
    dashboard_path = Path("dashboard")
    if not dashboard_path.exists():
        print_warning("dashboard/ folder not found!")
        sys.exit(1)
    
    print_success("dashboard/ folder found")
    
    # Step 2: Check if files exist
    print_step(2, "Check configuration files")
    
    required_files = [
        "dashboard/next.config.js",
        "dashboard/package.json",
        ".github/workflows/deploy-dashboard.yml"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path} exists")
        else:
            print_warning(f"{file_path} not found!")
    
    # Step 3: Get GitHub username
    print_step(3, "Get your GitHub username")
    
    username = input(f"{Colors.BOLD}Enter your GitHub username: {Colors.ENDC}").strip()
    
    if not username:
        print_warning("GitHub username is required!")
        sys.exit(1)
    
    dashboard_url = f"https://{username}.github.io/jimmy-ai-bot/"
    print_success(f"Your dashboard URL will be: {Colors.CYAN}{dashboard_url}{Colors.ENDC}")
    
    # Step 4: Instructions
    print_step(4, "Manual GitHub Pages Setup")
    
    print(f"\n{Colors.BOLD}Follow these steps in GitHub:{Colors.ENDC}\n")
    
    instructions = [
        "1. Go to: https://github.com/" + username + "/jimmy-ai-bot/settings",
        "2. Click 'Pages' in the left sidebar",
        "3. Under 'Build and deployment':",
        "   - Select: GitHub Actions",
        "   - Click: Save",
        "4. Wait 2-3 minutes for deployment",
        "5. Visit your dashboard: " + dashboard_url
    ]
    
    for instruction in instructions:
        if instruction.startswith("5. "):
            print(f"{Colors.GREEN}{instruction}{Colors.ENDC}")
        else:
            print(f"{Colors.CYAN}{instruction}{Colors.ENDC}")
    
    # Step 5: API Configuration
    print_step(5, "Optional: Set API URL")
    
    print(f"\n{Colors.BOLD}To connect your dashboard to the API:{Colors.ENDC}\n")
    
    api_steps = [
        "1. Go to: https://github.com/" + username + "/jimmy-ai-bot/settings/secrets/actions",
        "2. Click 'New repository secret'",
        "3. Add Secret:",
        "   - Name: NEXT_PUBLIC_API_BASE",
        "   - Value: https://your-bot-api.railway.app",
        "4. Click 'Add secret'",
        "5. Push code to trigger rebuild: git push origin main",
        "6. Wait 2-3 minutes",
        "7. Your dashboard will now show live data!"
    ]
    
    for step in api_steps:
        print(f"{Colors.CYAN}{step}{Colors.ENDC}")
    
    # Step 6: Verification
    print_step(6, "Verify Deployment")
    
    print(f"\n{Colors.BOLD}After 2-3 minutes, check:{Colors.ENDC}\n")
    
    verify_steps = [
        f"1. Dashboard: {Colors.GREEN}{dashboard_url}{Colors.ENDC}",
        f"2. Actions: https://github.com/{username}/jimmy-ai-bot/actions",
        "3. Look for 'Deploy Dashboard' workflow with green checkmark ✅"
    ]
    
    for step in verify_steps:
        print(f"   {step}")
    
    # Step 7: Deployment
    print_step(7, "Deploy Dashboard")
    
    print(f"\n{Colors.BOLD}Push code to trigger deployment:{Colors.ENDC}\n")
    
    deploy_cmd = "git push origin main"
    print(f"{Colors.CYAN}$ {deploy_cmd}{Colors.ENDC}")
    
    deploy = input(f"\n{Colors.BOLD}Ready to push? (y/n): {Colors.ENDC}").strip().lower()
    
    if deploy == 'y':
        try:
            result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print_success("Code pushed to GitHub!")
                print(f"\n{Colors.GREEN}GitHub Actions will now:{Colors.ENDC}")
                print("  1. Build your dashboard")
                print("  2. Deploy to GitHub Pages")
                print("  3. Update your live site")
            else:
                print_warning(f"Push failed: {result.stderr}")
        except Exception as e:
            print_warning(f"Error: {e}")
    
    # Final summary
    print_header("✨ Setup Complete!")
    
    print(f"{Colors.BOLD}Your Dashboard is Ready!{Colors.ENDC}\n")
    
    print(f"📱 {Colors.BOLD}Dashboard URL:{Colors.ENDC}")
    print(f"   {Colors.GREEN}{dashboard_url}{Colors.ENDC}\n")
    
    print(f"⏱️  {Colors.BOLD}Timeline:{Colors.ENDC}")
    print(f"   {Colors.CYAN}2-3 min:{Colors.ENDC} GitHub Actions builds and deploys")
    print(f"   {Colors.CYAN}Then:{Colors.ENDC} Dashboard is live at your URL!\n")
    
    print(f"📋 {Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"   1. Open GitHub Pages settings (done above)")
    print(f"   2. Push code: {Colors.CYAN}git push origin main{Colors.ENDC}")
    print(f"   3. Wait 2-3 minutes")
    print(f"   4. Visit your dashboard URL")
    print(f"   5. Enjoy! 🎉\n")
    
    print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
    print(f"   • DASHBOARD_URL.md - This guide")
    print(f"   • GITHUB_PAGES_SETUP.md - Detailed setup")
    print(f"   • dashboard/README.md - Dashboard docs\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}✅ All Set!{Colors.ENDC}\n")
    print(f"Visit {Colors.CYAN}{dashboard_url}{Colors.ENDC} in 2-3 minutes!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)
