#!/bin/bash

# Deploy a single MCP server to Railway
# Usage: ./deploy-mcp-server.sh <server-name> [environment]

SERVER_NAME=$1
ENVIRONMENT=${2:-production}

if [ -z "$SERVER_NAME" ]; then
    echo "Usage: ./deploy-mcp-server.sh <server-name> [environment]"
    echo "Example: ./deploy-mcp-server.sh spotify production"
    exit 1
fi

SERVER_DIR="mcp-servers/${SERVER_NAME}-server"

if [ ! -d "$SERVER_DIR" ]; then
    echo "Error: Server directory $SERVER_DIR does not exist"
    exit 1
fi

echo "🚀 Deploying MCP ${SERVER_NAME} server to Railway..."

# Navigate to server directory
cd "$SERVER_DIR"

# Create Railway service name
SERVICE_NAME="mcp-${SERVER_NAME}-${ENVIRONMENT}"

# Link to Railway project
railway link mcp-max-v2

# Create or switch to service
railway service create "$SERVICE_NAME" 2>/dev/null || railway service "$SERVICE_NAME"

# Deploy
railway up --detach

echo "✅ Deployed $SERVICE_NAME successfully!"
echo "🔗 Service URL: $(railway status --json | jq -r '.url')"

# Register with hub
cd ../..
python3 "mcp-servers/${SERVER_NAME}-server/register.py"

echo "📝 Registered with MCP Hub"
