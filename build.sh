#!/bin/bash
set -e

echo "=========================================="
echo "Building Jimmy AI Bot Platform for Render"
echo "=========================================="

echo ""
echo "Python version:"
python3 --version

echo ""
echo "Installing dependencies..."
pip install --no-cache-dir --upgrade pip setuptools wheel

echo ""
echo "Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt
else
    pip install --no-cache-dir -e .
fi

echo ""
echo "Verifying FastAPI installation..."
python3 -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"

echo ""
echo "Verifying SQLAlchemy installation..."
python3 -c "import sqlalchemy; print(f'SQLAlchemy version: {sqlalchemy.__version__}')"

echo ""
echo "=========================================="
echo "Initializing database..."
echo "=========================================="
python3 init_database.py
if [ $? -eq 0 ]; then
    echo "✅ Database initialization successful"
else
    echo "⚠️  Database initialization completed with warnings (will retry on first request)"
fi

echo ""
echo "=========================================="
echo "Build complete - ready for deployment"
echo "=========================================="


