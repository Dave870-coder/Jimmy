# Installation Guide

## Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)
- Node.js 18+ (for dashboard)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-bot-platform.git
cd ai-bot-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Setup PostgreSQL Database

```bash
# Create database
createdb aibot_db

# Create user
createuser aibot_user

# Grant privileges
psql -c "ALTER USER aibot_user WITH PASSWORD 'aibot_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE aibot_db TO aibot_user;"
```

### 6. Setup Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install locally (macOS)
brew install redis
redis-server
```

### 7. Run Database Migrations

```bash
alembic upgrade head
```

### 8. Start Development Server

```bash
uvicorn src.main:app --reload
```

API will be available at `http://localhost:8000`

## Docker Setup

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Dashboard (port 3000)

### Build Custom Image

```bash
docker build -t ai-bot-platform:latest -f docker/Dockerfile .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ai-bot \
  ai-bot-platform:latest
```

## Configuration

### Required API Keys

Get these from the respective services:

1. **OpenAI**
   - Sign up at https://openai.com
   - Get API key from https://platform.openai.com/api-keys

2. **Google AI**
   - Sign up at https://makersuite.google.com/app/apikey
   - Get API key

3. **Telegram**
   - Create bot via @BotFather on Telegram
   - Get token from BotFather

4. **WhatsApp**
   - Register at https://developers.facebook.com/
   - Get access token and business account ID

### Environment Variables

Update `.env` file:

```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
TELEGRAM_BOT_TOKEN=...
WHATSAPP_ACCESS_TOKEN=...
DATABASE_URL=postgresql://user:password@localhost/aibot_db
REDIS_URL=redis://localhost:6379/0
```

## First Run

1. Create admin user
   ```bash
   python scripts/create_admin.py
   ```

2. Initialize knowledge base
   ```bash
   python scripts/init_knowledge_base.py
   ```

3. Start development server
   ```bash
   uvicorn src.main:app --reload
   ```

4. Access dashboard
   ```
   http://localhost:3000
   ```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_auth.py -v
```

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U aibot_user -d aibot_db

# Reset database
dropdb aibot_db
createdb aibot_db
alembic upgrade head
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Next Steps

- [API Documentation](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Architecture Overview](ARCHITECTURE.md)
