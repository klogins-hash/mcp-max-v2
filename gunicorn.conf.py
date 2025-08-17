import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 2000
max_requests = 10000
max_requests_jitter = 1000
timeout = 120
keepalive = 5
threads = 4

# Restart workers after this many requests, with some variability
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'mcp-hub'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for memory efficiency
preload_app = True

# Enable StatsD metrics
statsd_host = 'localhost:8125'
statsd_prefix = 'mcp_hub'

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
