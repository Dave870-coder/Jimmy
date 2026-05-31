# API Reference

## Authentication

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201)**
```json
{
  "id": "user-uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

**Response (200)**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

## Messages

### Send Message

```http
POST /api/v1/messages/send
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "Hello AI!",
  "message_type": "text",
  "source": "api"
}
```

**Response (200)**
```json
{
  "id": "message-uuid",
  "user_id": "user-uuid",
  "content": "Hello AI!",
  "response": "Hi! How can I help you today?",
  "ai_model": "gpt-4-turbo-preview",
  "created_at": "2024-01-01T00:00:00"
}
```

### Get Messages

```http
GET /api/v1/messages/{user_id}?limit=50
Authorization: Bearer {access_token}
```

**Response (200)**
```json
[
  {
    "id": "message-uuid",
    "user_id": "user-uuid",
    "content": "Hello AI!",
    "response": "Hi! How can I help?",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

## Memory

### Store Memory

```http
POST /api/v1/memory/store
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Important Note",
  "content": "This is a memory to store",
  "memory_type": "fact",
  "category": "general",
  "importance": 8,
  "tags": "important,note"
}
```

**Response (200)**
```json
{
  "id": "memory-uuid",
  "user_id": "user-uuid",
  "title": "Important Note",
  "content": "This is a memory to store",
  "memory_type": "fact",
  "importance": 8,
  "created_at": "2024-01-01T00:00:00"
}
```

### Search Memories

```http
POST /api/v1/memory/search?user_id={user_id}&query=important&limit=10
Authorization: Bearer {access_token}
```

**Response (200)**
```json
[
  {
    "id": "memory-uuid",
    "user_id": "user-uuid",
    "title": "Important Note",
    "content": "This is a memory to store",
    "memory_type": "fact",
    "importance": 8,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Get User Memories

```http
GET /api/v1/memory/{user_id}?limit=100
Authorization: Bearer {access_token}
```

**Response (200)**
```json
[
  {
    "id": "memory-uuid",
    "user_id": "user-uuid",
    "title": "Important Note",
    "memory_type": "fact",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

## Admin

### Get Users

```http
GET /api/v1/admin/users?limit=50&offset=0
Authorization: Bearer {admin_token}
```

### Get Analytics

```http
GET /api/v1/admin/analytics?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {admin_token}
```

**Response (200)**
```json
{
  "active_users": 150,
  "total_messages": 5000,
  "average_response_time": 0.45
}
```

### Health Check

```http
GET /api/v1/admin/health
Authorization: Bearer {admin_token}
```

**Response (200)**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email",
      "type": "value_error"
    }
  ]
}
```

### 429 Too Many Requests

```json
{
  "detail": "Too many requests"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Rate limit: 100 requests per hour per user
- Rate limit headers:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 99
  - `X-RateLimit-Reset`: 1609459200
