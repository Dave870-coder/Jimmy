#!/usr/bin/env python3
"""
Jimmy Bot URL Verification Script
Tests both GitHub Pages dashboard and Render backend URLs
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Tuple

# URLs to test
GITHUB_PAGES_URL = "https://dave870-coder.github.io/Jimmy/"
RENDER_BACKEND_URL = "https://jimmy-ai-bot.onrender.com"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_github_pages() -> Tuple[bool, Dict]:
    """Test GitHub Pages dashboard URL"""
    print_header("Testing GitHub Pages Dashboard")
    
    try:
        print_info(f"URL: {GITHUB_PAGES_URL}")
        response = requests.get(GITHUB_PAGES_URL, timeout=10)
        
        if response.status_code == 200:
            print_success(f"Dashboard loads successfully (Status: {response.status_code})")
            
            # Check for key content
            checks = {
                "Jimmy Bot Dashboard": "Jimmy Bot Dashboard" in response.text,
                "Dashboard title": "Connect your users" in response.text,
                "Settings form": "Telegram bot token" in response.text,
                "WhatsApp section": "WhatsApp connection" in response.text,
            }
            
            all_good = True
            for check_name, result in checks.items():
                if result:
                    print_success(f"Found: {check_name}")
                else:
                    print_warning(f"Missing: {check_name}")
                    all_good = False
            
            return True, {"status": "live", "status_code": 200, "all_checks": all_good}
        else:
            print_error(f"Dashboard returned status {response.status_code}")
            return False, {"status": "error", "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot reach GitHub Pages URL (connection error)")
        return False, {"status": "connection_error"}
    except requests.exceptions.Timeout:
        print_error("GitHub Pages request timed out")
        return False, {"status": "timeout"}
    except Exception as e:
        print_error(f"Error testing GitHub Pages: {e}")
        return False, {"status": "error", "message": str(e)}

def test_render_backend() -> Tuple[bool, Dict]:
    """Test Render backend URL"""
    print_header("Testing Render Backend")
    
    try:
        print_info(f"URL: {RENDER_BACKEND_URL}")
        print_info("Testing /health endpoint...")
        
        health_url = f"{RENDER_BACKEND_URL}/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print_success(f"Backend is healthy (Status: {response.status_code})")
                print_success(f"Health data: {json.dumps(data, indent=2)}")
                
                return True, {"status": "healthy", "status_code": 200, "health": data}
            except json.JSONDecodeError:
                print_success(f"Backend responds (Status: {response.status_code})")
                return True, {"status": "responding", "status_code": 200}
        else:
            print_warning(f"Backend returned status {response.status_code}")
            return True, {"status": "warning", "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        print_warning("Cannot reach Render backend yet (may still be deploying)")
        print_info("If Render deployment is in progress, this is normal")
        print_info("Wait 3-5 minutes and try again")
        return False, {"status": "not_deployed", "message": "Connection refused"}
    except requests.exceptions.Timeout:
        print_warning("Render backend request timed out (may be sleeping on free tier)")
        print_info("First request wakes free tier instance (takes ~30s)")
        return False, {"status": "timeout"}
    except Exception as e:
        print_error(f"Error testing Render backend: {e}")
        return False, {"status": "error", "message": str(e)}

def test_api_connection() -> Tuple[bool, Dict]:
    """Test if dashboard can connect to backend"""
    print_header("Testing API Connection (Dashboard ↔ Backend)")
    
    try:
        print_info("Checking if backend API is accessible...")
        
        # Try to reach a simple API endpoint
        api_url = f"{RENDER_BACKEND_URL}/api/v1/admin/health"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            print_success(f"API endpoint is accessible (Status: {response.status_code})")
            return True, {"status": "connected", "status_code": 200}
        elif response.status_code == 404:
            print_warning(f"API endpoint not found (Status: {response.status_code})")
            print_info("This may indicate backend is not fully initialized")
            return False, {"status": "not_ready", "status_code": 404}
        else:
            print_warning(f"API returned status {response.status_code}")
            return False, {"status": "error", "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        print_warning("Cannot reach backend API yet")
        return False, {"status": "not_ready"}
    except Exception as e:
        print_error(f"Error testing API connection: {e}")
        return False, {"status": "error", "message": str(e)}

def generate_report(github_result: Tuple, render_result: Tuple, api_result: Tuple) -> Dict:
    """Generate a summary report"""
    github_ok, github_data = github_result
    render_ok, render_data = render_result
    api_ok, api_data = api_result
    
    return {
        "timestamp": datetime.now().isoformat(),
        "github_pages": {
            "status": "✓ LIVE" if github_ok else "✗ ERROR",
            "details": github_data
        },
        "render_backend": {
            "status": "✓ LIVE" if render_ok else "⚠ NOT YET DEPLOYED",
            "details": render_data
        },
        "api_connection": {
            "status": "✓ CONNECTED" if api_ok else "⚠ PENDING",
            "details": api_data
        },
        "overall_status": "READY" if (github_ok and render_ok and api_ok) else "PARTIAL"
    }

def print_report(report: Dict):
    """Print the final report"""
    print_header("Deployment Status Report")
    
    print(f"Timestamp: {report['timestamp']}\n")
    
    # GitHub Pages
    github_status = report['github_pages']['status']
    print(f"GitHub Pages Dashboard: {github_status}")
    print(f"  URL: {GITHUB_PAGES_URL}")
    
    # Render Backend
    render_status = report['render_backend']['status']
    print(f"\nRender Backend: {render_status}")
    print(f"  URL: {RENDER_BACKEND_URL}")
    
    # API Connection
    api_status = report['api_connection']['status']
    print(f"\nAPI Connection: {api_status}")
    
    # Overall
    overall = report['overall_status']
    if overall == "READY":
        print(f"\n{GREEN}{BOLD}Overall: READY FOR PRODUCTION{RESET}")
        print("Both dashboard and backend are live and connected!")
    elif overall == "PARTIAL":
        print(f"\n{YELLOW}{BOLD}Overall: PARTIAL DEPLOYMENT{RESET}")
        print("GitHub Pages is live but backend deployment pending")
        print("Next steps:")
        print("  1. Deploy to Render (see RENDER_QUICK_DEPLOY.md)")
        print("  2. Add API URL to GitHub Secrets")
        print("  3. Rebuild dashboard")
        print("  4. Run this script again to verify")
    
    print()

def main():
    """Main verification function"""
    print(f"\n{BOLD}{BLUE}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║      Jimmy Bot URL Verification Script                 ║")
    print("║      Testing GitHub Pages + Render Deployment         ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info("Starting verification tests...\n")
    
    # Run tests
    github_result = test_github_pages()
    render_result = test_render_backend()
    api_result = test_api_connection()
    
    # Generate and print report
    report = generate_report(github_result, render_result, api_result)
    print_report(report)
    
    # Return exit code
    if report['overall_status'] == "READY":
        print(f"{GREEN}{BOLD}✓ All systems go! Your Jimmy Bot is production-ready.{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}{BOLD}⚠ Deployment incomplete. Follow the steps above.{RESET}\n")
        return 1

if __name__ == "__main__":
    exit(main())
