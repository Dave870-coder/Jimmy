# AI Bot Platform

A production-ready AI Bot Platform powered by **Google AI Studio (Gemini)**, integrated with WhatsApp and Telegram, featuring autonomous agents, memory systems, and intelligent task automation.

## 👤 Author

**Onuoha Ikechukwu David**
- Software Engineering Student
- Babcock University
- [View Full Author Details](AUTHOR.md)

## 📊 Dashboard & Web App

### 🌐 Live Web App Dashboard
**[🚀 View Live Dashboard](https://Dave870-coder.github.io/Jimmy/)**

Your Jimmy Bot management dashboard with real-time metrics, monitoring, and control panel.

![Jimmy Bot Dashboard](docs/dashboard-screenshot.png)

The dashboard provides real-time monitoring of bot activity, active users, message counts, and integration setup for Telegram and WhatsApp.

## 🚀 Deploy Now (FREE!)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Dave870-coder/Jimmy)

Click the button above to deploy your bot to **Render for FREE**! The bot will run 24/7 online automatically at zero cost.

**After clicking Deploy:**
1. Authorize with GitHub  
2. Add your API keys (GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN, SECRET_KEY)
3. Click "Create Web Service"
4. Bot is LIVE! 🎉 (No credit card needed!)

### Google AI Studio Setup

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Create or copy an API key.
3. Add it as `GOOGLE_API_KEY` in Render and in your local `.env` file.
4. Use the same key in every environment where you want AI responses.

### Render Environment Variables

Set these in Render for production:

1. `GOOGLE_API_KEY` - required for AI responses.
2. `TELEGRAM_BOT_TOKEN` - required for Telegram webhooks and replies.
3. `SECRET_KEY` - generate a strong production secret.
4. `APP_ENV=production` and `DEBUG=False`.
5. Keep `DATABASE_URL` on the Render disk-backed SQLite path already defined in `render.yaml`.

## ✅ Production Startup Checklist

Use this quick check before you rely on a new deployment:

1. Confirm `/health` is healthy on the live URL.
2. Confirm `/ready` succeeds after startup and migrations.
3. Confirm Telegram `/start` replies from the deployed bot.
4. Confirm WhatsApp QR start returns both QR and barcode payloads.
5. Confirm secrets are set in Render and not stored in Git.
6. Confirm the SQLite path is mounted to persistent storage on Render.

## 🚀 Features

- **🤖 Google AI Integration**: Powered by Gemini 2.0 Flash for fast, intelligent responses
- **Multi-Channel Communication**: WhatsApp and Telegram bot support
- **WhatsApp Connection Sharing**: QR code plus barcode payload for external connection flows
- **Google AI Studio First**: Every agent routes through the same Gemini-backed reasoning engine
- **Autonomous Agents**: Smart agent framework that routes queries intelligently
  - Chat Agent - General conversation
  - Research Agent - Knowledge base search
  - Memory Agent - User memory management
  - Workflow Agent - Task automation
  - Planner Agent - Complex task breakdown
- **Custom Agents & Tools**: Extensible framework for custom agents (Summary, Analysis, Recommendation, Validation, Integration)
- **Memory System**: Short-term and long-term memory with semantic search
- **Knowledge Management**: PDF, DOCX, TXT, and Markdown upload support
- **Workflow Automation**: Scheduled tasks, reminders, and notifications
- **Admin Dashboard**: Modern web interface for management
- **Security**: JWT authentication, rate limiting, encryption
- **Monitoring**: Structured logging, error tracking, metrics
- **Scalability**: Horizontal scaling with Redis and PostgreSQL

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#-features)
- [Documentation](#-documentation)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)

## ⚡ Quick Start

**Get your AI Bot running in 5 minutes!**

See: **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)**

```bash
# Clone
git clone https://github.com/yourusername/ai-bot-platform.git
cd ai-bot-platform

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your Google AI key and Telegram token

# Test
python local_test.py

# Deploy
git push origin main
# Then deploy to Railway, Heroku, or AWS (see guides)
```

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)** | ⚡ Get running in 5 minutes |
| **[GITHUB_SETUP_COMPLETE.md](GITHUB_SETUP_COMPLETE.md)** | 📚 Complete setup guide |
| **[GITHUB_HOSTING_GUIDE.md](GITHUB_HOSTING_GUIDE.md)** | 🚀 Deploy to production |
| **[CUSTOM_AGENTS_TOOLS_GUIDE.md](CUSTOM_AGENTS_TOOLS_GUIDE.md)** | 🛠️ Extend functionality |
| **[DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md)** | 🌐 Platform-specific setup |

## 🔧 Requirements

- Python 3.12, 3.13, or 3.14
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose
- Node.js 18+ (for dashboard)

> The project now supports Python 3.14 in this environment; install dependencies with the current interpreter to avoid version mismatches.

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-bot-platform.git
   cd ai-bot-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database**
   ```bash
   alembic upgrade head
   ```

6. **Start Redis**
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

