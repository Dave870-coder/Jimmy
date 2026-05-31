# Deployment Guide

## Cloud Deployment Options

### 1. Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create ai-bot-platform

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Add Redis addon
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set TELEGRAM_BOT_TOKEN=...

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head
```

### 2. Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Create project
railway init

# Link to GitHub
railway connect

# Set environment variables in dashboard

# Deploy
git push

# Run migrations
railway run alembic upgrade head
```

### 3. Render

1. Connect GitHub repository
2. Create Web Service
3. Set environment variables
4. Configure start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database
6. Add Redis cache
7. Deploy

### 4. DigitalOcean App Platform

```bash
# Create app.yaml
# Push to GitHub
# Connect DigitalOcean App Platform to GitHub
# Deploy
```

### 5. AWS (EC2)

```bash
# Launch EC2 instance
# Connect via SSH
ssh -i key.pem ubuntu@<public-ip>

# Install Docker
sudo apt update && sudo apt install docker.io -y

# Clone repository
git clone <repo-url>
cd ai-bot-platform

# Create .env file
nano .env

# Start with Docker Compose
sudo docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

### 6. Kubernetes

```bash
# Create deployment manifest
kubectl apply -f k8s/deployment.yaml

# Create service
kubectl apply -f k8s/service.yaml

# Scale replicas
kubectl scale deployment ai-bot-platform --replicas=3

# Check status
kubectl get pods
kubectl logs <pod-name>
```

## Nginx Configuration

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/static/;
    }
}
```

## SSL/TLS Certificate

```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## Monitoring & Logging

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-bot-platform'
    static_configs:
      - targets: ['localhost:9090']
```

### ELK Stack Setup

```bash
docker-compose up elasticsearch logstash kibana
```

### Sentry Error Tracking

```python
# In .env
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

## Backup Strategy

### PostgreSQL Backup

```bash
# Daily backup
pg_dump aibot_db > backup_$(date +%Y%m%d).sql

# Automated with cron
0 2 * * * pg_dump aibot_db | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Redis Backup

```bash
# Enable persistence
appendonly yes
appendfsync everysec
```

## Performance Optimization

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM messages WHERE user_id = '...';

-- Add indexes
CREATE INDEX idx_messages_user_date ON messages(user_id, created_at DESC);
```

### Caching Strategy

```python
# Redis caching
@cache(ttl=3600)
async def get_user_memories(user_id: str):
    return await db.get_memories(user_id)
```

### Load Balancing

Use Nginx or HAProxy to distribute traffic across multiple API instances.

## Rollback Procedure

```bash
# Revert to previous version
git revert <commit-hash>
git push

# Rollback database migration
alembic downgrade -1

# Restart service
docker-compose restart api
```

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
psql -U aibot_user -d aibot_db -c "SELECT 1;"

# Redis health
redis-cli ping
```

## Scaling Considerations

1. **Horizontal Scaling**: Add more API instances behind load balancer
2. **Database Scaling**: Use read replicas for PostgreSQL
3. **Caching**: Increase Redis capacity
4. **Message Queue**: Add RabbitMQ for async tasks
5. **CDN**: Use CloudFront for static assets

## Disaster Recovery

1. Automated backups every 6 hours
2. Keep backups for 30 days
3. Monthly restore test
4. Document recovery procedure
5. Have runbook ready
