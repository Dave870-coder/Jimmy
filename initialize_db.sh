#!/bin/bash
# Initialize database on Render backend
# This script calls the manual initialization endpoint

echo "🚀 Database Initialization Script"
echo "=================================="

BACKEND_URL="https://jimmy-ai-bot.onrender.com"

# Check if backend is running
echo ""
echo "1️⃣ Checking backend status..."
HEALTH=$(curl -s "$BACKEND_URL/health" 2>/dev/null | grep -o '"database":"[^"]*"' || echo "offline")
echo "   Current status: $HEALTH"

# Try to initialize database
echo ""
echo "2️⃣ Initializing database..."
echo "   Calling: POST $BACKEND_URL/initialize-db"

INIT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/initialize-db" \
  -H "Content-Type: application/json" \
  -w "\n%{http_code}")

# Split response and status code
HTTP_CODE=$(echo "$INIT_RESPONSE" | tail -n1)
RESPONSE=$(echo "$INIT_RESPONSE" | head -n-1)

echo "   HTTP Status: $HTTP_CODE"
echo "   Response: $RESPONSE"

# Check if successful
if echo "$RESPONSE" | grep -q '"success":true'; then
    echo ""
    echo "✅ Database initialized successfully!"
    echo ""
    echo "3️⃣ Verifying database status..."
    HEALTH_NEW=$(curl -s "$BACKEND_URL/health" 2>/dev/null)
    echo "   $HEALTH_NEW"
else
    echo ""
    echo "⚠️ Initialization may have failed or is still in progress"
    echo "   Waiting 5 seconds before retry..."
    sleep 5
    
    echo "   Retrying..."
    RETRY_RESPONSE=$(curl -s -X POST "$BACKEND_URL/initialize-db" \
      -H "Content-Type: application/json")
    
    echo "   Retry response: $RETRY_RESPONSE"
fi

echo ""
echo "✨ Complete! Check https://jimmy-ai-bot.onrender.com/health to verify"
