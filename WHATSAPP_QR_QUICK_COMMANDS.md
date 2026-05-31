# WhatsApp QR Code - Quick Command Reference 🚀

Copy-paste these commands to quickly test your WhatsApp QR code authentication.

---

## 🎯 One-Liner Tests

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Start Connection & Get QR Code (Single Command)
```bash
curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}' | jq '.connection_id' -r > /tmp/conn_id.txt && \
curl http://localhost:8000/api/v1/whatsapp-qr/qr-code/$(cat /tmp/conn_id.txt)
```

### Test 3: Python Auto-Test (Recommended)
```bash
python test_whatsapp_qr.py
```

---

## 📝 Step-by-Step Commands

### Step 1: Start Connection
```bash
CONNECTION_ID=$(curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.connection_id')

echo "Connection ID: $CONNECTION_ID"
```

### Step 2: Get QR Code (JSON)
```bash
curl http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONNECTION_ID | jq '.qr_code_data' -r | head -c 100
```

### Step 3: Save QR Code as Image
```bash
# Extract base64 and decode to PNG
curl -s http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONNECTION_ID | \
  jq -r '.qr_code_data' | \
  sed 's/data:image\/png;base64,//' | \
  base64 -d > qr_code.png

# Open QR code
# Mac:
open qr_code.png
# Linux:
xdg-open qr_code.png
```

### Step 4: Monitor Status (Auto-Refresh)
```bash
# Bash: Check status every 2 seconds
while true; do
  clear
  echo "Status for: $CONNECTION_ID"
  curl -s http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID | jq '.connection_status'
  echo ""
  echo "Press Ctrl+C to stop. Waiting for scan... (next check in 2s)"
  sleep 2
done
```

### Step 5: Wait for Authentication (Blocking)
```bash
# This command blocks until authenticated (max 120 seconds)
curl -X POST http://localhost:8000/api/v1/whatsapp-qr/authenticate/$CONNECTION_ID?timeout=120 | jq '.'
```

### Step 6: Get Final Status
```bash
curl http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID | jq '.connection_status'
```

### Step 7: Disconnect (Optional)
```bash
curl -X DELETE http://localhost:8000/api/v1/whatsapp-qr/disconnect/$CONNECTION_ID
```

---

## 🔄 Complete Workflow (Copy-Paste)

```bash
#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 WhatsApp QR Code Test${NC}\n"

# 1. Start connection
echo -e "${YELLOW}Starting connection...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Connection"}')

CONNECTION_ID=$(echo $RESPONSE | jq -r '.connection_id')
echo -e "${GREEN}✓ Connection ID: $CONNECTION_ID${NC}\n"

# 2. Get QR code
echo -e "${YELLOW}Getting QR code...${NC}"
QR_RESPONSE=$(curl -s http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONNECTION_ID)
echo -e "${GREEN}✓ QR code ready${NC}\n"

# 3. Inform user
echo -e "${YELLOW}📱 Instructions:${NC}"
echo "  1. Open WhatsApp on your phone"
echo "  2. Go to Settings > Linked Devices > Link a device"
echo "  3. Scan the QR code from browser"
echo "  4. You have 5 minutes"
echo ""

# 4. Open QR code in browser (macOS)
if command -v open &> /dev/null; then
    echo -e "${YELLOW}Opening QR code in browser...${NC}"
    # Save as HTML and open
    cat > /tmp/qr.html <<EOF
<!DOCTYPE html>
<html>
<head><title>WhatsApp QR</title><style>body{display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f0f0f0;}</style></head>
<body><img src="$(echo $QR_RESPONSE | jq -r '.qr_code_data')"></body>
</html>
EOF
    open /tmp/qr.html
fi

# 5. Wait for authentication
echo -e "\n${YELLOW}⏳ Waiting for authentication (timeout: 120s)...${NC}"
START=$(date +%s)
TIMEOUT=120

while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID | jq -r '.connection_status.status')
  ELAPSED=$(($(date +%s) - START))
  
  echo -ne "\r  Status: $STATUS (${ELAPSED}s)   "
  
  if [ "$STATUS" = "authenticated" ]; then
    echo ""
    echo -e "${GREEN}✓ Authenticated!${NC}\n"
    curl -s http://localhost:8000/api/v1/whatsapp-qr/status/$CONNECTION_ID | jq '.connection_status'
    break
  fi
  
  if [ "$STATUS" = "error" ]; then
    echo ""
    echo -e "${RED}✗ Authentication failed${NC}"
    break
  fi
  
  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo ""
    echo -e "${RED}✗ Timeout${NC}"
    break
  fi
  
  sleep 2
done
```

Save as `test.sh`, then:
```bash
chmod +x test.sh
./test.sh
```

---

## 🌐 Browser Console Commands

