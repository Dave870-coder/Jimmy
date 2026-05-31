#!/usr/bin/env python3
"""
Bulk Insert Script for SQLite 700M Record Database
Efficiently loads millions of records into SQLite with optimization
"""

import argparse
import sqlite3
import random
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

# Configuration
BATCH_SIZE = 50000  # Insert 50K records at a time
COMMIT_EVERY = 10  # Commit every 500K records
TOTAL_USERS = 100_000  # Distribute across 100K users
TOTAL_CONVERSATIONS = 10_000_000  # Base conversation count
DATABASE_PATH = Path(__file__).parent.parent / "data" / "bot.db"

# Sample content for messages
USER_MESSAGES = [
    "Hello, how are you?",
    "Can you help me with this?",
    "What do you think about this?",
    "Tell me about AI",
    "How does machine learning work?",
    "I need some advice",
    "What's the weather like?",
    "Can you explain this concept?",
]

ASSISTANT_RESPONSES = [
    "I'd be happy to help! Here's what I know: ",
    "Great question! Let me break this down for you: ",
    "That's an interesting point. Consider: ",
    "Based on my knowledge: ",
    "Let me explain this: ",
    "Good thinking! Here are some insights: ",
]


def create_database_path():
    """Create data directory if it doesn't exist"""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


def optimize_sqlite(conn: sqlite3.Connection):
    """Apply SQLite optimizations for bulk inserts"""
    cursor = conn.cursor()
    
    # Disable synchronous mode during bulk insert (faster)
    cursor.execute("PRAGMA synchronous = OFF")
    
    # Increase cache size
    cursor.execute("PRAGMA cache_size = -64000")
    
    # Use memory for temp storage
    cursor.execute("PRAGMA temp_store = MEMORY")
    
    # Disable foreign key checks temporarily (faster inserts)
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Set journal mode to WAL
    cursor.execute("PRAGMA journal_mode = WAL")
    
    print("✓ SQLite optimizations applied")


def restore_sqlite(conn: sqlite3.Connection):
    """Restore normal SQLite settings after bulk insert"""
    cursor = conn.cursor()
    
    # Re-enable safety features
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Vacuum to optimize database file
    cursor.execute("VACUUM")
    
    print("✓ SQLite restored to normal mode and optimized")


def create_schema(conn: sqlite3.Connection):
    """Create database schema from SQL file"""
    schema_file = Path(__file__).parent / "create_700m_sqlite_schema.sql"
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)
    
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    print("✓ Database schema created")


def generate_sample_users(conn: sqlite3.Connection, count: int):
    """Generate test users"""
    cursor = conn.cursor()
    
    users = []
    for i in range(count):
        username = f"user_{i:06d}"
        email = f"user_{i:06d}@example.com"
        telegram_id = 100000000 + i
        
        users.append((username, email, telegram_id, None, None))
    
    # Batch insert users
    print(f"Creating {count:,} test users...", end=" ", flush=True)
    start = time.time()
    cursor.executemany(
        "INSERT INTO users (username, email, telegram_id, whatsapp_id, metadata) VALUES (?, ?, ?, ?, ?)",
        users
    )
    conn.commit()
    elapsed = time.time() - start
    print(f"✓ {elapsed:.1f}s")


def generate_sample_conversations(conn: sqlite3.Connection, count: int):
    """Generate test conversations"""
    cursor = conn.cursor()
    
    print(f"Creating {count:,} test conversations...", end=" ", flush=True)
    start = time.time()
    
    # Batch insert conversations distributed across users
    batch = []
    for i in range(count):
        user_id = (i % TOTAL_USERS) + 1
        title = f"Conversation {i:08d}"
        
        batch.append((user_id, title, None, 0))
        
        if len(batch) >= 10000:
            cursor.executemany(
                "INSERT INTO conversations (user_id, title, metadata, is_archived) VALUES (?, ?, ?, ?)",
                batch
            )
            batch = []
    
    # Insert remaining
    if batch:
        cursor.executemany(
            "INSERT INTO conversations (user_id, title, metadata, is_archived) VALUES (?, ?, ?, ?)",
            batch
        )
    
    conn.commit()
    elapsed = time.time() - start
    print(f"✓ {elapsed:.1f}s")


def generate_messages(count: int) -> List[Tuple]:
    """Generate random messages for bulk insert"""
    messages = []
    base_date = datetime(2022, 1, 1)
    
    for i in range(count):
        # Random distribution
        conversation_id = random.randint(1, TOTAL_CONVERSATIONS)
        user_id = random.randint(1, TOTAL_USERS)
        
        # 60% user messages, 40% assistant
        if random.random() < 0.6:
            role = 'user'
            content = random.choice(USER_MESSAGES)
            tokens = random.randint(5, 50)
        else:
            role = 'assistant'
            content = random.choice(ASSISTANT_RESPONSES) + f"[response {i}]"
            tokens = random.randint(50, 500)
        
        # Random timestamp within 3-year window
        days_offset = random.randint(0, 365 * 3)
        created_at = (base_date + timedelta(days=days_offset)).isoformat()
        
        messages.append((
            conversation_id, user_id, role, content, tokens, None, 0, 0, None, created_at, created_at
        ))
    
    return messages


