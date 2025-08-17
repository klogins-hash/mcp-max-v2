# Railway Deployment Instructions for MCP Max v2

Since the Railway CLI authentication is having issues, here's how to deploy via the Railway dashboard:

## Step 1: Push to GitHub

First, create a GitHub repository and push your code:

```bash
git init
git add .
git commit -m "Initial commit: MCP Max v2 with 20+ MCP servers"

# Create repo on GitHub manually or use gh CLI if available
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/mcp-max-v2.git
git push -u origin main
```

## Step 2: Deploy on Railway Dashboard

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Connect your GitHub account if not already connected
4. Select the `mcp-max-v2` repository
5. Railway will automatically detect the Python app

## Step 3: Configure Environment Variables

In the Railway dashboard, go to your service settings and add these environment variables:

```
PORT=8000
GUNICORN_WORKERS=16
GUNICORN_WORKER_CONNECTIONS=2000
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

## Step 4: Railway Configuration

Railway will use the `railpack.json` file we created, which optimizes the build:

- Python 3.11 runtime
- Gunicorn with uvloop for high performance
- 16 workers optimized for 32 vCPUs
- Proper virtual environment setup

## Step 5: Monitor Deployment

Once deployed, you can:
- View logs in the Railway dashboard
- Access the health endpoint at `https://YOUR_APP.railway.app/health`
- Monitor metrics at `https://YOUR_APP.railway.app/metrics`

## Alternative: Direct Upload

If you don't want to use GitHub:

1. Go to https://railway.app/new
2. Click "Deploy from local directory"
3. Drag and drop your project folder
4. Railway will build and deploy automatically

## API Token Information

Your Railway API token: `ce03376f-6cf9-43ea-b678-12055cc20a7c`

This token can be used for:
- CI/CD pipelines
- Automated deployments
- Railway CLI operations (once authentication is fixed)

## Project Structure Ready for Deployment

✅ `requirements.txt` - Python dependencies
✅ `railpack.json` - Railway build configuration
✅ `mcp-hub/main.py` - FastAPI application entry point
✅ Optimized for 32 vCPUs and 32GB RAM
✅ Hub-and-spoke architecture for 20+ MCP servers
