#!/bin/bash

# Deploy to Railway via GitHub

echo "Setting up GitHub repository for Railway deployment..."

# Initialize git if not already
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: MCP Max v2 with 20+ MCP servers"
fi

# Create GitHub repo using gh CLI
echo "Creating GitHub repository..."
gh repo create mcp-max-v2 --public --source=. --remote=origin --push

# Push to GitHub
git push -u origin main

echo "Repository pushed to GitHub!"
echo "Now follow these steps:"
echo "1. Go to https://railway.app/new"
echo "2. Click 'Deploy from GitHub repo'"
echo "3. Select the 'mcp-max-v2' repository"
echo "4. Railway will automatically detect the Python app and deploy it"
echo ""
echo "Railway will use the railpack.json configuration we created for optimal deployment."