def bulk_insert_messages(conn: sqlite3.Connection, total_records: int):
    """Bulk insert messages in optimized batches"""
    cursor = conn.cursor()
    
    print(f"\n📊 Inserting {total_records:,} messages...")
    print("=" * 70)
    
    start_time = time.time()
    inserted = 0
    failed = 0
    batch_count = 0
    
    try:
        while inserted < total_records:
            # Generate batch
            remaining = total_records - inserted
            batch_size = min(BATCH_SIZE, remaining)
            
            batch = generate_messages(batch_size)
            
            try:
                # Insert batch
                cursor.executemany(
                    """INSERT INTO messages 
                    (conversation_id, user_id, role, content, tokens_used, embedding_id, 
                     is_deleted, is_edited, deleted_at, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    batch
                )
                
                inserted += batch_size
                batch_count += 1
                
                # Commit periodically
                if batch_count % COMMIT_EVERY == 0:
                    conn.commit()
                    
                    elapsed = time.time() - start_time
                    rate = inserted / elapsed
                    remaining_records = total_records - inserted
                    eta_seconds = remaining_records / rate if rate > 0 else 0
                    eta_hours = eta_seconds / 3600
                    
                    print(f"  Batch {batch_count:4d}: {inserted:12,} inserted | "
                          f"Rate: {rate:8.0f} rec/sec | ETA: {eta_hours:6.1f}h | "
                          f"Failed: {failed}")
                    
            except Exception as e:
                failed += batch_size
                print(f"  ⚠️  Batch {batch_count} failed: {str(e)[:50]}")
                conn.rollback()
        
        # Final commit
        conn.commit()
        
        elapsed = time.time() - start_time
        rate = inserted / elapsed if elapsed > 0 else 0
        
        print("=" * 70)
        print(f"✅ Insertion complete!")
        print(f"   Total inserted: {inserted:,}")
        print(f"   Total failed: {failed:,}")
        print(f"   Total time: {elapsed:.1f}s ({elapsed/60:.1f}m)")
        print(f"   Average rate: {rate:.0f} records/sec")
        print(f"   Throughput: {rate*1024/1024/1024:.2f} MB/sec")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Insertion interrupted by user")
        conn.commit()
        print(f"   Inserted so far: {inserted:,}")
        print(f"   Progress: {inserted/total_records*100:.1f}%")


def verify_data(conn: sqlite3.Connection):
    """Verify inserted data"""
    cursor = conn.cursor()
    
    print("\n📊 Verifying data...")
    print("=" * 70)
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM messages")
    message_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cursor.fetchone()[0]
    
    print(f"  Messages:      {message_count:>12,}")
    print(f"  Conversations: {conv_count:>12,}")
    print(f"  Users:         {user_count:>12,}")
    
    # Get database file size
    db_size = DATABASE_PATH.stat().st_size / (1024**3)  # Convert to GB
    print(f"  Database size: {db_size:>12.2f} GB")
    
    # Average size per message
    if message_count > 0:
        size_per_msg = (db_size * 1024**3) / message_count
        print(f"  Size per msg:  {size_per_msg:>12.1f} bytes")
    
    print("=" * 70)


def get_database_stats(conn: sqlite3.Connection):
    """Get SQLite database statistics"""
    cursor = conn.cursor()
    
    print("\n📈 Database Statistics:")
    print("=" * 70)
    
    # Table sizes
    tables = ['messages', 'conversations', 'users', 'memory', 'cache', 'analytics']
    total_rows = 0
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_rows += count
        print(f"  {table:20s}: {count:>12,} rows")
    
    # Get database page count
    cursor.execute("PRAGMA page_count")
    pages = cursor.fetchone()[0]
    
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    
    db_size_mb = (pages * page_size) / (1024 * 1024)
    
    print("=" * 70)
    print(f"  Total rows:    {total_rows:>12,}")
    print(f"  Pages:         {pages:>12,}")
    print(f"  Page size:     {page_size:>12,} bytes")
    print(f"  Database size: {db_size_mb:>12.1f} MB")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Bulk insert data into SQLite 700M database")
    parser.add_argument("--records", type=int, default=1000000,
                       help="Number of records to insert (default: 1M)")
    parser.add_argument("--test", action="store_true",
                       help="Load test data (1M records)")
    
    args = parser.parse_args()
    
    # Determine record count
    if args.test:
        total_records = 1_000_000
    else:
        total_records = args.records
    
    print("\n" + "=" * 70)
    print("🗄️  SQLite 700M RECORD BULK INSERT")
    print("=" * 70)
    print(f"Target: {total_records:,} records")
    print(f"Database: {DATABASE_PATH}")
    print("=" * 70 + "\n")
    
    # Create database path
    create_database_path()
    
    # Connect to database
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30)
    
    try:
        # Create schema
        print("Setting up schema...\n")
        create_schema(conn)
        
        # Apply optimizations
        optimize_sqlite(conn)
        
        # Generate base data
        print("\nGenerating base data...")
        generate_sample_users(conn, TOTAL_USERS)
        generate_sample_conversations(conn, TOTAL_CONVERSATIONS)
        
        # Bulk insert messages
        bulk_insert_messages(conn, total_records)
        
        # Restore normal mode
        restore_sqlite(conn)
        
        # Verify and get stats
        verify_data(conn)
        get_database_stats(conn)
        
        print("\n✅ SQLite database successfully loaded!")
        print(f"Database file: {DATABASE_PATH}")
        print("\n💡 To verify queries work:")
        print("   python local_test.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
