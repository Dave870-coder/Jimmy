# WhatsApp QR Code Authentication - Setup & Testing Guide 📱

This guide shows you how to set up and test the WhatsApp QR code authentication system.

---

## 🎯 Overview

The QR code authentication system uses Selenium WebDriver to:
1. Launch WhatsApp Web in a headless browser
2. Display the QR code from WhatsApp Web
3. Wait for you to scan it with your phone
4. Authenticate your WhatsApp connection
5. Use the authenticated connection for bot interactions

---

## 📋 Prerequisites

### 1. Dependencies
Ensure you have the latest dependencies installed:

```bash
# Install Selenium and QR code libraries
pip install selenium qrcode[pil]

# Or if using poetry
poetry install

# Or with the new pyproject.toml
pip install -e .
```

### 2. Chrome/Chromium Browser
Selenium needs Chrome or Chromium installed:

**Windows:**
```bash
# Check if Chrome is installed at default location
# Or install via:
choco install googlechrome
```

**Mac:**
```bash
brew install google-chrome
```

**Linux (Ubuntu):**
```bash
sudo apt-get install google-chrome-stable
```

### 3. ChromeDriver
The system uses webdriver-manager to auto-download ChromeDriver. No manual setup needed!

---

## 🚀 Quick Start

### 1. Start Your Bot Platform

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
docker-compose ps

# Verify API is running
curl http://localhost:8000/health
```

### 2. Start WhatsApp QR Code Authentication

Open a terminal and run:

```bash
# Create a new WhatsApp connection
curl -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
  -H "Content-Type: application/json" \
  -d '{"name": "My WhatsApp Bot"}'
```

**Response:**
```json
{
  "status": "success",
  "connection_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Scan the QR code with WhatsApp to connect",
  "has_qr_code": true
}
```

**Copy the `connection_id` for next steps!**

### 3. Get QR Code Image

```bash
curl http://localhost:8000/api/v1/whatsapp-qr/qr-code/{connection_id} \
  > qr_code.json
```

Or open in browser (replace with your connection_id):
```
http://localhost:8000/api/v1/whatsapp-qr/qr-code/550e8400-e29b-41d4-a716-446655440000
```

This returns:
```json
{
  "connection_id": "550e8400-e29b-41d4-a716-446655440000",
  "qr_code_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "message": "Scan this QR code with WhatsApp to connect",
  "expires_in_seconds": 300
}
```

### 4. Scan QR Code with Your Phone

1. Open WhatsApp on your phone
2. Go to **Settings** → **Linked Devices** (or **Linked accounts**)
3. Tap **Link a device**
4. **Scan the QR code** (displayed in browser or from the API response)

### 5. Verify Authentication

In a new terminal, check the connection status:

```bash
# Check status every 2 seconds
while true; do
  curl http://localhost:8000/api/v1/whatsapp-qr/status/{connection_id}
  sleep 2
done
```

Or use the blocking authenticate endpoint:

```bash
# This will wait up to 60 seconds for authentication
curl -X POST http://localhost:8000/api/v1/whatsapp-qr/authenticate/{connection_id}?timeout=120
```

When authenticated, you'll see:
```json
{
  "status": "success",
  "message": "WhatsApp connection authenticated",
  "phone_number": "connected",
  "connection_status": {
    "connection_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "authenticated",
    "phone_number": "connected",
    "is_active": true,
    "authenticated_at": "2026-05-31T10:30:45.123456"
  }
}
```

---

## 🔄 Connection Lifecycle

```
1. START CONNECTION
   ↓
2. GENERATE QR CODE
   ↓
3. DISPLAY QR CODE TO USER
   ↓
4. USER SCANS WITH PHONE
   ↓
5. WAIT FOR AUTHENTICATION
   ↓
6. AUTHENTICATED ✅
   ↓
7. USE FOR MESSAGING
   ↓
8. DISCONNECT (OPTIONAL)
```

---

## 📊 API Endpoints

### Start Connection
```bash
POST /api/v1/whatsapp-qr/start-connection
Content-Type: application/json

{
  "name": "My WhatsApp Connection"
}
```

### Get QR Code
```bash
GET /api/v1/whatsapp-qr/qr-code/{connection_id}
```

### Check Connection Status
```bash
GET /api/v1/whatsapp-qr/status/{connection_id}
```

Status values:
- `disconnected` - Not connected
- `waiting_qr` - Waiting for QR generation
- `qr_ready` - Ready to scan
- `scanned` - User has scanned
- `authenticated` - Successfully authenticated ✅
- `error` - Error occurred

### Authenticate (Blocking)
```bash
POST /api/v1/whatsapp-qr/authenticate/{connection_id}?timeout=120
```

### Get All Connections
```bash
GET /api/v1/whatsapp-qr/connections
```

### Disconnect
```bash
DELETE /api/v1/whatsapp-qr/disconnect/{connection_id}
```

### Real-time Status (WebSocket)
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/whatsapp-qr/ws/{connection_id}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Status:', data.status);
};
```

---

## 🧪 Complete Test Workflow

Here's a complete bash script to test the entire flow:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 WhatsApp QR Code Authentication Test${NC}\n"

# 1. Start connection
echo -e "${YELLOW}1️⃣  Starting connection...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Connection"}')

