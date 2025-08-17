#!/bin/bash

# Railway deployment script that works with token
set -e

echo "🚀 Deploying MCP Max v2 to Railway..."

# Use the project ID we just created
PROJECT_ID="08459bbc-9b07-4212-b80d-a5e9372a412c"
RAILWAY_TOKEN="ce03376f-6cf9-43ea-b678-12055cc20a7c"

# Export token
export RAILWAY_TOKEN=$RAILWAY_TOKEN

# Link to the project we created
echo "🔗 Linking to Railway project..."
railway link $PROJECT_ID --environment production

# Deploy
echo "🚂 Deploying..."
railway up --detach

echo "✅ Deployment started!"
echo "📊 Check status: railway logs"
echo "🌐 Get URL: railway domain"
