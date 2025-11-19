"""
Monitoring and Performance Tracking
Prometheus metrics, structured logging, health checks
"""

from fastapi import APIRouter, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import logging
import psutil
import sys
from typing import Dict, Any
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Prometheus Metrics - use try/except to handle duplicates in testing
try:
    REQUEST_COUNT = Counter(
        'realdiag_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
except ValueError:
    # Metric already exists (in testing)
    from prometheus_client import REGISTRY
    REQUEST_COUNT = REGISTRY._names_to_collectors.get('realdiag_requests_total')

try:
    REQUEST_DURATION = Histogram(
        'realdiag_request_duration_seconds',
        'HTTP request duration in seconds',
        ['method', 'endpoint']
    )
except ValueError:
    from prometheus_client import REGISTRY
    REQUEST_DURATION = REGISTRY._names_to_collectors.get('realdiag_request_duration_seconds')

try:
    ACTIVE_REQUESTS = Gauge(
        'realdiag_active_requests',
        'Number of active requests'
    )
except ValueError:
    from prometheus_client import REGISTRY
    ACTIVE_REQUESTS = REGISTRY._names_to_collectors.get('realdiag_active_requests')

try:
    SYMPTOM_SEARCHES = Counter(
        'realdiag_symptom_searches_total',
        'Total symptom searches performed'
    )
except ValueError:
    from prometheus_client import REGISTRY
    SYMPTOM_SEARCHES = REGISTRY._names_to_collectors.get('realdiag_symptom_searches_total')

try:
    DIAGNOSTIC_SESSIONS = Counter(
        'realdiag_diagnostic_sessions_total',
        'Total diagnostic sessions started',
        ['family']
    )
except ValueError:
    from prometheus_client import REGISTRY
    DIAGNOSTIC_SESSIONS = REGISTRY._names_to_collectors.get('realdiag_diagnostic_sessions_total')

try:
    EDUCATION_INTERACTIONS = Counter(
        'realdiag_education_interactions_total',
        'Total education feature interactions',
        ['feature_type']
    )
except ValueError:
    from prometheus_client import REGISTRY
    EDUCATION_INTERACTIONS = REGISTRY._names_to_collectors.get('realdiag_education_interactions_total')

try:
    CPU_USAGE = Gauge(
        'realdiag_cpu_usage_percent',
        'CPU usage percentage'
    )
except ValueError:
    from prometheus_client import REGISTRY
    CPU_USAGE = REGISTRY._names_to_collectors.get('realdiag_cpu_usage_percent')

try:
    MEMORY_USAGE = Gauge(
        'realdiag_memory_usage_bytes',
        'Memory usage in bytes'
    )
except ValueError:
    from prometheus_client import REGISTRY
    MEMORY_USAGE = REGISTRY._names_to_collectors.get('realdiag_memory_usage_bytes')

try:
    DATABASE_OPERATIONS = Counter(
        'realdiag_database_operations_total',
        'Total database operations',
        ['operation_type', 'status']
    )
except ValueError:
    from prometheus_client import REGISTRY
    DATABASE_OPERATIONS = REGISTRY._names_to_collectors.get('realdiag_database_operations_total')


class PerformanceMonitor:
    """Monitor application performance and resource usage"""
    
    @staticmethod
    def update_system_metrics():
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    @staticmethod
    def track_request(method: str, endpoint: str, status_code: int, duration: float):
        """Track request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def track_symptom_search():
        """Track symptom search metrics"""
        SYMPTOM_SEARCHES.inc()
    
    @staticmethod
    def track_diagnostic_session(family: str):
        """Track diagnostic session metrics"""
        DIAGNOSTIC_SESSIONS.labels(family=family).inc()
    
    @staticmethod
    def track_education_interaction(feature_type: str):
        """Track education feature usage"""
        EDUCATION_INTERACTIONS.labels(feature_type=feature_type).inc()
    
    @staticmethod
    def track_database_operation(operation_type: str, status: str = "success"):
        """Track database operations"""
        DATABASE_OPERATIONS.labels(operation_type=operation_type, status=status).inc()


class StructuredLogger:
    """Structured logging with context"""
    
    @staticmethod
    def log_request(request: Request, duration: float, status_code: int):
        """Log HTTP request with structured data"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        logger.info(f"HTTP Request: {log_data}")
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        logger.error(f"Error: {log_data}")
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log security-related events"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if severity == "CRITICAL":
            logger.critical(f"Security Event: {log_data}")
        elif severity == "WARNING":
            logger.warning(f"Security Event: {log_data}")
        else:
            logger.info(f"Security Event: {log_data}")
    
    @staticmethod
    def log_performance_warning(metric: str, value: float, threshold: float):
        """Log performance warnings"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": "WARNING"
        }
        logger.warning(f"Performance Warning: {log_data}")


# Middleware for performance tracking
async def performance_middleware(request: Request, call_next):
    """Middleware to track request performance"""
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Track metrics
        PerformanceMonitor.track_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        # Log request
        StructuredLogger.log_request(request, duration, response.status_code)
        
        # Check for slow requests
        if duration > 1.0:  # More than 1 second
            StructuredLogger.log_performance_warning(
                metric="request_duration",
                value=duration,
                threshold=1.0
            )
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        StructuredLogger.log_error(e, {"path": request.url.path, "method": request.method})
        raise
    
    finally:
        ACTIVE_REQUESTS.dec()
        PerformanceMonitor.update_system_metrics()


# Health Check Endpoints
@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    PerformanceMonitor.update_system_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/health/detailed")
async def health_detailed() -> Dict[str, Any]:
    """Detailed health check with system metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Python runtime info
        python_version = sys.version
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent
                }
            },
            "runtime": {
                "python_version": python_version.split()[0],
                "uptime_seconds": int(time.time() - psutil.boot_time())
            },
            "checks": {
                "cpu_ok": cpu_percent < 90,
                "memory_ok": memory.percent < 90,
                "disk_ok": disk.percent < 90
            }
        }
        
        # Overall health status
        all_checks_ok = all(health_data["checks"].values())
        health_data["status"] = "healthy" if all_checks_ok else "degraded"
        
        return health_data
    
    except Exception as e:
        StructuredLogger.log_error(e, {"endpoint": "/health/detailed"})
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/liveness")
async def liveness() -> Dict[str, bool]:
    """Kubernetes liveness probe - is the app running?"""
    return {"alive": True}


@router.get("/health/readiness")
async def readiness() -> Dict[str, Any]:
    """Kubernetes readiness probe - is the app ready to serve traffic?"""
    try:
        # Check critical dependencies
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Ready if resources are available
        ready = cpu_percent < 95 and memory.percent < 95
        
        return {
            "ready": ready,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent
        }
    
    except Exception as e:
        return {
            "ready": False,
            "error": str(e)
        }
