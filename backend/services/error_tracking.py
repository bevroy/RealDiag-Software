"""
Error Tracking with Sentry Integration
Captures and reports errors to Sentry for monitoring
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import Sentry SDK
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry SDK not installed. Error tracking disabled.")

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Error tracking and reporting with Sentry"""
    
    def __init__(self):
        self.enabled = False
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        
        if SENTRY_AVAILABLE and self.sentry_dsn:
            self._initialize_sentry()
    
    def _initialize_sentry(self):
        """Initialize Sentry SDK"""
        try:
            # Logging integration
            logging_integration = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            # FastAPI integration
            fastapi_integration = FastApiIntegration(
                transaction_style="endpoint"
            )
            
            sentry_sdk.init(
                dsn=self.sentry_dsn,
                integrations=[
                    fastapi_integration,
                    logging_integration
                ],
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                environment=os.getenv("ENVIRONMENT", "development"),
                release=os.getenv("APP_VERSION", "1.4.0"),
                send_default_pii=False,  # Don't send PII
                attach_stacktrace=True,
                max_breadcrumbs=50
            )
            
            self.enabled = True
            logger.info("Sentry error tracking initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            self.enabled = False
    
    def capture_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ):
        """Capture an exception with context"""
        if not self.enabled:
            logger.error(f"Exception: {error}", extra=context or {})
            return
        
        try:
            # Add context to Sentry
            if context:
                sentry_sdk.set_context("custom", context)
            
            # Set level
            sentry_sdk.set_level(level)
            
            # Capture exception
            sentry_sdk.capture_exception(error)
            
        except Exception as e:
            logger.error(f"Failed to capture exception in Sentry: {e}")
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ):
        """Capture a message with context"""
        if not self.enabled:
            logger.log(getattr(logging, level.upper(), logging.INFO), message, extra=context or {})
            return
        
        try:
            if context:
                sentry_sdk.set_context("custom", context)
            
            sentry_sdk.capture_message(message, level=level)
            
        except Exception as e:
            logger.error(f"Failed to capture message in Sentry: {e}")
    
    def set_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """Set user context for error tracking"""
        if not self.enabled:
            return
        
        try:
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
        except Exception as e:
            logger.error(f"Failed to set user in Sentry: {e}")
    
    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info", data: Optional[Dict] = None):
        """Add a breadcrumb for error context"""
        if not self.enabled:
            return
        
        try:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )
        except Exception as e:
            logger.error(f"Failed to add breadcrumb in Sentry: {e}")
    
    def start_transaction(self, name: str, op: str = "http.server") -> Any:
        """Start a performance transaction"""
        if not self.enabled:
            return None
        
        try:
            return sentry_sdk.start_transaction(name=name, op=op)
        except Exception as e:
            logger.error(f"Failed to start transaction in Sentry: {e}")
            return None
    
    def capture_performance_issue(self, operation: str, duration_ms: float, threshold_ms: float):
        """Capture slow operations as performance issues"""
        if duration_ms > threshold_ms:
            context = {
                "operation": operation,
                "duration_ms": duration_ms,
                "threshold_ms": threshold_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.capture_message(
                f"Slow operation detected: {operation} took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)",
                level="warning",
                context=context
            )


# Global error tracker instance
error_tracker = ErrorTracker()


# Convenience functions
def capture_exception(error: Exception, context: Optional[Dict[str, Any]] = None, level: str = "error"):
    """Capture an exception"""
    error_tracker.capture_exception(error, context, level)


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None):
    """Capture a message"""
    error_tracker.capture_message(message, level, context)


def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
    """Set user context"""
    error_tracker.set_user(user_id, email, username)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: Optional[Dict] = None):
    """Add a breadcrumb"""
    error_tracker.add_breadcrumb(message, category, level, data)


def track_performance(operation: str, duration_ms: float, threshold_ms: float = 1000):
    """Track operation performance"""
    error_tracker.capture_performance_issue(operation, duration_ms, threshold_ms)
