"""
Database monitoring for large-scale deployments (700M+ records).
Tracks performance, health, and optimization opportunities.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Monitor and optimize large-scale databases."""
    
    @staticmethod
    async def get_database_stats(session: Session) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns info on table sizes, row counts, cache hit ratio, etc.
        """
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "tables": {},
                "cache_hit_ratio": None,
                "total_size": None,
                "index_count": None
            }
            
            # Get table sizes and row counts
            table_query = text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                n_live_tup as row_count
            FROM pg_tables
            JOIN pg_stat_user_tables ON pg_tables.tablename = pg_stat_user_tables.relname
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            result = await session.execute(table_query)
            for row in result:
                stats['tables'][row[1]] = {
                    'size': row[2],
                    'row_count': row[3]
                }
            
            # Get cache hit ratio
            cache_query = text("""
            SELECT 
                ROUND(
                    (sum(heap_blks_hit)::float / 
                    (sum(heap_blks_hit) + sum(heap_blks_read))::float) * 100, 2
                ) as cache_hit_ratio
            FROM pg_statio_user_tables
            WHERE sum(heap_blks_hit) + sum(heap_blks_read) > 0
            """)
            
            result = await session.execute(cache_query)
            row = result.fetchone()
            if row:
                stats['cache_hit_ratio'] = row[0]
            
            # Get total database size
            size_query = text("""
            SELECT pg_size_pretty(pg_database_size('aibot_700m'))
            """)
            
            result = await session.execute(size_query)
            row = result.fetchone()
            if row:
                stats['total_size'] = row[0]
            
            # Get index count
            index_query = text("""
            SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'
            """)
            
            result = await session.execute(index_query)
            row = result.fetchone()
            if row:
                stats['index_count'] = row[0]
            
            logger.info(f"Database stats retrieved: {stats['total_size']} total, "
                       f"{stats['cache_hit_ratio']}% cache hit")
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def get_slowest_queries(session: Session, limit: int = 10) -> list:
        """
        Get slowest queries from query logs.
        
        Helps identify optimization opportunities.
        """
        try:
            query = text("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                stddev_time,
                max_time
            FROM pg_stat_statements
            WHERE query NOT LIKE '%pg_stat%'
            ORDER BY total_time DESC
            LIMIT :limit
            """)
            
            result = await session.execute(query, {"limit": limit})
            
            slowest_queries = []
            for row in result:
                slowest_queries.append({
                    'query': row[0][:100],  # First 100 chars
                    'calls': row[1],
                    'total_time_ms': round(row[2], 2),
                    'mean_time_ms': round(row[3], 2),
                    'stddev_time_ms': round(row[4], 2),
                    'max_time_ms': round(row[5], 2)
                })
            
            return slowest_queries
        
        except Exception as e:
            logger.error(f"Error getting slowest queries: {e}")
            return []
    
    @staticmethod
    async def get_index_usage_stats(session: Session) -> Dict[str, Any]:
        """
        Get index usage statistics.
        
        Identifies unused or underutilized indexes.
        """
        try:
            query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan as scan_count,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            """)
            
            result = await session.execute(query)
            
            index_stats = {
                "used": [],
                "unused": []
            }
            
            for row in result:
                index_info = {
                    'table': row[1],
                    'index': row[2],
                    'scans': row[3],
                    'tuples_read': row[4],
                    'tuples_fetched': row[5],
                    'size': row[6]
                }
                
                if row[3] == 0:
                    index_stats['unused'].append(index_info)
                else:
                    index_stats['used'].append(index_info)
            
            logger.info(f"Index stats: {len(index_stats['used'])} used, "
                       f"{len(index_stats['unused'])} unused")
            
            return index_stats
        
        except Exception as e:
            logger.error(f"Error getting index usage: {e}")
            return {"used": [], "unused": []}
    
    @staticmethod
    async def get_table_bloat(session: Session) -> Dict[str, Any]:
        """
        Analyze table bloat (wasted space).
        
        Returns tables that would benefit from VACUUM FULL.
        """
        try:
            query = text("""
            SELECT 
                schemaname,
                tablename,
                ROUND(100 * (pg_total_relation_size(schemaname||'.'||tablename) - 
                    pg_relation_size(schemaname||'.'||tablename))::numeric / 
                    pg_total_relation_size(schemaname||'.'||tablename), 2) as bloat_ratio,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY bloat_ratio DESC
            """)
            
            result = await session.execute(query)
            
            bloat_info = {
                "high_bloat": [],  # > 30%
                "medium_bloat": [],  # 10-30%
                "low_bloat": []  # < 10%
            }
            
            for row in result:
                table_info = {
                    'table': row[1],
                    'bloat_ratio': row[2],
                    'total_size': row[3]
                }
                
                if row[2] > 30:
                    bloat_info['high_bloat'].append(table_info)
                elif row[2] > 10:
                    bloat_info['medium_bloat'].append(table_info)
                else:
                    bloat_info['low_bloat'].append(table_info)
            
            logger.info(f"Table bloat: {len(bloat_info['high_bloat'])} tables with high bloat")
            
            return bloat_info
        
        except Exception as e:
            logger.error(f"Error analyzing table bloat: {e}")
            return {"high_bloat": [], "medium_bloat": [], "low_bloat": []}
    
    @staticmethod
    async def get_connection_stats(session: Session) -> Dict[str, Any]:
        """Get database connection statistics."""
        try:
            query = text("""
            SELECT 
                datname,
                count(*) as connections,
                max(EXTRACT(EPOCH FROM (now() - query_start))) as max_query_time_seconds
            FROM pg_stat_activity
            WHERE datname IS NOT NULL
            GROUP BY datname
            """)
            
            result = await session.execute(query)
            
            conn_stats = {}
            for row in result:
                conn_stats[row[0]] = {
                    'connections': row[1],
                    'max_query_time_seconds': int(row[2]) if row[2] else 0
                }
            
            return conn_stats
        
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {}
    
    @staticmethod
    async def optimize_tables(session: Session) -> Dict[str, str]:
        """
        Perform optimization on all tables.
        
        Runs VACUUM ANALYZE on main tables.
        """
        try:
            logger.info("🔧 Starting table optimization...")
            
            results = {}
            tables = ['messages', 'conversations', 'users', 'analytics']
            
            for table in tables:
                try:
                    logger.info(f"  Optimizing {table}...")
                    
                    # Vacuum and analyze
                    await session.execute(text(f"VACUUM ANALYZE {table}"))
                    results[table] = "✓ Optimized"
                    
                except Exception as e:
                    logger.error(f"  Error optimizing {table}: {e}")
                    results[table] = f"✗ Error: {e}"
            
            logger.info("✅ Table optimization complete")
            return results
        
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def analyze_query_plan(session: Session, query: str) -> str:
        """
        Analyze query execution plan (EXPLAIN ANALYZE).
        
        Helps identify inefficient queries.
        """
        try:
            explain_query = text(f"EXPLAIN ANALYZE {query}")
            result = await session.execute(explain_query)
            
            plan_lines = []
            for row in result:
                plan_lines.append(row[0])
            
            return "\n".join(plan_lines)
        
        except Exception as e:
            logger.error(f"Error analyzing query plan: {e}")
            return f"Error: {e}"
    
    @staticmethod
    async def get_health_summary(session: Session) -> Dict[str, Any]:
        """
        Get overall database health summary.
        
        Quick overview of database status and issues.
        """
        try:
            stats = await DatabaseMonitor.get_database_stats(session)
            bloat = await DatabaseMonitor.get_table_bloat(session)
            index_usage = await DatabaseMonitor.get_index_usage_stats(session)
            connections = await DatabaseMonitor.get_connection_stats(session)
            
            health = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "warnings": [],
                "stats": {
                    "total_size": stats.get('total_size'),
                    "tables": len(stats.get('tables', {})),
                    "cache_hit_ratio": stats.get('cache_hit_ratio'),
                    "index_count": stats.get('index_count')
                },
                "bloat": {
                    "high_bloat_tables": len(bloat.get('high_bloat', []))
                },
                "indexes": {
                    "used": len(index_usage.get('used', [])),
                    "unused": len(index_usage.get('unused', []))
                },
                "connections": connections
            }
            
            # Check for issues
            if stats.get('cache_hit_ratio') and stats['cache_hit_ratio'] < 80:
                health['warnings'].append(f"Low cache hit ratio: {stats['cache_hit_ratio']}%")
                health['overall_status'] = "degraded"
            
            if bloat.get('high_bloat') and len(bloat['high_bloat']) > 0:
                health['warnings'].append(f"{len(bloat['high_bloat'])} tables with high bloat")
                health['overall_status'] = "degraded"
            
            if index_usage.get('unused') and len(index_usage['unused']) > 5:
                health['warnings'].append(f"{len(index_usage['unused'])} unused indexes")
            
            logger.info(f"Database health: {health['overall_status']}")
            
            return health
        
        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {"error": str(e), "overall_status": "error"}


# Export monitor class
__all__ = ['DatabaseMonitor']
