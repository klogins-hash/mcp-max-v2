#!/bin/bash
set -e

echo "Starting MCP Hub on Railway..."
echo "Environment: ${RAILWAY_ENVIRONMENT:-development}"
echo "Workers: ${GUNICORN_WORKERS:-16}"
echo "Port: ${PORT:-8000}"

# Export Railway environment variables
export PYTHONPATH=/app:$PYTHONPATH

# Start with gunicorn using config file
exec gunicorn mcp-hub.main:app -c gunicorn.conf.py