CONNECTION_ID=$(echo $RESPONSE | grep -o '"connection_id":"[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✅ Connection started: $CONNECTION_ID${NC}\n"

# 2. Get QR code
echo -e "${YELLOW}2️⃣  Getting QR code...${NC}"
QR_RESPONSE=$(curl -s "http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONNECTION_ID")
echo -e "${GREEN}✅ QR code generated${NC}\n"

# 3. Display instructions
echo -e "${YELLOW}3️⃣  Instructions:${NC}"
echo -e "   1. Open WhatsApp on your phone"
echo -e "   2. Go to Settings → Linked Devices → Link a device"
echo -e "   3. Scan the QR code shown in your browser"
echo -e "   4. You have 5 minutes (300 seconds)\n"

# 4. Open QR code in browser (if on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo -e "${YELLOW}Opening QR code in browser...${NC}"
  open "http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONNECTION_ID"
fi

# 5. Poll for authentication
echo -e "${YELLOW}4️⃣  Waiting for authentication...${NC}"
MAX_WAIT=120
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
  
  echo -ne "\r   Status: $STATUS (${ELAPSED}s)   "
  
  if [ "$STATUS" = "authenticated" ]; then
    echo -e "\n${GREEN}✅ Authenticated!${NC}\n"
    
    # Get full connection info
    curl -s "http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID" | jq '.'
    echo ""
    
    echo -e "${GREEN}✅ Your WhatsApp connection is ready to use!${NC}"
    echo -e "${YELLOW}Connection ID: $CONNECTION_ID${NC}\n"
    exit 0
  fi
  
  if [ "$STATUS" = "error" ]; then
    echo -e "\n${RED}❌ Authentication failed${NC}\n"
    curl -s "http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID" | jq '.'
    exit 1
  fi
  
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done

echo -e "\n${RED}❌ Authentication timeout${NC}"
exit 1
```

Save as `test_whatsapp_qr.sh` and run:

```bash
chmod +x test_whatsapp_qr.sh
./test_whatsapp_qr.sh
```

---

## 🌐 Web Dashboard Example

Create an HTML file to display QR code in real-time:

```html
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp QR Code Scanner</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        #qrCode {
            max-width: 400px;
            margin: 20px 0;
        }
        #status {
            font-size: 18px;
            margin: 20px 0;
            font-weight: bold;
        }
        .status-waiting { color: #ff9800; }
        .status-scanned { color: #2196f3; }
        .status-authenticated { color: #4caf50; }
        .status-error { color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Connect WhatsApp</h1>
        <div id="status" class="status-waiting">Generating QR Code...</div>
        <img id="qrCode" src="" alt="QR Code">
        <p>Scan with WhatsApp to connect</p>
    </div>

    <script>
        const connectionId = new URLSearchParams(window.location.search).get('id');
        if (!connectionId) {
            // Generate new connection
            fetch('http://localhost:8000/api/v1/whatsapp-qr/start-connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'Web Connection' })
            })
            .then(r => r.json())
            .then(data => {
                window.history.replaceState({}, '', `?id=${data.connection_id}`);
                startMonitoring(data.connection_id);
            });
        } else {
            startMonitoring(connectionId);
        }

        function startMonitoring(id) {
            // Get QR Code
            fetch(`http://localhost:8000/api/v1/whatsapp-qr/qr-code/${id}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('qrCode').src = data.qr_code_data;
                });

            // Monitor status with WebSocket
            const ws = new WebSocket(`ws://localhost:8000/api/v1/whatsapp-qr/ws/${id}`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                const status = document.getElementById('status');
                
                if (data.type === 'status_update') {
                    const connStatus = data.status.status;
                    status.textContent = connStatus.toUpperCase();
                    status.className = `status-${connStatus}`;
                }
                
                if (data.type === 'complete') {
                    status.textContent = '✅ ' + data.message;
                }
            };
        }
    </script>
</body>
</html>
```

Save as `qr_scanner.html` and open:
```bash
open qr_scanner.html
```

---

## 🔍 Troubleshooting

### Issue: "Selenium not installed"
```bash
pip install selenium qrcode[pil]
```

### Issue: "Chrome not found"
Check if Chrome is installed:
```bash
# Windows
where google-chrome
# or
where chrome

# Mac
which google-chrome

# Linux
which google-chrome-stable
```

### Issue: "QR code timeout"
1. Check your internet connection
2. Make sure Chrome can load web.whatsapp.com
3. Try again with a longer timeout

### Issue: "Authentication failed"
1. Make sure you're using the correct phone number for WhatsApp
2. Check that your WhatsApp app is updated
3. Try linking device again
4. Check logs: `docker-compose logs -f api`

### Issue: WebSocket connection refused
Make sure the API is running:
```bash
docker-compose ps api
curl http://localhost:8000/health
```

---

## 📝 Integration with Your Bot

Once authenticated, use the connection in your bot:

```python
from src.bot.whatsapp.connection_manager import get_connection_manager

# Get authenticated connection
manager = await get_connection_manager()
connection = manager.get_connection_status(connection_id)

if connection['is_active']:
    # Use the authenticated connection
    phone_number = connection['phone_number']
    # Send messages, etc.
```

---

## 🔐 Security Notes

✅ **Secure:**
- QR codes expire after 5 minutes
- Session data is stored in memory only
- No credentials stored on disk
- Selenium runs in headless mode

⚠️ **Keep in Mind:**
- QR codes should only be displayed to authorized users
- Don't expose connection URLs publicly
- Use HTTPS in production
- Implement rate limiting on QR code endpoints

---

## 🎯 Next Steps

1. ✅ Test QR code authentication
2. ✅ Get authenticated connection ID
3. ✅ Integrate with your messaging endpoints
4. ✅ Deploy to production with webhooks
5. ✅ Monitor connection status

---

## 📞 Support

For issues:
- Check logs: `docker-compose logs -f api | grep -i whatsapp`
- View API docs: http://localhost:8000/docs
- See full endpoint reference in this file

**Your WhatsApp bot is now live!** 🚀

