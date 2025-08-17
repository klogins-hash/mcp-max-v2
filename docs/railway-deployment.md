# Railway Deployment Guide for MCP Max v2

## Overview
This guide explains how to deploy MCP Max v2 on Railway with optimal settings for 32 vCPUs and 32GB RAM.

## Architecture for Railway

### Resource Allocation Strategy
- **MCP Hub**: 8GB RAM, 16 Gunicorn workers
- **20 App Servers**: 24GB RAM total (1.2GB average per app)
- **System Reserved**: ~0GB (Railway handles OS overhead)

### Performance Optimizations
1. **Worker Configuration**
   - 16 Gunicorn workers with uvloop
   - 2000 connections per worker
   - Async connection pool of 2000

2. **Memory Management**
   - Each worker limited to 1.5GB
   - Automatic garbage collection tuning
   - Efficient message serialization with orjson

3. **Load Balancing**
   - Least-connections strategy for even distribution
   - Health checks every 10 seconds
   - Automatic failover for unhealthy services

## Deployment Steps

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Deploy the Hub
```bash
cd /path/to/mcp-max-v2
./scripts/deploy-railway.sh
```

### 3. Monitor Performance
```bash
# View logs
railway logs

# Check metrics endpoint
curl https://your-app.railway.app/metrics
```

## Environment Variables

Set these in Railway dashboard or via CLI:

```bash
# Performance
GUNICORN_WORKERS=16
GUNICORN_WORKER_CONNECTIONS=2000
GUNICORN_MAX_REQUESTS=10000

# Memory
GUNICORN_MAX_REQUESTS_JITTER=1000
PYTHON_GC_THRESHOLD=1000

# Monitoring
MCP_HUB_DEBUG=false
MCP_HUB_LOG_LEVEL=INFO
```

## Scaling Considerations

### Vertical Scaling
Railway's 32 vCPU/32GB plan is utilized as:
- CPU: 16 workers × 2 vCPUs = 32 vCPUs
- Memory: 16 workers × 1.5GB + 8GB services = 32GB

### Horizontal Scaling
For more than 20 apps, consider:
1. Multiple Railway services
2. Redis for shared state
3. External load balancer

## Monitoring

### Health Checks
- Hub: `GET /health`
- Metrics: `GET /metrics`
- Services: `GET /services`

### Performance Metrics
Monitor these key metrics:
- Worker CPU usage
- Memory per worker
- Request latency
- Active connections
- Service health status

## Troubleshooting

### High Memory Usage
1. Reduce `GUNICORN_WORKERS`
2. Lower `max_memory_per_worker`
3. Enable aggressive GC

### Connection Errors
1. Increase `GUNICORN_WORKER_CONNECTIONS`
2. Check service health
3. Review load balancer logs

### Slow Response Times
1. Enable uvloop (already configured)
2. Increase worker count
3. Check service-specific bottlenecks
