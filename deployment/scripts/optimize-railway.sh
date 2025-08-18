#!/bin/bash
# Optimize MCP Max v2 for Railway deployment

set -e

echo "🚀 Optimizing MCP Max v2 for Railway deployment..."

# Create optimized gunicorn config
cat > gunicorn.conf.py << 'EOF'
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
EOF

echo "✅ Created optimized gunicorn configuration"

# Update requirements.txt with Railway optimizations
cat > requirements.txt << 'EOF'
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
uvloop==0.19.0
httptools==0.6.1
aiohttp==3.9.1
pydantic==2.5.0
python-multipart==0.0.6

# Performance monitoring
prometheus-client==0.19.0
psutil==5.9.6

# MCP dependencies
mcp==0.1.0
websockets==12.0

# Async utilities
asyncio==3.4.3
aiofiles==23.2.1

# JSON handling
orjson==3.9.10
ujson==5.8.0

# Railway optimizations
gevent==23.9.1
greenlet==3.0.1
EOF

echo "✅ Updated requirements.txt with optimized dependencies"

# Create Railway-specific environment file
cat > .env.railway << 'EOF'
# Railway Production Environment
RAILWAY_ENVIRONMENT=production
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONOPTIMIZE=1

# Performance settings
GUNICORN_WORKERS=16
GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
GUNICORN_WORKER_CONNECTIONS=2000
GUNICORN_MAX_REQUESTS=10000
GUNICORN_MAX_REQUESTS_JITTER=1000

# MCP Hub settings
MCP_HUB_HOST=0.0.0.0
MCP_HUB_PORT=8000
MCP_HUB_LOG_LEVEL=INFO
MCP_HUB_ENABLE_METRICS=true
MCP_HUB_HEARTBEAT_INTERVAL=30
MCP_HUB_HEALTH_CHECK_INTERVAL=60
MCP_HUB_LOAD_BALANCER_STRATEGY=least_connections

# Resource allocation
MCP_HUB_MEMORY_LIMIT=8192
MCP_SERVICE_MEMORY_LIMIT=1200
MCP_MAX_SERVICES=20
EOF

echo "✅ Created Railway environment configuration"

# Create startup script
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting MCP Hub on Railway..."
echo "Environment: ${RAILWAY_ENVIRONMENT:-development}"
echo "Workers: ${GUNICORN_WORKERS:-16}"
echo "Port: ${PORT:-8000}"

# Export Railway environment variables
export PYTHONPATH=/app:$PYTHONPATH

# Start with gunicorn using config file
exec gunicorn mcp_hub.main:app -c gunicorn.conf.py
EOF

chmod +x start.sh

echo "✅ Created startup script"

# Update Dockerfile CMD to use startup script
sed -i.bak 's|CMD \["gunicorn".*|CMD ["./start.sh"]|' deployment/docker/Dockerfile.railway

echo "🎉 Railway optimization complete!"
echo ""
echo "Next steps:"
echo "1. Review the optimized configuration"
echo "2. Test locally with: docker-compose -f deployment/docker/docker-compose.railway.yml up"
echo "3. Deploy to Railway"
EOF

chmod +x deployment/scripts/optimize-railway.sh
