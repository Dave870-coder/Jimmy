"""
Production monitoring and metrics collection for 7M users.
Uses Prometheus for metrics, integrates with Grafana.
"""

import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
import os

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, CollectorRegistry,
    generate_latest, CONTENT_TYPE_LATEST
)
from prometheus_client.core import REGISTRY

logger = logging.getLogger(__name__)

# Create custom registry for production
metrics_registry = CollectorRegistry()

# ============================================================
# REQUEST METRICS
# ============================================================

request_count = Counter(
    'jimmy_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=metrics_registry
)

request_duration = Histogram(
    'jimmy_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=metrics_registry
)

request_size = Histogram(
    'jimmy_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=metrics_registry
)

response_size = Histogram(
    'jimmy_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=metrics_registry
)

# ============================================================
# DATABASE METRICS
# ============================================================

db_query_duration = Histogram(
    'jimmy_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table'],
    buckets=(0.001, 0.01, 0.1, 1.0, 5.0),
    registry=metrics_registry
)

db_connections = Gauge(
    'jimmy_db_connections',
    'Current database connections',
    ['status'],
    registry=metrics_registry
)

db_pool_size = Gauge(
    'jimmy_db_pool_size',
    'Database connection pool size',
    registry=metrics_registry
)

db_errors = Counter(
    'jimmy_db_errors_total',
    'Total database errors',
    ['error_type'],
    registry=metrics_registry
)

# ============================================================
# CACHE METRICS
# ============================================================

cache_hits = Counter(
    'jimmy_cache_hits_total',
    'Cache hits',
    ['cache_type'],
    registry=metrics_registry
)

cache_misses = Counter(
    'jimmy_cache_misses_total',
    'Cache misses',
    ['cache_type'],
    registry=metrics_registry
)

cache_size = Gauge(
    'jimmy_cache_size_bytes',
    'Cache size in bytes',
    ['cache_type'],
    registry=metrics_registry
)

cache_operations_duration = Histogram(
    'jimmy_cache_operations_duration_seconds',
    'Cache operation duration',
    ['operation', 'cache_type'],
    registry=metrics_registry
)

# ============================================================
# BUSINESS METRICS
# ============================================================

messages_processed = Counter(
    'jimmy_messages_processed_total',
    'Total messages processed',
    ['source'],  # telegram, whatsapp
    registry=metrics_registry
)

ai_responses_generated = Counter(
    'jimmy_ai_responses_generated_total',
    'Total AI responses generated',
    registry=metrics_registry
)

ai_response_duration = Histogram(
    'jimmy_ai_response_duration_seconds',
    'AI response generation duration',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=metrics_registry
)

ai_errors = Counter(
    'jimmy_ai_errors_total',
    'Total AI processing errors',
    registry=metrics_registry
)

active_users = Gauge(
    'jimmy_active_users',
    'Active users',
    registry=metrics_registry
)

conversations = Gauge(
    'jimmy_conversations_total',
    'Total conversations',
    registry=metrics_registry
)

# ============================================================
# RESOURCE METRICS
# ============================================================

cpu_usage = Gauge(
    'jimmy_cpu_usage_percent',
    'CPU usage percentage',
    registry=metrics_registry
)

memory_usage = Gauge(
    'jimmy_memory_usage_bytes',
    'Memory usage in bytes',
    registry=metrics_registry
)

memory_usage_percent = Gauge(
    'jimmy_memory_usage_percent',
    'Memory usage percentage',
    registry=metrics_registry
)

disk_usage = Gauge(
    'jimmy_disk_usage_bytes',
    'Disk usage in bytes',
    registry=metrics_registry
)

# ============================================================
# QUEUE METRICS
# ============================================================

queue_size = Gauge(
    'jimmy_queue_size',
    'Message queue size',
    ['queue_type'],
    registry=metrics_registry
)

queue_processing_duration = Histogram(
    'jimmy_queue_processing_duration_seconds',
    'Queue item processing duration',
    ['queue_type'],
    registry=metrics_registry
)

queue_errors = Counter(
    'jimmy_queue_errors_total',
    'Queue processing errors',
    ['queue_type'],
    registry=metrics_registry
)

