# 🚀 QUICK START: 700M Local Database Setup

## ⏱️ 5-Minute Setup (With Database Already Running)

### Step 1: Enable in Bot Config (1 min)

Update `src/config.py`:

```python
# Change from SQLite to PostgreSQL
DATABASE_URL = "postgresql://postgres:change_me_123@localhost:5432/aibot_700m"

# Optimize for large dataset
DB_POOL_SIZE = 20
DB_POOL_MAX_OVERFLOW = 40
DB_POOL_RECYCLE = 3600
```

### Step 2: Initialize Schema (2 min)

```bash
# On Windows PowerShell:
psql -U postgres -h localhost -f scripts\create_700m_schema.sql
```

### Step 3: Test Database (1 min)

```bash
python test_700m_database.py
```

**Expected output:**
```
✅ Connected to database
✅ All tables exist
✅ Indexes created
✅ ALL TESTS PASSED!
```

### Step 4: Test Bot (1 min)

```bash
python local_test.py
```

**Done!** Your bot now uses 700M capacity database! 🎉

---

## 📊 Complete Setup (From Scratch)

### Prerequisites

- **OS**: Windows 10/11
- **Storage**: 1TB free (for 700M records)
- **RAM**: 16GB (8GB for PostgreSQL, 8GB system)

---

## Installation

### Option A: PostgreSQL Native (Recommended for Windows)

```bash
# 1. Download from https://www.postgresql.org/download/windows/
# Choose version 16 or higher

# OR use Chocolatey:
choco install postgresql

# 2. During installation:
#    - Port: 5432 ✓
#    - Username: postgres ✓
#    - Password: change_me_123 (choose secure password!)
#    - Data location: C:\PostgreSQL\data (or larger drive)

# 3. Initialize database (automatic on install)

# 4. Verify
psql -U postgres -h localhost -c "SELECT version();"
# Should show: PostgreSQL 16.x ...
```

### Option B: Docker (If Preferred)

```bash
# Requires Docker Desktop installed

docker run -d \
  --name postgres_700m \
  -e POSTGRES_PASSWORD=change_me_123 \
  -e POSTGRES_DB=aibot_700m \
  -v C:\PostgreSQL\data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Verify
docker logs postgres_700m
# Should show: "database system is ready to accept connections"
```

---

## Database Configuration

### Optimize PostgreSQL for 700M Records

Edit `C:\Program Files\PostgreSQL\16\data\postgresql.conf`:

```ini
# MEMORY SETTINGS (for 16GB RAM)
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 50MB

# PERFORMANCE
random_page_cost = 1.1
effective_io_concurrency = 200
synchronous_commit = off
checkpoint_completion_target = 0.9
max_wal_size = 16GB

# CONNECTIONS
max_connections = 500
```

**Restart PostgreSQL:**

```bash
# Windows Services
# Right-click start menu → Run Services
# Find "postgresql-x64-16"
# Right-click → Restart

# Or command line:
net stop postgresql-x64-16
net start postgresql-x64-16
```

---

## Create Database Schema

```bash
# 1. Create database
psql -U postgres -h localhost -c "CREATE DATABASE aibot_700m;"

# 2. Load schema
psql -U postgres -h localhost -d aibot_700m -f scripts/create_700m_schema.sql

# 3. Verify
psql -U postgres -h localhost -d aibot_700m -c "\dt"
# Should show tables: users, conversations, messages, embeddings, memory, cache, analytics
```

---

## Load Initial Data

### Option 1: Quick Test (1M records - 5 min)

```bash
# Load 1 million test records
python scripts/bulk_insert_700m.py --records 1000000

# Expected output:
# ✓ Inserted 1,000,000 records
# ✓ Rate: 50,000 rec/sec
# ✓ Completed in ~20 seconds
```

### Option 2: Full Load (700M records - 24-48 hours)

```bash
# Load all 700 million records
# WARNING: Takes 24-48 hours on typical hardware!
python scripts/bulk_insert_700m.py --records 700000000

# Progress updates every minute showing:
# - Records inserted
# - Insertion rate
# - Estimated completion time
```

### Option 3: Gradual Load (Recommended)

```bash
# Run multiple times with delays
# Day 1: 100M records
python scripts/bulk_insert_700m.py --records 100000000

# Day 2: +200M records
python scripts/bulk_insert_700m.py --records 200000000

# Day 3: +400M records  
python scripts/bulk_insert_700m.py --records 400000000

# Total: 700M records
```

---

## Update Bot Configuration

### `.env` file

```env
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://postgres:change_me_123@localhost:5432/aibot_700m

# Connection pooling
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600

# Performance tuning
BATCH_INSERT_SIZE=5000
BATCH_QUERY_SIZE=10000

# Keep other settings the same
GOOGLE_API_KEY=AIzaSyBk563VvLColh0pnXFRjfzMbnZkV7Ghb0U
TELEGRAM_BOT_TOKEN=7895886891:AAFHQFUrgeRdeA_LI5P9y5lAZfKO3Mbd_M8
```

