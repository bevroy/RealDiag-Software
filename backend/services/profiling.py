"""
Performance Profiling Middleware
Identifies bottlenecks and slow endpoints
"""

import time
import cProfile
import pstats
import io
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class PerformanceProfiler(BaseHTTPMiddleware):
    """Middleware to profile request performance"""
    
    def __init__(self, app, threshold_ms: float = 1000, enable_detailed: bool = False):
        super().__init__(app)
        self.threshold_ms = threshold_ms
        self.enable_detailed = enable_detailed
        self.slow_requests = []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Profile each request"""
        start_time = time.time()
        
        # Enable detailed profiling if configured
        if self.enable_detailed:
            profiler = cProfile.Profile()
            profiler.enable()
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log slow requests
            if duration_ms > self.threshold_ms:
                slow_request = {
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": round(duration_ms, 2),
                    "timestamp": time.time()
                }
                self.slow_requests.append(slow_request)
                
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} "
                    f"took {duration_ms:.2f}ms (threshold: {self.threshold_ms}ms)"
                )
                
                # Detailed profiling for very slow requests
                if self.enable_detailed and duration_ms > self.threshold_ms * 2:
                    profiler.disable()
                    s = io.StringIO()
                    stats = pstats.Stats(profiler, stream=s)
                    stats.sort_stats('cumulative')
                    stats.print_stats(20)  # Top 20 functions
                    
                    logger.info(f"Profiling data for {request.url.path}:\n{s.getvalue()}")
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Request failed after {duration_ms:.2f}ms: {e}")
            raise
    
    def get_slow_requests(self, limit: int = 50) -> list:
        """Get list of slow requests"""
        return sorted(
            self.slow_requests[-limit:],
            key=lambda x: x["duration_ms"],
            reverse=True
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.slow_requests:
            return {
                "total_slow_requests": 0,
                "message": "No slow requests detected"
            }
        
        durations = [r["duration_ms"] for r in self.slow_requests]
        
        return {
            "total_slow_requests": len(self.slow_requests),
            "average_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "threshold_ms": self.threshold_ms,
            "slowest_endpoints": self._get_slowest_endpoints()
        }
    
    def _get_slowest_endpoints(self, top_n: int = 10) -> list:
        """Get slowest endpoints"""
        endpoint_stats = {}
        
        for request in self.slow_requests:
            key = f"{request['method']} {request['path']}"
            if key not in endpoint_stats:
                endpoint_stats[key] = {
                    "endpoint": key,
                    "count": 0,
                    "total_duration": 0,
                    "max_duration": 0
                }
            
            stats = endpoint_stats[key]
            stats["count"] += 1
            stats["total_duration"] += request["duration_ms"]
            stats["max_duration"] = max(stats["max_duration"], request["duration_ms"])
        
        # Calculate averages and sort
        for stats in endpoint_stats.values():
            stats["avg_duration_ms"] = stats["total_duration"] / stats["count"]
        
        return sorted(
            endpoint_stats.values(),
            key=lambda x: x["avg_duration_ms"],
            reverse=True
        )[:top_n]


# Database query profiler
class QueryProfiler:
    """Profile database queries"""
    
    def __init__(self):
        self.queries = []
    
    def log_query(self, query_type: str, duration_ms: float, details: Dict[str, Any] = None):
        """Log a database query"""
        query_log = {
            "type": query_type,
            "duration_ms": duration_ms,
            "timestamp": time.time(),
            "details": details or {}
        }
        self.queries.append(query_log)
        
        # Warn on slow queries
        if duration_ms > 100:  # 100ms threshold
            logger.warning(
                f"Slow query detected: {query_type} took {duration_ms:.2f}ms"
            )
    
    def get_query_summary(self) -> Dict[str, Any]:
        """Get query performance summary"""
        if not self.queries:
            return {"total_queries": 0}
        
        durations = [q["duration_ms"] for q in self.queries]
        
        return {
            "total_queries": len(self.queries),
            "average_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "slow_queries_count": sum(1 for d in durations if d > 100)
        }


# Memory profiler
class MemoryProfiler:
    """Profile memory usage"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get current memory usage"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024),
            "percent": process.memory_percent()
        }
    
    @staticmethod
    def log_memory_usage(context: str = ""):
        """Log current memory usage"""
        usage = MemoryProfiler.get_memory_usage()
        logger.info(
            f"Memory usage {context}: "
            f"RSS={usage['rss_mb']:.2f}MB, "
            f"VMS={usage['vms_mb']:.2f}MB, "
            f"Percent={usage['percent']:.2f}%"
        )


# Global instances
query_profiler = QueryProfiler()
memory_profiler = MemoryProfiler()
