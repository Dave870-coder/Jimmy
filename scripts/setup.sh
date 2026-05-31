#!/bin/bash

# Setup script for AI Bot Platform

set -e

echo "🚀 Setting up AI Bot Platform..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# Setup environment
echo "⚙️  Setting up environment..."
cp .env.example .env
echo "📝 Edit .env with your configuration"

# Create data directory
mkdir -p data

# Database setup
echo "🗄️  Setting up database..."
createdb aibot_db || true
createuser aibot_user || true
psql -c "ALTER USER aibot_user WITH PASSWORD 'aibot_password';" || true
psql -c "GRANT ALL PRIVILEGES ON DATABASE aibot_db TO aibot_user;" || true

# Run migrations
echo "🔄 Running migrations..."
alembic upgrade head

# Initialize database
echo "📋 Initializing database..."
python scripts/init_db.py

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Start development server: uvicorn src.main:app --reload"
echo "3. Access API docs: http://localhost:8000/docs"