Open DevTools (F12) and run in Console:

```javascript
// Start connection
fetch('http://localhost:8000/api/v1/whatsapp-qr/start-connection', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Browser Test'})
})
.then(r => r.json())
.then(data => {
  window.connId = data.connection_id;
  console.log('Connection ID:', window.connId);
})

// Get QR code (after connection started)
fetch(`http://localhost:8000/api/v1/whatsapp-qr/qr-code/${window.connId}`)
  .then(r => r.json())
  .then(data => {
    console.log('QR Code Data URL:', data.qr_code_data);
    // Display in new window
    window.open('about:blank').document.write(`<img src="${data.qr_code_data}">`);
  })

// Check status (run multiple times)
fetch(`http://localhost:8000/api/v1/whatsapp-qr/status/${window.connId}`)
  .then(r => r.json())
  .then(data => console.log(data.connection_status))

// WebSocket for live updates
const ws = new WebSocket(`ws://localhost:8000/api/v1/whatsapp-qr/ws/${window.connId}`);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## 📊 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/whatsapp-qr/start-connection` | Start new connection |
| GET | `/api/v1/whatsapp-qr/qr-code/{id}` | Get QR code image |
| GET | `/api/v1/whatsapp-qr/status/{id}` | Check connection status |
| POST | `/api/v1/whatsapp-qr/authenticate/{id}` | Wait for authentication |
| GET | `/api/v1/whatsapp-qr/connections` | List all connections |
| DELETE | `/api/v1/whatsapp-qr/disconnect/{id}` | Disconnect |
| WS | `/api/v1/whatsapp-qr/ws/{id}` | WebSocket for updates |

---

## 🐛 Quick Debugging

### Check if API is running
```bash
curl -v http://localhost:8000/health
```

### View API logs
```bash
docker-compose logs -f api | grep -i whatsapp
```

### Check connection status directly
```bash
curl http://localhost:8000/api/v1/whatsapp-qr/status/{your_connection_id} | jq '.'
```

### List all active connections
```bash
curl http://localhost:8000/api/v1/whatsapp-qr/connections | jq '.connections'
```

### Test WebSocket connection
```bash
# Install websocat first: brew install websocat (macOS) or apt-get install websocat (Linux)
websocat ws://localhost:8000/api/v1/whatsapp-qr/ws/{your_connection_id}
```

---

## ⚡ Performance Tips

### Parallel Testing (Multiple Connections)
```bash
# Start 3 connections in parallel
for i in {1..3}; do
  curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"Connection $i\"}" | jq '.connection_id'
done
```

### Batch Status Check
```bash
# Get all connections and their status
curl -s http://localhost:8000/api/v1/whatsapp-qr/connections | jq '.connections[] | {id: .connection_id, status: .status, phone: .phone_number}'
```

---

## 🔗 Integration Examples

### Python
```python
import asyncio
from src.bot.whatsapp.connection_manager import get_connection_manager

async def test():
    manager = await get_connection_manager()
    conn = await manager.start_connection("test-1")
    print(f"Connection: {conn}")

asyncio.run(test())
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/api/v1/whatsapp-qr/start-connection', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: 'Node Test'})
});

const data = await response.json();
console.log('Connection ID:', data.connection_id);
```

### cURL with Aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias wa-start='curl -s -X POST http://localhost:8000/api/v1/whatsapp-qr/start-connection -H "Content-Type: application/json" -d "{}"'
alias wa-status='curl -s http://localhost:8000/api/v1/whatsapp-qr/status'
alias wa-list='curl -s http://localhost:8000/api/v1/whatsapp-qr/connections | jq ".connections"'

# Then use:
wa-start | jq '.connection_id'
wa-status <connection_id> | jq '.connection_status'
wa-list
```

---

## ✨ Pro Tips

1. **Save connection ID to variable for reuse:**
   ```bash
   export CONN_ID="550e8400-e29b-41d4-a716-446655440000"
   curl http://localhost:8000/api/v1/whatsapp-qr/status/$CONN_ID
   ```

2. **Pretty print JSON responses:**
   ```bash
   curl ... | jq '.'
   ```

3. **Extract specific fields:**
   ```bash
   curl ... | jq '.connection_status.status'
   curl ... | jq '.connection_status.phone_number'
   ```

4. **Watch status in real-time (macOS):**
   ```bash
   watch -n 2 'curl -s http://localhost:8000/api/v1/whatsapp-qr/status/$CONN_ID | jq ".connection_status.status"'
   ```

5. **Save QR code for sharing:**
   ```bash
   curl -s http://localhost:8000/api/v1/whatsapp-qr/qr-code/$CONN_ID | jq -r '.qr_code_data' > qr.txt
   ```

---

**Ready to test? Run:** `python test_whatsapp_qr.py` or `./test.sh`

