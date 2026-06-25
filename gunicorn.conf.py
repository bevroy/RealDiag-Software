# Gunicorn configuration for RealDiag - Optimized for Performance
import multiprocessing
import os

# Server Socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker Processes
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 1000  # Add randomness to prevent all workers restarting at once

# Timeouts
timeout = 120  # 2 minutes for long-running requests
keepalive = 5  # Keep connections alive for 5 seconds
graceful_timeout = 30  # Give workers 30 seconds to finish requests before killing

# Performance
preload_app = True  # Load application before forking workers (faster startup)
reuse_port = True  # Use SO_REUSEPORT for better load distribution

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log errors to stdout
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "realdiag"

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Enable async workers for better I/O performance
threads = 4  # 4 threads per worker for handling concurrent requests

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 RealDiag server starting...")
    server.log.info(f"📊 Configuration: {workers} workers, {threads} threads/worker")
    server.log.info(f"⚡ Preload: {preload_app}, Reuse Port: {reuse_port}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("♻️  Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ RealDiag server ready to accept connections")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"👷 Worker {worker.pid} received INT/QUIT signal")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info(f"⚠️  Worker {worker.pid} aborted")
