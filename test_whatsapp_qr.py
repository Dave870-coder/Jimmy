#!/usr/bin/env python
"""WhatsApp QR Code Authentication Test Script."""

import asyncio
import httpx
import json
import time
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
QR_ENDPOINT = f"{API_BASE_URL}/api/v1/whatsapp-qr"


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


async def test_api_health():
    """Test API health."""
    print_info("Checking API health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print_success("API is healthy")
                return True
    except Exception as e:
        print_error(f"API is not responding: {e}")
        return False


async def start_connection():
    """Start a new WhatsApp connection."""
    print_info("Starting WhatsApp connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{QR_ENDPOINT}/start-connection",
                json={"name": "Test Connection"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                connection_id = data.get("connection_id")
                print_success(f"Connection started: {connection_id}")
                return connection_id
            else:
                print_error(f"Failed to start connection: {response.text}")
                return None
    except Exception as e:
        print_error(f"Error starting connection: {e}")
        return None


async def get_qr_code(connection_id: str):
    """Get QR code for connection."""
    print_info("Retrieving QR code...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{QR_ENDPOINT}/qr-code/{connection_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                qr_data = data.get("qr_code_data", "")
                
                # Save QR code as HTML file
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp QR Code</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: Arial, sans-serif;
            margin: 0;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        p {{
            color: #666;
            margin-bottom: 30px;
        }}
        img {{
            max-width: 100%;
            border: 2px solid #667eea;
            border-radius: 10px;
        }}
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 10px;
            font-size: 14px;
            color: #333;
        }}
        .connection-id {{
            font-family: monospace;
            background: #e0e0e0;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 WhatsApp Connection</h1>
        <p>Scan this QR code with WhatsApp on your phone</p>
        <img src="{qr_data}" alt="WhatsApp QR Code">
        <div class="info">
            <p>Settings → Linked Devices → Link a device</p>
            <div class="connection-id">
                <strong>Connection ID:</strong><br>{connection_id}
            </div>
            <p style="margin-top: 10px; color: #999; font-size: 12px;">
                QR code expires in 5 minutes
            </p>
        </div>
    </div>
</body>
</html>
"""
                
                # Save to file
                html_file = Path("whatsapp_qr_code.html")
                html_file.write_text(html_content)
                
                print_success(f"QR code saved to {html_file}")
                print_info(f"Open in browser: file://{html_file.absolute()}")
                
                return connection_id
            else:
                print_error(f"Failed to get QR code: {response.text}")
                return None
    except Exception as e:
        print_error(f"Error getting QR code: {e}")
        return None


async def wait_for_authentication(connection_id: str, timeout: int = 120):
    """Wait for authentication."""
    print_info(f"Waiting for authentication (timeout: {timeout}s)...")
    print_info("Scan the QR code with your WhatsApp phone...")
    
    try:
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(
                        f"{QR_ENDPOINT}/status/{connection_id}",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("connection_status", {}).get("status")
                        elapsed = int(time.time() - start_time)
                        
                        # Update status line
                        sys.stdout.write(f"\r📱 Status: {status:15} ({elapsed}s)   ")
                        sys.stdout.flush()
                        
                        if status == "authenticated":
                            print()
                            print_success("WhatsApp authenticated!")
                            
                            # Print full details
                            connection_info = data.get("connection_status", {})
                            print_info(f"Phone: {connection_info.get('phone_number')}")
                            print_info(f"Connected at: {connection_info.get('authenticated_at')}")
                            
                            return True
                        
                        elif status == "error":
                            print()
                            error_msg = data.get("connection_status", {}).get("error_message")
                            print_error(f"Authentication error: {error_msg}")
                            return False
                    
                except Exception as e:
                    print_warning(f"Connection check failed: {e}")
                
                await asyncio.sleep(2)
            
            print()
            print_error("Authentication timeout")
            return False
    
    except Exception as e:
        print_error(f"Error waiting for authentication: {e}")
        return False


async def get_connection_info(connection_id: str):
    """Get final connection information."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{QR_ENDPOINT}/status/{connection_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                conn_info = data.get("connection_status", {})
                
                print_info("Connection Information:")
                print_info(f"  Connection ID: {conn_info.get('connection_id')}")
                print_info(f"  Status: {conn_info.get('status')}")
                print_info(f"  Phone: {conn_info.get('phone_number')}")
                print_info(f"  Active: {conn_info.get('is_active')}")
                print_info(f"  Created: {conn_info.get('created_at')}")
                
                return conn_info
    except Exception as e:
        print_error(f"Error getting connection info: {e}")
        return None


async def list_connections():
    """List all active connections."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{QR_ENDPOINT}/connections",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                
                print_info(f"Total connections: {len(connections)}")
                
                if connections:
                    print("\n{:<40} {:<20} {:<15}".format("Connection ID", "Status", "Phone"))
                    print("-" * 75)
                    for conn in connections:
                        print("{:<40} {:<20} {:<15}".format(
                            conn.get('connection_id', '')[:40],
                            conn.get('status', ''),
                            conn.get('phone_number', 'N/A')
                        ))
    except Exception as e:
        print_error(f"Error listing connections: {e}")


async def main():
    """Main test flow."""
    print_header("WhatsApp QR Code Authentication Test")
    
    # Check API health
    print("\n[1/5] Checking API health...")
    if not await test_api_health():
        print_error("Please start the bot platform first: docker-compose up -d")
        sys.exit(1)
    
    # Start connection
    print("\n[2/5] Starting new connection...")
    connection_id = await start_connection()
    if not connection_id:
        print_error("Failed to start connection")
        sys.exit(1)
    
    # Get QR code
    print("\n[3/5] Getting QR code...")
    if not await get_qr_code(connection_id):
        print_error("Failed to get QR code")
        sys.exit(1)
    
    # Wait for authentication
    print("\n[4/5] Waiting for authentication...")
    if not await wait_for_authentication(connection_id):
        print_error("Authentication failed")
        sys.exit(1)
    
    # Get final info
    print("\n[5/5] Getting connection details...")
    conn_info = await get_connection_info(connection_id)
    
    # Summary
    print_header("Test Complete! ✅")
    
    print_success("Your WhatsApp connection is ready!")
    print_info(f"Connection ID: {connection_id}")
    print_info("You can now use this connection for:")
    print_info("  - Send messages")
    print_info("  - Receive webhooks")
    print_info("  - Integration with your bot")
    
    # List all connections
    print("\nActive Connections:")
    await list_connections()
    
    print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
    print("1. Your bot can now receive messages from this WhatsApp connection")
    print("2. Deploy to production with webhooks")
    print("3. Use connection_id in your integrations")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