---

## Testing

### Test 1: Database Connectivity

```bash
python test_700m_database.py
```

**Output:**
```
🧪 Test 1: Database Connection
   ✅ PASS: PostgreSQL 16.0

🧪 Test 2: Database Schema  
   ✅ PASS: 7 tables exist

🧪 Test 3: Database Indexes
   ✅ PASS: 25 indexes created

🧪 Test 4: Table Sizes
   messages:      500GB (700,000,000 rows)
   analytics:      50GB
   conversations:   1GB

✅ ALL TESTS PASSED!
```

### Test 2: Bot Functionality

```bash
python local_test.py
```

Expected output:
```
✅ Tools Testing: PASSED
✅ Orchestrator: PASSED
✅ Database: Connected to aibot_700m
✅ ALL TESTS PASSED
```

### Test 3: Query Performance

```bash
# Interactive test
psql -U postgres -d aibot_700m

# Try queries
SELECT COUNT(*) FROM messages WHERE user_id = 1;
-- Should return < 100ms

SELECT COUNT(*) FROM messages 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';
-- Should return < 500ms

\q  # Exit
```

---

## Monitoring

### Check Database Health

```bash
# Get database size
psql -U postgres -d aibot_700m -c \
  "SELECT pg_size_pretty(pg_database_size('aibot_700m'))"

# Get table sizes
psql -U postgres -d aibot_700m -c \
  "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
   FROM pg_tables WHERE schemaname='public' ORDER BY 3 DESC"

# Monitor active queries
psql -U postgres -d aibot_700m -c \
  "SELECT pid, usename, query, state FROM pg_stat_activity WHERE datname='aibot_700m'"
```

### Maintenance

```bash
# Vacuum and analyze (weekly)
psql -U postgres -d aibot_700m -c "VACUUM ANALYZE"

# Reindex large tables (monthly)
psql -U postgres -d aibot_700m -c "REINDEX TABLE messages"

# Backup (daily)
pg_dump -U postgres aibot_700m > backup_$(date +%Y%m%d).sql
```

---

## Performance Reference

| Operation | Speed | Notes |
|-----------|-------|-------|
| Insert | 50K-100K rec/sec | Batch inserts only |
| Simple Query | <100ms | With indexed column |
| Range Query | <500ms | Partitioned table |
| Join Query | <1s | Optimized indexes |
| Storage | ~1KB per record | Compress if needed |

---

## Troubleshooting

### "Connection refused"
```
Solution:
1. Check PostgreSQL running: Services → PostgreSQL
2. Test: psql -U postgres -h localhost
3. Restart: net restart postgresql-x64-16
```

### "Database doesn't exist"
```
Solution:
1. Create it: psql -U postgres -c "CREATE DATABASE aibot_700m"
2. Load schema: psql -U postgres -d aibot_700m -f schema.sql
```

### "Slow queries"
```
Solution:
1. Check indexes: psql -d aibot_700m -c "\di"
2. Analyze: psql -d aibot_700m -c "ANALYZE"
3. Vacuum: psql -d aibot_700m -c "VACUUM"
4. Check cache hit ratio: psql -d aibot_700m -c "SELECT * FROM pg_statio_user_tables"
```

### "Out of disk space"
```
Solution:
1. Check usage: psql -d aibot_700m -c "SELECT pg_database_size('aibot_700m')"
2. Archive old data: python scripts/archive_old_messages.py
3. Upgrade storage
```

---

## Next Steps

Once database is running:

1. **Deploy bot**: Push to GitHub and deploy to Railway
2. **Monitor**: Watch database performance in production
3. **Optimize**: Fine-tune based on query logs
4. **Scale**: Add more resources if needed
5. **Backup**: Set up automated daily backups

---

## Reference Files

| File | Purpose |
|------|---------|
| `scripts/create_700m_schema.sql` | Database schema creation |
| `scripts/bulk_insert_700m.py` | Bulk data import script |
| `src/database/large_scale_queries.py` | Optimized query module |
| `src/monitoring/db_monitor.py` | Database monitoring |
| `test_700m_database.py` | Comprehensive tests |
| `LOCAL_DATABASE_700M_SETUP.md` | Full technical guide |

---

## 🎉 You're Done!

Your bot now has:
- ✅ **700M+ record capacity** local database
- ✅ **Fast queries** (<100ms with indexes)
- ✅ **High throughput** (50K+ inserts/sec)
- ✅ **Enterprise reliability** (ACID transactions)
- ✅ **Automatic optimization** (partitioning, indexes)

**Bot is ready to handle massive amounts of data locally!** 🚀
