#!/bin/bash

# Simple Railway deployment using API token

export RAILWAY_API_TOKEN="fJgWTDcdLr2T1T8Y8u5vQPMH"

echo "Deploying to Railway with API token..."

# Create a new project and deploy
railway init --name mcp-max-v2
railway up --detach
