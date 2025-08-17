#!/bin/bash
# Railway deployment script for MCP Max v2

set -e

echo "🚀 Deploying MCP Max v2 to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Set Railway token
export RAILWAY_TOKEN="ce03376f-6cf9-43ea-b678-12055cc20a7c"

# Login to Railway
echo "📝 Using Railway API token..."

# Create or link to project
echo "🔗 Creating Railway project..."
railway init --name "mcp-max-v2" || railway link

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set MCP_HUB_PORT=8000
railway variables set GUNICORN_WORKERS=16
railway variables set GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
railway variables set GUNICORN_WORKER_CONNECTIONS=2000
railway variables set PYTHONUNBUFFERED=1
railway variables set PYTHONDONTWRITEBYTECODE=1

# Deploy
echo "🚂 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "📊 View logs: railway logs"
echo "🌐 Open app: railway open"