# ============================================================
# RATE LIMIT METRICS
# ============================================================

rate_limit_exceeded = Counter(
    'jimmy_rate_limit_exceeded_total',
    'Times rate limit was exceeded',
    ['user_tier'],
    registry=metrics_registry
)

rate_limit_remaining = Gauge(
    'jimmy_rate_limit_remaining',
    'Remaining requests in rate limit window',
    ['user_id', 'user_tier'],
    registry=metrics_registry
)

# ============================================================
# ERROR METRICS
# ============================================================

errors_total = Counter(
    'jimmy_errors_total',
    'Total errors',
    ['error_type', 'endpoint'],
    registry=metrics_registry
)

exceptions_total = Counter(
    'jimmy_exceptions_total',
    'Total exceptions',
    ['exception_type'],
    registry=metrics_registry
)

error_rate = Gauge(
    'jimmy_error_rate',
    'Current error rate',
    registry=metrics_registry
)

# ============================================================
# WEBHOOK METRICS
# ============================================================

webhook_events = Counter(
    'jimmy_webhook_events_total',
    'Webhook events received',
    ['source', 'event_type'],
    registry=metrics_registry
)

webhook_processing_duration = Histogram(
    'jimmy_webhook_processing_duration_seconds',
    'Webhook processing time',
    ['source'],
    registry=metrics_registry
)

webhook_errors = Counter(
    'jimmy_webhook_errors_total',
    'Webhook processing errors',
    ['source', 'error_type'],
    registry=metrics_registry
)

# ============================================================
# DECORATOR FOR AUTOMATIC METRICS
# ============================================================

def track_metrics(
    metric_type: str = 'request',
    endpoint: str = '',
    query_type: str = ''
):
    """Decorator to automatically track metrics."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if metric_type == 'request':
                    request_count.labels(
                        method='POST',
                        endpoint=endpoint,
                        status=200
                    ).inc()
                    request_duration.labels(
                        method='POST',
                        endpoint=endpoint
                    ).observe(duration)
                
                elif metric_type == 'db_query':
                    db_query_duration.labels(
                        query_type=query_type,
                        table='default'
                    ).observe(duration)
                
                elif metric_type == 'ai_response':
                    ai_response_duration.observe(duration)
                    ai_responses_generated.inc()
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                if metric_type == 'request':
                    request_count.labels(
                        method='POST',
                        endpoint=endpoint,
                        status=500
                    ).inc()
                
                exceptions_total.labels(
                    exception_type=type(e).__name__
                ).inc()
                
                raise
        
        return async_wrapper
    
    return decorator

# ============================================================
# MONITORING UTILITIES
# ============================================================

class MetricsCollector:
    """Collects and reports metrics."""
    
    @staticmethod
    def get_metrics_bytes() -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest(metrics_registry)
    
    @staticmethod
    def get_metrics_content_type() -> str:
        """Get content type for metrics response."""
        return CONTENT_TYPE_LATEST.encode('utf-8')
    
    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'requests_total': int(request_count._value.get()),
            'messages_processed': int(messages_processed._value.get()),
            'ai_responses': int(ai_responses_generated._value.get()),
            'active_users': int(active_users._value.get()),
            'errors': int(errors_total._value.get()),
        }
    
    @staticmethod
    def record_message_processed(source: str = 'telegram'):
        """Record processed message."""
        messages_processed.labels(source=source).inc()
    
    @staticmethod
    def record_ai_response():
        """Record AI response."""
        ai_responses_generated.inc()
    
    @staticmethod
    def record_cache_hit(cache_type: str = 'redis'):
        """Record cache hit."""
        cache_hits.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_cache_miss(cache_type: str = 'redis'):
        """Record cache miss."""
        cache_misses.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_error(error_type: str, endpoint: str = ''):
        """Record error."""
        errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    
    @staticmethod
    def set_active_users(count: int):
        """Set active users count."""
        active_users.set(count)
    
    @staticmethod
    def record_webhook_event(source: str, event_type: str):
        """Record webhook event."""
        webhook_events.labels(source=source, event_type=event_type).inc()

# Export metrics collector
metrics = MetricsCollector()
