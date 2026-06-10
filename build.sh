#!/bin/bash
set -e

echo "=========================================="
echo "Building Jimmy AI Bot Platform for Render"
echo "=========================================="

echo ""
echo "Python version:"
python3 --version

echo ""
echo "Upgrading pip, setuptools, and wheel..."
pip install --no-cache-dir --upgrade pip setuptools wheel

echo ""
echo "Installing project dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install --no-cache-dir -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Verifying core dependencies..."
echo "=========================================="

echo ""
echo "Checking FastAPI..."
python3 -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__}')" || exit 1

echo ""
echo "Checking SQLAlchemy..."
python3 -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__}')" || exit 1

echo ""
echo "Checking Pydantic..."
python3 -c "import pydantic; print(f'✅ Pydantic {pydantic.__version__}')" || exit 1

echo ""
echo "Checking Uvicorn..."
python3 -c "import uvicorn; print(f'✅ Uvicorn {uvicorn.__version__}')" || exit 1

echo ""
echo "=========================================="
echo "Initializing database..."
echo "=========================================="

if [ -f "init_database.py" ]; then
    python3 init_database.py
    if [ $? -eq 0 ]; then
        echo "✅ Database initialization successful"
    else
        echo "⚠️  Database initialization completed with warnings"
        echo "    (Database will be created on first app startup)"
    fi
else
    echo "⚠️  init_database.py not found, skipping pre-initialization"
    echo "    (Database will be created on first app startup)"
fi

echo ""
echo "=========================================="
echo "✅ Build complete - ready for deployment"
echo "=========================================="



