# 🔧 Jimmy Bot Dashboard - Configuration Guide

## Environment Variables

### For Dashboard (GitHub Pages)

```env
# .env.local (local development)
NEXT_PUBLIC_API_BASE=http://localhost:8000

# For GitHub deployment, set in repository settings:
# Settings > Secrets and variables > Actions > New repository secret
NEXT_PUBLIC_API_BASE=https://your-bot-url.onrender.com
```

### For Backend (FastAPI)

```env
# .env (local)
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./data/bot.db
GOOGLE_API_KEY=your-google-ai-key
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
PUBLIC_BASE_URL=http://localhost:8000
WHATSAPP_ACCESS_TOKEN=optional
OPENAI_API_KEY=optional

# .env.production (Render/Railway)
APP_ENV=production
DEBUG=False
SECRET_KEY=strong-random-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
GOOGLE_API_KEY=your-google-ai-key
TELEGRAM_BOT_TOKEN=your-telegram-token
PUBLIC_BASE_URL=https://your-deployed-url.onrender.com
```

---

## API Endpoints Required

The dashboard requires these endpoints to be available on your backend:

### Analytics Endpoints
```
GET /api/v1/admin/analytics
  Response: {
    active_users: number,
    total_users: number,
    total_messages: number,
    total_workflows: number,
    average_response_time: number,
    generated_at: string
  }

GET /api/v1/admin/analytics/messages?days=7
  Response: {
    dates: string[],
    counts: number[]
  }

GET /api/v1/admin/analytics/performance
  Response: {
    avg_response_time: number,
    p95_response_time: number,
    p99_response_time: number,
    error_rate: number,
    cache_hit_rate: number
  }
```

### User Management Endpoints
```
GET /api/v1/admin/users?limit=50&offset=0
  Response: [
    {
      id: string,
      username: string,
      email: string,
      is_active: boolean,
      created_at: string,
      last_seen: string,
      message_count: number
    }
  ]

GET /api/v1/admin/users/{user_id}
  Response: { user details }

PUT /api/v1/admin/users/{user_id}
  Body: { is_active: boolean, role: string }

DELETE /api/v1/admin/users/{user_id}
```

### Message History Endpoints
```
GET /api/v1/admin/messages?limit=50&offset=0&user_id=optional
  Response: [
    {
      id: string,
      user_id: string,
      content: string,
      sender: "user" | "bot",
      created_at: string,
      channel: "telegram" | "whatsapp" | "web"
    }
  ]

GET /api/v1/admin/conversations/{conversation_id}/messages
  Response: [ messages array ]
```

### Settings Endpoints
```
POST /api/v1/admin/settings
  Body: {
    telegram_bot_token: string,
    google_api_key: string,
    openai_api_key: string,
    whatsapp_access_token: string,
    telegram_webhook_secret: string,
    public_base_url: string,
    database_url: string
  }
  Response: { message: "Settings saved successfully" }

GET /api/v1/admin/integrations
  Response: {
    telegram_configured: boolean,
    telegram_webhook_url: string,
    whatsapp_configured: boolean,
    google_ai_configured: boolean
  }
```

### Health Endpoints
```
GET /health
  Response: { status: "ok" }

GET /ready
  Response: { ready: true, checks: {...} }
```

---

## Dashboard Component Configuration

### Home Component
- Displays summary cards
- Shows real-time analytics
- Latest 6 users
- Integration status
- Auto-refresh every 10 seconds

### Analytics Component
- Message volume chart (7 days)
- User growth trend
- Response time histogram
- Workflow completion rates
- Export buttons

### Users Component
- Paginated user list (50 per page)
- Search by username/email
- Filter by active status
- User activity timeline
- Bulk operations (block/unblock)

### Messages Component
- Full message history
- Search by content
- Filter by date range
- Channel selector
- User thread view
- Export to JSON/CSV

### Performance Component
- Real-time metrics
- API response time chart
- Error rate tracking
- Cache efficiency display
- Database performance stats
- System resource usage

---

## API Connection Patterns

### Auto-Reconnect Logic
```typescript
// Built into dashboard
// Automatically retries failed requests with exponential backoff
// Max 3 retries with 1s, 2s, 4s delays
// Shows connection status in UI
```

### Real-Time Updates
```typescript
// Auto-refresh intervals:
// Analytics: 10 seconds
// Users: 30 seconds
// Messages: 5 seconds (when viewing)
// Performance: 3 seconds
```

### Error Handling
```typescript
// Graceful degradation:
// - Missing API key? Show empty state
// - API timeout? Show last cached data
// - Network error? Show offline mode
// - 401 Unauthorized? Show login prompt
```

---

## CORS Configuration

Your backend must allow requests from:
- `http://localhost:3000` (local development)
- `https://Dave870-coder.github.io` (GitHub Pages production)

Add to your FastAPI app:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://Dave870-coder.github.io",
        "https://Dave870-coder.github.io/Jimmy/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Optimization

### Dashboard Caching
```typescript
// Local storage caching:
// - Analytics cached for 30 seconds
// - User list cached for 60 seconds
// - Settings cached for 5 minutes
// - Automatic invalidation on mutation
```

### API Rate Limiting
```typescript
// Built-in rate limiting:
// Dashboard respects backend rate limits
// Automatic backoff on 429 responses
// Local request deduplication
```

### Image Optimization
```typescript
// Chart images optimized
// SVG rendering preferred
// Lazy loading for metrics
// Progressive enhancement
```

---

## Monitoring & Logging

### Browser Console Logs
Enable by setting in .env:
```env
NEXT_DEBUG=1
```

### Backend Integration Logs
```
All API calls logged with:
- Request method and path
- Response status
- Execution time
- Error details (if any)
```

---

## Testing Configuration

### Unit Tests
```bash
cd dashboard
npm test
```

### Integration Tests
```bash
# Requires running backend
npm run test:integration
```

### E2E Tests
```bash
# Full dashboard workflow testing
npm run test:e2e
```

---

## Deployment Configuration

### GitHub Pages
- Automatically deployed on push to main
- Static export via Next.js
- No build configuration needed
- Auto-refresh on release

### Custom Domain
Add to GitHub repository settings:
- Settings > Pages > Custom domain
- Point DNS to GitHub Pages servers
- Update `NEXT_PUBLIC_API_BASE` for custom domain

---

## Security Configuration

### API Security
```typescript
// HTTPS enforced
// CORS restrictions applied
// Request signing (if needed)
// Rate limiting per endpoint
```

### Data Protection
```typescript
// Sensitive data not cached locally
// API keys never stored in browser
// Settings form auto-clears after save
// Tokens in sessionStorage (cleared on close)
```

---

## Advanced Configuration

### Custom Analytics
Edit dashboard/app/components/analytics.tsx:
```typescript
// Add custom metrics
// Modify chart types
// Add new filters
// Export different formats
```

### Custom User Fields
Extend dashboard/app/types/user.ts:
```typescript
// Add custom properties
// Extend validation rules
// Customize display columns
```

---

## Support & Troubleshooting

See [DASHBOARD_TROUBLESHOOTING.md](DASHBOARD_TROUBLESHOOTING.md) for common issues and solutions.
