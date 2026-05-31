#!/bin/bash
# Quick start script for the AI Bot Platform

set -e

echo "🚀 AI Bot Platform - Quick Start"
echo "================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)"
    echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo ""
    echo "Then run this script again!"
    exit 0
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Install Docker from: https://docker.com"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    echo "   Install Docker Desktop which includes docker-compose"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Check if services are healthy
echo ""
echo "🏥 Checking service health..."
docker-compose ps

# Test API
echo ""
echo "🧪 Testing API health..."
response=$(curl -s http://localhost:8000/health || echo '{"status": "error"}')
echo "API Response: $response"

if echo "$response" | grep -q "healthy"; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API might still be starting..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Open Telegram and find your bot"
echo "2. Send /start to test the bot"
echo "3. View logs: docker-compose logs -f api"
echo "4. API docs: http://localhost:8000/docs"
echo ""
echo "💡 To stop services: docker-compose down"
echo ""