7. **Run development server**
   ```bash
   uvicorn src.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Using Docker Compose

```bash
docker-compose up -d
```

This starts:
- FastAPI backend on port 8000
- PostgreSQL database
- Redis cache
- Admin dashboard on port 3000

## 🏗️ Architecture

### Project Structure

```
ai-bot-platform/
├── src/
│   ├── api/                 # FastAPI routes and middleware
│   ├── bot/                 # Bot integrations (Telegram, WhatsApp)
│   ├── ai/                  # AI agent framework
│   ├── memory/              # Memory systems
│   ├── database/            # Database models and migrations
│   ├── workflows/           # Workflow automation
│   ├── security/            # Authentication and authorization
│   ├── monitoring/          # Logging and monitoring
│   └── main.py              # Application entry point
├── dashboard/               # React/Next.js admin dashboard
├── tests/                   # Unit and integration tests
├── docker/                  # Docker configurations
├── .github/workflows/       # CI/CD pipelines
└── docs/                    # Documentation
```

### Core Components

1. **API Layer**: FastAPI with async support
2. **Bot Integrations**: Telegram and WhatsApp handlers
3. **AI System**: LangGraph-based agent framework
4. **Memory**: PostgreSQL + ChromaDB for semantic search
5. **Database**: SQLAlchemy ORM with Alembic migrations
6. **Security**: JWT authentication and authorization
7. **Monitoring**: Structured logging and Prometheus metrics

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all available configuration options.

For local development, copy `.env.example` to `.env` and fill in at least:

```bash
GOOGLE_API_KEY=your-google-ai-studio-key
TELEGRAM_BOT_TOKEN=your-telegram-token
SECRET_KEY=your-production-secret
```

Without `GOOGLE_API_KEY`, the app will still start, but responses will fall back to a limited message until the key is configured.

Key configurations:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
TELEGRAM_BOT_TOKEN=...
WHATSAPP_ACCESS_TOKEN=...
```

### Database Setup

1. **Create database**
   ```bash
   createdb aibot_db
   ```

2. **Run migrations**
   ```bash
   alembic upgrade head
   ```

3. **Create initial data**
   ```bash
   python scripts/init_db.py
   ```

## 📚 API Documentation

Interactive API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

### Key Endpoints

```
# Auth
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

# Messages
GET    /api/v1/messages/{user_id}
POST   /api/v1/messages/send
GET    /api/v1/messages/{message_id}

# Memory
GET    /api/v1/memory/{user_id}
POST   /api/v1/memory/store
GET    /api/v1/memory/search

# Documents
POST   /api/v1/documents/upload
GET    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}

# Workflows
GET    /api/v1/workflows
POST   /api/v1/workflows/create
PUT    /api/v1/workflows/{workflow_id}
DELETE /api/v1/workflows/{workflow_id}

# Admin
GET    /api/v1/admin/users
GET    /api/v1/admin/analytics
GET    /api/v1/admin/health
```

## 🤖 Telegram Commands

```
/start      - Start the bot
/help       - Show help menu
/memory     - View your memories
/clear      - Clear conversation history
/status     - Bot status
/search     - Search knowledge base
/tasks      - View active tasks
/settings   - User preferences
```

## 📦 Deployment

### Docker Deployment

```bash
# Build image
docker build -t ai-bot-platform:latest -f docker/Dockerfile .

# Run container
docker run -d \
  --name ai-bot \
  -p 8000:8000 \
  --env-file .env \
  ai-bot-platform:latest
```

### Cloud Platforms

#### Heroku
```bash
git push heroku main
```

#### Railway
```bash
railway up
```

#### Render
1. Connect GitHub repo
2. Create web service
3. Add environment variables
4. Deploy
5. Open `/health` and `/ready` on the live URL and confirm they return success.

### WhatsApp Connection Flow

The WhatsApp QR endpoints can be used to start a live connection session and retrieve both QR and barcode payloads for external access:

1. Call `POST /api/v1/whatsapp-qr/start-connection`
2. Open the returned QR or barcode data in a viewer, or use the absolute `connect_url`
3. Scan the QR with WhatsApp Linked Devices
4. Use the status endpoint to confirm the session is authenticated

#### AWS EC2
See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run specific test suite
```bash
pytest tests/unit/
pytest tests/integration/
```

### With coverage
```bash
pytest --cov=src --cov-report=html
```

### Target: 90%+ test coverage

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Prometheus Metrics
```bash
curl http://localhost:9090/metrics
```

### Logs
```bash
# View application logs
docker logs ai-bot

# Stream logs
docker logs -f ai-bot
```

## 🔒 Security

- JWT token-based authentication
- Password hashing with bcrypt
- Rate limiting per user/IP
- Prompt injection prevention
- SQL injection protection
- CSRF protection
- Encryption at rest and in transit
- Audit logs for all actions

## 🛠️ Development

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

- AI Bot Team

## 🙏 Acknowledgments

- LangChain and LangGraph teams
- FastAPI community
- OpenAI and Google AI
- Telegram and WhatsApp

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/ai-bot-platform/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ai-bot-platform/discussions)
- Email: support@aibot.com

---

**Made with ❤️ by the AI Bot Team**
