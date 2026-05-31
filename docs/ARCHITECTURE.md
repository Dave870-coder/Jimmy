# Architecture Guide

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  (Telegram, WhatsApp, Web, Mobile)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
│  (FastAPI, Rate Limiting, Auth, CORS)                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Application Layer                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ AI Agent System (LangGraph)                       │   │
│  │ - Chat Agent                                      │   │
│  │ - Research Agent                                  │   │
│  │ - Memory Agent                                    │   │
│  │ - Workflow Agent                                  │   │
│  │ - Planner Agent                                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Bot Integration Layer                             │   │
│  │ - Telegram Handler                                │   │
│  │ - WhatsApp Handler                                │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Service Layer                                     │   │
│  │ - Message Service                                 │   │
│  │ - Memory Service                                  │   │
│  │ - Workflow Service                                │   │
│  │ - Document Service                                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ PostgreSQL                                        │   │
│  │ - Users, Messages, Memories                       │   │
│  │ - Workflows, Tasks, Feedback                      │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ChromaDB (Vector DB)                              │   │
│  │ - Embeddings, Semantic Search                      │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Redis Cache                                       │   │
│  │ - Session Store, Temporary Data                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (FastAPI)

**Location**: `src/api/`

- **Routes**: Authentication, Messages, Memory, Admin, Bots
- **Middleware**: Logging, Rate Limiting, CORS, Error Handling
- **Dependencies**: User authentication, database sessions

### 2. AI Agent System

**Location**: `src/ai/`

**Agents**:
- **Chat Agent**: Conversational responses
- **Research Agent**: Knowledge base search
- **Memory Agent**: Store/retrieve memories
- **Workflow Agent**: Task automation
- **Planner Agent**: Break down complex requests
- **Tool Agent**: External API calls

**Communication Flow**:
1. User input → Agent Orchestrator
2. Route to appropriate agent(s)
3. Process through LLM
4. Store results in memory/database
5. Return response

### 3. Bot Integration Layer

**Location**: `src/bot/`

**Telegram Bot**:
- Command handlers (/start, /help, /memory, etc.)
- Message routing to agents
- Session management

**WhatsApp Bot**:
- Webhook handling
- Message sending/receiving
- Media support (images, documents)

### 4. Memory System

**Location**: `src/memory/`

**Components**:
- **Memory Manager**: Store and retrieve memories
- **Vector Database**: ChromaDB for semantic search
- **Embedding Generation**: Sentence transformers

**Memory Types**:
- Short-term: Recent messages (Redis)
- Long-term: User preferences, facts (PostgreSQL + ChromaDB)

### 5. Database Layer

**Location**: `src/database/`

**Tables**:
- Users: User accounts and profiles
- Messages: Conversation history
- Memories: User memories with embeddings
- Documents: Uploaded files
- Workflows: Automation workflows
- Tasks: Task queue
- Feedback: User ratings

**Features**:
- Async SQLAlchemy ORM
- Alembic migrations
- Connection pooling
- Query optimization

### 6. External Integrations

**AI Models**:
- OpenAI GPT-4
- Google Gemini
- Ollama (local LLM)

**Communication**:
- Telegram Bot API
- WhatsApp Business API
- Twilio (optional)

## Design Patterns

### 1. Repository Pattern

```python
class UserRepository:
    async def get_by_id(self, user_id: str):
        pass
    
    async def create(self, user_data: dict):
        pass
```

### 2. Dependency Injection

```python
async def get_current_user(token: str) -> dict:
    return verify_token(token)

@app.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    pass
```

### 3. Service Layer

```python
class MessageService:
    async def send_message(self, user_id, content):
        message = await self.agent_orchestrator.process(user_id, content)
        await self.db.store_message(user_id, content, message)
        return message
```

### 4. Factory Pattern

```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str):
        agents = {
            "chat": ChatAgent(),
            "research": ResearchAgent(),
        }
        return agents.get(agent_type)
```

## Data Flow

### User Message Flow

```
User Input (Telegram/WhatsApp)
    ↓
Bot Handler
    ↓
Message Storage (PostgreSQL)
    ↓
Agent Orchestrator
    ↓
Route to appropriate agent
    ↓
Generate response (via LLM)
    ↓
Store memory/embeddings (PostgreSQL + ChromaDB)
    ↓
Cache response (Redis)
    ↓
Send response to user
```

### Knowledge Base Search

```
User Query
    ↓
Generate Embedding
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve relevant documents
    ↓
Inject into LLM context
    ↓
Generate informed response
```

## Security Architecture

### 1. Authentication

- JWT tokens with HS256
- Refresh token rotation
- Token expiration (24 hours)

### 2. Authorization

- Role-based access control (RBAC)
- Resource-level permissions
- API scopes

### 3. Data Protection

- Password hashing (bcrypt)
- Encryption at rest
- HTTPS/TLS in transit

### 4. Input Validation

- Pydantic schemas
- Prompt injection prevention
- SQL injection protection

### 5. Rate Limiting

- Per-user limits
- Per-IP limits
- Sliding window algorithm

## Performance Optimization

### 1. Caching Strategy

```
User Preferences → Redis (1 hour TTL)
Popular Memories → Redis (24 hour TTL)
Search Results → Redis (30 min TTL)
```

### 2. Database Optimization

- Connection pooling (20 connections)
- Query indexing
- Prepared statements
- Batch operations

### 3. Async Architecture

- All I/O operations are async
- Non-blocking request handling
- Concurrent request processing

### 4. Vector Search Optimization

- Embedding caching
- Batch indexing
- Similarity threshold filtering

## Scaling Considerations

### Horizontal Scaling

1. **API Servers**: Run multiple instances behind load balancer
2. **Workers**: Async task queue (Celery) for background jobs
3. **Cache**: Distributed Redis cluster

### Database Scaling

1. **Read Replicas**: For read-heavy operations
2. **Sharding**: User-based sharding for large datasets
3. **Connection Pooling**: PgBouncer for connection management

### Monitoring at Scale

1. **Metrics**: Prometheus for system metrics
2. **Logging**: ELK stack for centralized logging
3. **Tracing**: Distributed tracing for debugging

## Disaster Recovery

- Automated daily backups
- Backup retention: 30 days
- Recovery time objective (RTO): 1 hour
- Recovery point objective (RPO): 1 hour
