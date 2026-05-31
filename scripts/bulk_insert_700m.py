#!/usr/bin/env python3
"""
Bulk insert 700M records efficiently into PostgreSQL.
Optimized for maximum throughput.

Usage:
    python scripts/bulk_insert_700m.py --records 700000000
    python scripts/bulk_insert_700m.py --records 1000000 --test  # Test with 1M
"""

import psycopg2
from psycopg2.extras import execute_batch, execute_values
import time
import random
import sys
from datetime import datetime, timedelta
from typing import List, Tuple
import argparse

# Database configuration
DB_CONFIG = {
    'dbname': 'aibot_700m',
    'user': 'postgres',
    'password': 'change_me_123',
    'host': 'localhost',
    'port': 5432
}

# Performance tuning
BATCH_SIZE = 50000  # Records per batch (larger = faster but more memory)
COMMIT_EVERY = 10  # Commit every N batches
TOTAL_USERS = 100_000  # Distribute across users
TOTAL_CONVERSATIONS = 10_000_000  # Base conversations

# Tracking
total_inserted = 0
failed_batches = 0
start_time = None

def generate_message_data(batch_num: int, batch_size: int, start_record: int) -> List[Tuple]:
    """
    Generate sample message data for a batch.
    
    Creates realistic message data:
    - Random users and conversations
    - Mix of user and assistant messages
    - Realistic timestamps (last 2 years)
    - Random content length
    """
    data = []
    
    for i in range(batch_size):
        record_id = start_record + i
        
        # Distribute records across users evenly
        user_id = (record_id % TOTAL_USERS) + 1
        
        # Distribute across conversations (some users have more conversations)
        conversation_id = (record_id % TOTAL_CONVERSATIONS) + 1
        
        # Alternate user/assistant with ~60% user, 40% assistant
        role = 'user' if random.random() < 0.6 else 'assistant'
        
        # Random content (realistic lengths)
        if role == 'user':
            content_length = random.randint(10, 500)
            content = f"User message {record_id}: " + "x" * content_length
            tokens = content_length // 4  # Rough token count
        else:
            content_length = random.randint(50, 2000)
            content = f"Assistant response {record_id}: " + "x" * content_length
            tokens = content_length // 4
        
        # Random timestamp in last 2 years
        days_ago = random.randint(0, 730)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        data.append((
            conversation_id,
            user_id,
            role,
            content,
            tokens,
            created_at
        ))
    
    return data


def create_initial_users_and_conversations(conn):
    """Create initial users and conversations."""
    print("🔄 Creating initial users and conversations...")
    
    cursor = conn.cursor()
    
    try:
        # Disable auto-commit for faster inserts
        cursor.execute("SET synchronous_commit = OFF")
        cursor.execute("SET maintenance_work_mem = '1GB'")
        cursor.execute("SET work_mem = '512MB'")
        
        # Create users
        print(f"  Creating {TOTAL_USERS:,} users...")
        user_data = [
            (f"user_{i}", f"user_{i}@bot.local", f"{1000000000 + i}", None, '{}')
            for i in range(1, TOTAL_USERS + 1)
        ]
        
        execute_batch(cursor, """
            INSERT INTO users (username, email, telegram_id, whatsapp_id, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """, user_data, page_size=10000)
        
        conn.commit()
        print(f"  ✓ {TOTAL_USERS:,} users created")
        
        # Create conversations
        print(f"  Creating {TOTAL_CONVERSATIONS:,} conversations...")
        conv_data = [
            (
                (i % TOTAL_USERS) + 1,  # user_id
                f"Conversation {i}",    # title
                (datetime.now() - timedelta(days=random.randint(0, 730))).isoformat(),
                '{}'
            )
            for i in range(1, TOTAL_CONVERSATIONS + 1)
        ]
        
        execute_batch(cursor, """
            INSERT INTO conversations (user_id, title, created_at, metadata)
            VALUES (%s, %s, %s, %s)
        """, conv_data, page_size=10000)
        
        conn.commit()
        print(f"  ✓ {TOTAL_CONVERSATIONS:,} conversations created")
        
        cursor.close()
        
    except Exception as e:
        print(f"  ❌ Error creating base data: {e}")
        conn.rollback()
        raise


