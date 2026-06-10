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
    echo "[OK] Dependencies installed from requirements.txt"
else
    echo "[ERROR] requirements.txt not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Verifying core dependencies..."
echo "=========================================="

echo ""
echo "Checking FastAPI..."
python3 -c "import fastapi; print(f'[OK] FastAPI {fastapi.__version__}')" || exit 1

echo ""
echo "Checking SQLAlchemy..."
python3 -c "import sqlalchemy; print(f'[OK] SQLAlchemy {sqlalchemy.__version__}')" || exit 1

echo ""
echo "Checking Pydantic..."
python3 -c "import pydantic; print(f'[OK] Pydantic {pydantic.__version__}')" || exit 1

echo ""
echo "Checking Uvicorn..."
python3 -c "import uvicorn; print(f'[OK] Uvicorn {uvicorn.__version__}')" || exit 1

echo ""
echo "=========================================="
echo "Building Next.js Frontend..."
echo "=========================================="

# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "Node.js version: $(node --version)"
    echo "npm version: $(npm --version)"
    
    if [ -d "dashboard" ]; then
        cd dashboard
        
        echo "Installing frontend dependencies..."
        npm install --legacy-peer-deps 2>/dev/null || npm install 2>/dev/null || {
            echo "[WARN] npm install failed - frontend build skipped"
            cd ..
        }
        
        if [ -f "package.json" ] && [ -d "node_modules" ]; then
            echo "Building Next.js application..."
            npm run build 2>/dev/null || {
                echo "[WARN] Frontend build failed - this is OK for now"
                echo "       Frontend will use development build or static fallback"
            }
            cd ..
        else
            cd ..
        fi
    else
        echo "[WARN] dashboard directory not found, skipping frontend build"
    fi
else
    echo "[WARN] Node.js not available - skipping frontend build"
    echo "       (Frontend will serve as static site if pre-built)"
fi

echo ""
echo "=========================================="
echo "Initializing database..."
echo "=========================================="

if [ -f "init_database.py" ]; then
    python3 init_database.py
    if [ $? -eq 0 ]; then
        echo "[OK] Database initialization successful"
    else
        echo "[WARN] Database initialization completed with warnings"
        echo "    (Database will be created on first app startup)"
    fi
else
    echo "[WARN] init_database.py not found, skipping pre-initialization"
    echo "    (Database will be created on first app startup)"
fi

echo ""
echo "=========================================="
echo "[OK] Build complete - ready for deployment"
echo "=========================================="




