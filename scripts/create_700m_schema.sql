-- ============================================
-- OPTIMIZED SCHEMA FOR 700M RECORDS
-- ============================================
-- This schema uses table partitioning, proper indexing,
-- and optimization for storing massive amounts of data

-- Create database
CREATE DATABASE IF NOT EXISTS aibot_700m;
\c aibot_700m

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telegram_id BIGINT UNIQUE,
    whatsapp_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================
-- 2. CONVERSATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'
) PARTITION BY RANGE (created_at);

-- Create quarterly partitions
DO $$
DECLARE
    quarter_start DATE;
    quarter_end DATE;
BEGIN
    FOR year IN 2023..2026 LOOP
        FOR q IN 1..4 LOOP
            quarter_start := make_date(year, (q-1)*3+1, 1);
            quarter_end := quarter_start + INTERVAL '3 months';
            
            EXECUTE format('CREATE TABLE IF NOT EXISTS conversations_%s_%s PARTITION OF conversations 
                           FOR VALUES FROM (%L) TO (%L)',
                year, q, quarter_start, quarter_end);
        END LOOP;
    END LOOP;
END $$;

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);

-- ============================================
-- 3. MESSAGES TABLE (700M+ records here)
-- ============================================
-- Partitioned by date for better performance
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for 3 years
DO $$
DECLARE
    month_start DATE;
    month_end DATE;
BEGIN
    FOR year IN 2024..2026 LOOP
        FOR month IN 1..12 LOOP
            month_start := make_date(year, month, 1);
            month_end := month_start + INTERVAL '1 month';
            
            EXECUTE format('CREATE TABLE IF NOT EXISTS messages_%s_%02s PARTITION OF messages 
                           FOR VALUES FROM (%L) TO (%L)',
                year, month, month_start, month_end);
        END LOOP;
    END LOOP;
END $$;

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_is_deleted ON messages(is_deleted) WHERE is_deleted = false;

-- Set table for large dataset optimization
ALTER TABLE messages SET (fillfactor = 70);

-- ============================================
-- 4. MESSAGE EMBEDDINGS (Vector search)
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL UNIQUE REFERENCES messages(id) ON DELETE CASCADE,
    embedding vector(384),  -- Using 384-dim embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_message_id ON embeddings(message_id);
-- Vector index for similarity search (may take time to create)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);

-- ============================================
-- 5. USER MEMORY (Fast access)
-- ============================================
CREATE TABLE IF NOT EXISTS memory (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(500) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_memory_user_id ON memory(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key);
CREATE INDEX IF NOT EXISTS idx_memory_gin_value ON memory USING GIN(value);  -- For JSON search

-- ============================================
-- 6. SESSION CACHE (Hot data)
-- ============================================
CREATE TABLE IF NOT EXISTS cache (
    id BIGSERIAL PRIMARY KEY,
    cache_key VARCHAR(500) UNIQUE NOT NULL,
    cache_value JSONB NOT NULL,
    ttl INTERVAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON cache(expires_at);

-- ============================================
-- 7. ANALYTICS (Usage tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for analytics
DO $$
DECLARE
    month_start DATE;
    month_end DATE;
BEGIN
    FOR year IN 2024..2026 LOOP
        FOR month IN 1..12 LOOP
            month_start := make_date(year, month, 1);
            month_end := month_start + INTERVAL '1 month';
            
            EXECUTE format('CREATE TABLE IF NOT EXISTS analytics_%s_%02s PARTITION OF analytics 
                           FOR VALUES FROM (%L) TO (%L)',
                year, month, month_start, month_end);
        END LOOP;
    END LOOP;
END $$;

CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);

-- ============================================
-- 8. MATERIALIZED VIEWS FOR FAST STATS
-- ============================================

-- User statistics view
CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT c.id) as conversation_count,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at,
    SUM(m.tokens_used) as total_tokens_used
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN messages m ON u.id = m.user_id AND m.is_deleted = false
GROUP BY u.id, u.username;

CREATE INDEX IF NOT EXISTS idx_user_stats_id ON user_stats(id);
CREATE INDEX IF NOT EXISTS idx_user_stats_message_count ON user_stats(message_count DESC);

-- Conversation statistics view
CREATE MATERIALIZED VIEW IF NOT EXISTS conversation_stats AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    COUNT(m.id) as message_count,
    COUNT(DISTINCT CASE WHEN m.role='user' THEN 1 END) as user_messages,
    COUNT(DISTINCT CASE WHEN m.role='assistant' THEN 1 END) as assistant_messages,
    MAX(m.created_at) as last_message_at,
    SUM(m.tokens_used) as total_tokens_used
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id AND m.is_deleted = false
GROUP BY c.id, c.user_id, c.title;

CREATE INDEX IF NOT EXISTS idx_conversation_stats_id ON conversation_stats(id);
CREATE INDEX IF NOT EXISTS idx_conversation_stats_user_id ON conversation_stats(user_id);

-- ============================================
-- 9. FUNCTIONS
-- ============================================

-- Clean up expired cache
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM cache WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Mark message as deleted (soft delete)
CREATE OR REPLACE FUNCTION delete_message(msg_id BIGINT)
RETURNS void AS $$
BEGIN
    UPDATE messages SET is_deleted = true, deleted_at = CURRENT_TIMESTAMP WHERE id = msg_id;
END;
$$ LANGUAGE plpgsql;

-- Get user conversation count (efficient)
CREATE OR REPLACE FUNCTION get_user_conversation_count(user_id BIGINT)
RETURNS BIGINT AS $$
    SELECT COUNT(*) FROM conversations WHERE user_id = user_id;
$$ LANGUAGE SQL IMMUTABLE;

-- ============================================
-- 10. TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================
-- 11. PERMISSIONS
-- ============================================

-- Create app user (don't use postgres for app)
CREATE USER bot_app WITH PASSWORD 'secure_password_here';

GRANT CONNECT ON DATABASE aibot_700m TO bot_app;
GRANT USAGE ON SCHEMA public TO bot_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bot_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bot_app;

-- ============================================
-- 12. SETTINGS FOR PERFORMANCE
-- ============================================

-- Optimize for large tables
ALTER TABLE messages SET (fillfactor = 70, autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE analytics SET (fillfactor = 70, autovacuum_vacuum_scale_factor = 0.01);

-- Perform initial vacuum and analyze
VACUUM ANALYZE;

-- ============================================
-- DONE!
-- ============================================
GRANT ALL PRIVILEGES ON DATABASE aibot_700m TO postgres;
