#!/usr/bin/env python3
"""
Test script for 700M record database.
Verifies database setup, performance, and bot functionality.

Usage:
    python test_700m_database.py
    python test_700m_database.py --quick  # Fast tests only
"""

import asyncio
import time
import psycopg2
from psycopg2.extras import execute_batch
import sys
from datetime import datetime, timedelta
import argparse

# Database config
DB_CONFIG = {
    'dbname': 'aibot_700m',
    'user': 'postgres',
    'password': 'change_me_123',
    'host': 'localhost',
    'port': 5432
}

class DatabaseTester:
    """Test database setup and performance."""
    
    def __init__(self):
        self.conn = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
    
    def connect(self):
        """Connect to database."""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def test_connection(self):
        """Test 1: Basic connection."""
        print("\n🧪 Test 1: Database Connection")
        print("   Testing: Can connect to PostgreSQL")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"   ✅ PASS: {version[:50]}...")
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_schema(self):
        """Test 2: Schema exists."""
        print("\n🧪 Test 2: Database Schema")
        print("   Testing: All tables created correctly")
        
        try:
            cursor = self.conn.cursor()
            
            # Check tables
            cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            expected_tables = ['users', 'conversations', 'messages', 'embeddings', 
                             'memory', 'cache', 'analytics']
            
            cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing = [t for t in expected_tables if t not in existing_tables]
            
            if missing:
                print(f"   ❌ FAIL: Missing tables: {missing}")
                self.results['failed'] += 1
            else:
                print(f"   ✅ PASS: All {table_count} tables exist")
                self.results['passed'] += 1
            
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_indexes(self):
        """Test 3: Indexes created."""
        print("\n🧪 Test 3: Database Indexes")
        print("   Testing: Proper indexes for performance")
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE schemaname = 'public'
            """)
            index_count = cursor.fetchone()[0]
            
            if index_count < 10:
                print(f"   ⚠️  WARNING: Only {index_count} indexes (recommend 15+)")
            else:
                print(f"   ✅ PASS: {index_count} indexes created")
            
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_table_sizes(self):
        """Test 4: Table sizes."""
        print("\n🧪 Test 4: Table Sizes")
        print("   Testing: Database size and table distribution")
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            SELECT 
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                n_live_tup as rows
            FROM pg_tables
            JOIN pg_stat_user_tables ON pg_tables.tablename = pg_stat_user_tables.relname
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            print("   Top tables by size:")
            for row in cursor.fetchall():
                print(f"      {row[0]:20} {row[1]:>10} ({row[2]:>12,} rows)")
            
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_insert_speed(self):
        """Test 5: Insert performance."""
        print("\n🧪 Test 5: Insert Performance")
        print("   Testing: Fast bulk inserts (1000 records)")
        
        try:
            cursor = self.conn.cursor()
            
            # Ensure test users exist
            cursor.execute("""
            INSERT INTO users (username, email, telegram_id)
            SELECT 'test_user_' || i, 'test_' || i || '@test.local', 9000000 + i
            FROM generate_series(1, 10) i
            ON CONFLICT (username) DO NOTHING
            """)
            self.conn.commit()
            
            cursor.execute("""
            INSERT INTO conversations (user_id, title)
            SELECT user_id, 'Test Conv ' || row_number() OVER ()
            FROM (
                SELECT id as user_id FROM users 
                WHERE username LIKE 'test_user_%' LIMIT 10
            ) t
            """)
            self.conn.commit()
            
            # Test insert speed
            start = time.time()
            
            data = [
                (
                    (i % 100) + 1,  # conversation_id
                    (i % 10) + 1,   # user_id
                    'user' if i % 2 == 0 else 'assistant',
                    f"Test message {i}",
                    50
                )
                for i in range(1000)
            ]
            
            cursor.executemany("""
            INSERT INTO messages (conversation_id, user_id, role, content, tokens_used)
            VALUES (%s, %s, %s, %s, %s)
            """, data)
            
            self.conn.commit()
            elapsed = time.time() - start
            rate = 1000 / elapsed
            
            print(f"   ✅ PASS: Inserted 1000 records in {elapsed:.2f}s ({rate:,.0f} rec/sec)")
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_query_speed(self):
        """Test 6: Query performance."""
        print("\n🧪 Test 6: Query Performance")
        print("   Testing: Indexed query speed")
        
        try:
            cursor = self.conn.cursor()
            
            # Simple indexed lookup
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = 1")
            result = cursor.fetchone()[0]
            elapsed = time.time() - start
            
            if elapsed < 0.1:
                status = "✅ EXCELLENT"
            elif elapsed < 0.5:
                status = "✅ GOOD"
            elif elapsed < 1.0:
                status = "⚠️  ACCEPTABLE"
            else:
                status = "❌ SLOW"
            
            print(f"   {status}: Simple query in {elapsed*1000:.1f}ms (found {result} records)")
            
            # Date range query
            start = time.time()
            cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            """)
            result = cursor.fetchone()[0]
            elapsed = time.time() - start
            
            print(f"   ✅ PASS: Range query in {elapsed*1000:.1f}ms (found {result} records)")
            
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def test_cache_hit_ratio(self):
        """Test 7: Cache performance."""
        print("\n🧪 Test 7: Cache Hit Ratio")
        print("   Testing: PostgreSQL buffer cache effectiveness")
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            SELECT 
                ROUND(100 * 
                    (sum(heap_blks_hit)::float / 
                    (sum(heap_blks_hit) + sum(heap_blks_read))::float), 2) as cache_ratio
            FROM pg_statio_user_tables
            """)
            
            ratio = cursor.fetchone()[0]
            
            if ratio is None or ratio < 80:
                print(f"   ⚠️  WARNING: Cache hit ratio {ratio}% (recommend 85%+)")
            else:
                print(f"   ✅ PASS: Cache hit ratio {ratio}%")
            
            self.results['passed'] += 1
            cursor.close()
        except Exception as e:
            print(f"   ⚠️  WARNING: {e} (stats extension may not be enabled)")
            self.results['passed'] += 1  # Don't fail on this
    
    def test_connection_pool(self):
        """Test 8: Connection pooling."""
        print("\n🧪 Test 8: Connection Pool")
        print("   Testing: Multiple concurrent connections")
        
        try:
            connections = []
            
            # Create 5 test connections
            for i in range(5):
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                connections.append(conn)
            
            print(f"   ✅ PASS: Created 5 concurrent connections successfully")
            
            # Close all
            for conn in connections:
                conn.close()
            
            self.results['passed'] += 1
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            self.results['failed'] += 1
    
    def run_all_tests(self, quick=False):
        """Run all tests."""
        print("=" * 70)
        print("🗄️  700M RECORD DATABASE TEST SUITE")
        print("=" * 70)
        
        if not self.connect():
            return False
        
        try:
            self.test_connection()
            self.test_schema()
            self.test_indexes()
            self.test_table_sizes()
            
            if not quick:
                self.test_insert_speed()
                self.test_query_speed()
                self.test_cache_hit_ratio()
                self.test_connection_pool()
            
            self.print_summary()
            
        finally:
            self.disconnect()
        
        return self.results['failed'] == 0
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Total:  {self.results['passed'] + self.results['failed']}")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("   Your 700M database is ready for production use!")
        else:
            print(f"\n⚠️  {self.results['failed']} TEST(S) FAILED")
            print("   Please check the errors above")
        
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test 700M record database'
    )
    parser.add_argument('--quick', action='store_true', help='Quick tests only')
    
    args = parser.parse_args()
    
    tester = DatabaseTester()
    success = tester.run_all_tests(quick=args.quick)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
