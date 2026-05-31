#!/usr/bin/env bash
# Deployment configuration helper script

echo "🚀 AI Bot Platform - Deployment Configuration"
echo "=============================================="
echo ""

# Check environment
ENV=${1:-production}
echo "📋 Environment: $ENV"

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/chroma
mkdir -p logs

# Build Docker image
build_docker() {
    echo "🐳 Building Docker image..."
    docker build -t ai-bot-platform:latest .
    docker build -t ai-bot-platform:latest-dashboard ./dashboard
}

# Deploy to Heroku
deploy_heroku() {
    echo "🚀 Deploying to Heroku..."
    heroku login
    heroku create ai-bot-platform
    heroku config:set GOOGLE_API_KEY=$GOOGLE_API_KEY
    heroku config:set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
    git push heroku main
    heroku run alembic upgrade head
}

# Deploy to Railway
deploy_railway() {
    echo "🚀 Deploying to Railway..."
    railway login
    railway init
    railway up
}

# Deploy to AWS EC2
deploy_aws() {
    echo "🚀 Deploying to AWS EC2..."
    echo "Instance setup required - follow AWS guide"
}

case $ENV in
    docker)
        build_docker
        ;;
    heroku)
        deploy_heroku
        ;;
    railway)
        deploy_railway
        ;;
    aws)
        deploy_aws
        ;;
    *)
        echo "Usage: $0 {docker|heroku|railway|aws}"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment configuration complete!"
