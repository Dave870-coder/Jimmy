"""
Health monitoring system for the bot.
Monitors bot health and triggers auto-restart on failure.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors bot health and auto-restarts on failure"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.last_check = datetime.now()
        self.failure_count = 0
        self.max_failures = 3
        self.healthy = True
        self.startup_time = datetime.now()
        self.total_checks = 0
        self.successful_checks = 0
        self.failed_checks = 0

    async def check_health(self, checker: Callable) -> bool:
        """Check if bot is healthy"""
        try:
            self.total_checks += 1
            await checker()
            self.failure_count = 0
            self.healthy = True
            self.successful_checks += 1
            self.last_check = datetime.now()
            logger.debug("✅ Health check passed")
            return True
        except Exception as e:
            self.failure_count += 1
            self.failed_checks += 1
            logger.error(
                f"❌ Health check failed ({self.failure_count}/{self.max_failures}): {e}"
            )

            if self.failure_count >= self.max_failures:
                self.healthy = False
                logger.critical("🚨 Bot marked as unhealthy - restart needed")
                return False

            return True

    async def monitor(
        self,
        checker: Callable,
        restart_handler: Optional[Callable] = None,
    ):
        """Continuously monitor health"""
        logger.info(f"Starting health monitor (interval: {self.check_interval}s)")
        while True:
            await asyncio.sleep(self.check_interval)

            if not await self.check_health(checker):
                if restart_handler:
                    logger.info("Calling restart handler...")
                    await restart_handler()
                else:
                    logger.critical("Health monitor: restart handler not provided")

    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        uptime = datetime.now() - self.startup_time
        check_success_rate = (
            (self.successful_checks / self.total_checks * 100)
            if self.total_checks > 0
            else 0
        )

        return {
            "healthy": self.healthy,
            "failure_count": self.failure_count,
            "last_check": self.last_check.isoformat(),
            "last_check_ago_seconds": (datetime.now() - self.last_check).total_seconds(),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "success_rate_percent": check_success_rate,
            "startup_time": self.startup_time.isoformat(),
        }

    async def startup_check(self, checker: Callable, timeout: int = 30) -> bool:
        """Verify bot is healthy on startup"""
        logger.info("🔍 Performing startup health check...")
        try:
            # Try multiple times with delay
            for attempt in range(3):
                try:
                    await asyncio.wait_for(checker(), timeout=timeout)
                    logger.info(f"✅ Startup check passed (attempt {attempt + 1})")
                    self.successful_checks += 1
                    self.total_checks += 1
                    return True
                except asyncio.TimeoutError:
                    logger.warning(
                        f"⚠️  Startup check timeout (attempt {attempt + 1}/3)"
                    )
                    if attempt < 2:
                        await asyncio.sleep(5)
                except Exception as e:
                    logger.warning(f"⚠️  Startup check failed (attempt {attempt + 1}): {e}")
                    if attempt < 2:
                        await asyncio.sleep(5)

            logger.error("❌ Startup health check failed after 3 attempts")
            self.failed_checks += 1
            self.total_checks += 1
            return False

        except Exception as e:
            logger.error(f"❌ Unexpected error during startup check: {e}")
            return False


# Global monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def reset_health_monitor():
    """Reset health monitor (useful for testing)"""
    global _health_monitor
    _health_monitor = None
