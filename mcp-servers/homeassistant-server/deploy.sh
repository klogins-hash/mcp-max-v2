#!/bin/bash

# Deploy Home Assistant MCP Server to Railway

echo "🚀 Deploying Home Assistant MCP Server to Railway..."

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   brew install railway"
    exit 1
fi

# Navigate to the server directory
cd "$(dirname "$0")"

# Check if already linked to a Railway project
if [ ! -f ".railway/config.json" ]; then
    echo "📎 Linking to Railway project..."
    railway link
else
    echo "✅ Already linked to Railway project"
fi

# Deploy to Railway
echo "📦 Deploying to Railway..."
railway up -d

echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your Railway dashboard to monitor the deployment"
echo "2. Set the environment variables in Railway:"
echo "   - HOMEASSISTANT_URL"
echo "   - HOMEASSISTANT_TOKEN"
echo "3. Check the deployment logs for the service URL"
echo ""
echo "🔗 Your service will be available at: https://<service-name>.railway.app"
