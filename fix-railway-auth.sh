#!/bin/bash

# Fix Railway authentication and deploy
echo "🔧 Setting up Railway authentication..."

# Create Railway config directory if it doesn't exist
mkdir -p ~/.config/railway

# Create auth config with your token
cat > ~/.config/railway/config.json << EOF
{
  "token": "ce03376f-6cf9-43ea-b678-12055cc20a7c",
  "project": "08459bbc-9b07-4212-b80d-a5e9372a412c",
  "environment": "production"
}
EOF

echo "✅ Railway config created"

# Test authentication
railway whoami

# If successful, deploy
if [ $? -eq 0 ]; then
    echo "🚀 Authentication successful! Deploying..."
    railway up --detach
else
    echo "❌ Authentication still failing. Trying alternative method..."
    
    # Alternative: Use railway.json config
    cat > railway.json << EOF
{
  "projectId": "08459bbc-9b07-4212-b80d-a5e9372a412c",
  "environmentId": "b349c7bb-4112-4408-978c-b38190e424d3"
}
EOF
    
    # Try deployment with project config
    RAILWAY_TOKEN=ce03376f-6cf9-43ea-b678-12055cc20a7c railway up --detach
fi