def bulk_insert_messages(conn, total_records: int):
    """Bulk insert messages efficiently."""
    global total_inserted, failed_batches, start_time
    
    cursor = conn.cursor()
    total_batches = total_records // BATCH_SIZE
    
    print(f"\n🚀 Starting bulk insert of {total_records:,} messages")
    print(f"   Batch size: {BATCH_SIZE:,}")
    print(f"   Total batches: {total_batches:,}")
    print(f"   Est. time: {(total_records / 50000 / 3600):.1f} hours")
    print()
    
    start_time = time.time()
    
    try:
        # Optimize for fast inserts
        cursor.execute("SET synchronous_commit = OFF")
        cursor.execute("SET maintenance_work_mem = '1GB'")
        cursor.execute("SET work_mem = '512MB'")
        cursor.execute("SET fsync = OFF")
        cursor.execute("SET full_page_writes = OFF")
        
        for batch_num in range(total_batches):
            try:
                # Generate batch data
                start_record = batch_num * BATCH_SIZE
                data = generate_message_data(batch_num, BATCH_SIZE, start_record)
                
                # Insert batch
                sql = """
                    INSERT INTO messages (conversation_id, user_id, role, content, tokens_used, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                execute_batch(cursor, sql, data, page_size=BATCH_SIZE)
                total_inserted += BATCH_SIZE
                
                # Commit every N batches
                if (batch_num + 1) % COMMIT_EVERY == 0:
                    conn.commit()
                    print_progress(batch_num, total_batches)
                
                # Vacuum every 1000 batches
                if (batch_num + 1) % 1000 == 0:
                    cursor.execute("VACUUM ANALYZE messages")
                    conn.commit()
            
            except Exception as e:
                print(f"❌ Error in batch {batch_num}: {e}")
                conn.rollback()
                failed_batches += 1
                continue
        
        # Final commit
        conn.commit()
        print_final_summary()
        
        # Create indexes (or re-create if needed)
        print("\n🔍 Finalizing database...")
        cursor.execute("REINDEX TABLE messages")
        cursor.execute("ANALYZE messages")
        conn.commit()
        print("✅ Database finalized")
        
    finally:
        # Re-enable settings
        try:
            cursor.execute("SET synchronous_commit = ON")
            cursor.execute("SET fsync = ON")
            cursor.execute("SET full_page_writes = ON")
            conn.commit()
        except:
            pass
        
        cursor.close()


def print_progress(batch_num: int, total_batches: int):
    """Print progress update."""
    elapsed = time.time() - start_time
    rate = total_inserted / elapsed if elapsed > 0 else 0
    remaining = (total_batches - batch_num - 1) * BATCH_SIZE
    eta_seconds = remaining / rate if rate > 0 else 0
    
    print(f"✓ Batch {batch_num + 1:,}/{total_batches:,} | "
          f"Inserted: {total_inserted:,} | "
          f"Rate: {rate:,.0f} rec/sec | "
          f"ETA: {eta_seconds/3600:.1f} hours | "
          f"Failed: {failed_batches}")


def print_final_summary():
    """Print final summary."""
    elapsed = time.time() - start_time
    rate = total_inserted / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 70)
    print(f"✅ INSERT COMPLETED!")
    print(f"   Total inserted:  {total_inserted:,} records")
    print(f"   Time elapsed:    {elapsed/3600:.2f} hours ({elapsed/60:.1f} min)")
    print(f"   Average rate:    {rate:,.0f} records/sec")
    print(f"   Failed batches:  {failed_batches}")
    print(f"   Storage:         ~{(total_inserted * 1024 / 1_000_000):.1f}GB")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Bulk insert millions of records into PostgreSQL'
    )
    parser.add_argument(
        '--records',
        type=int,
        default=1_000_000,
        help='Total records to insert (default: 1M)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode with reduced records'
    )
    parser.add_argument(
        '--users-only',
        action='store_true',
        help='Only create users and conversations (no messages)'
    )
    
    args = parser.parse_args()
    
    if args.test:
        args.records = 1_000_000
        print("🧪 TEST MODE: 1M records")
    
    try:
        # Connect to database
        print(f"🔌 Connecting to {DB_CONFIG['dbname']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected")
        
        # Create base data (users & conversations)
        create_initial_users_and_conversations(conn)
        
        # Insert messages
        if not args.users_only:
            bulk_insert_messages(conn, args.records)
        
        conn.close()
        print("\n🎉 All done!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
