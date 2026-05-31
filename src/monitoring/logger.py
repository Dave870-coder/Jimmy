"""Monitoring and logging utilities."""

import json
import logging
from datetime import datetime

from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """Setup application logging."""
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # JSON formatter for structured logging
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    return logger


class MetricsCollector:
    """Collect and track application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "total_messages": 0,
            "total_users": 0,
            "total_api_calls": 0,
            "errors": 0,
            "average_response_time": 0.0,
        }

    def record_message(self):
        """Record a message."""
        self.metrics["total_messages"] += 1

    def record_user(self):
        """Record a user."""
        self.metrics["total_users"] += 1

    def record_api_call(self, response_time: float):
        """Record an API call."""
        self.metrics["total_api_calls"] += 1
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total_calls = self.metrics["total_api_calls"]
        new_avg = (current_avg * (total_calls - 1) + response_time) / total_calls
        self.metrics["average_response_time"] = new_avg

    def record_error(self):
        """Record an error."""
        self.metrics["errors"] += 1

    def get_metrics(self) -> dict:
        """Get current metrics."""
        return self.metrics.copy()


# Global metrics instance
metrics_collector = MetricsCollector()
