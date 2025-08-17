# Quick Deploy to Railway

## Prerequisites
- Railway CLI: `npm install -g @railway/cli`
- Python packages: `pip install requests toml`

## Deploy Steps

### Option 1: Automated Setup (Recommended)
```bash
cd /Users/dp/CascadeProjects/mcp\ max\ v2
python scripts/setup-railway-project.py
railway up
```

### Option 2: Manual Deploy
```bash
cd /Users/dp/CascadeProjects/mcp\ max\ v2
export RAILWAY_TOKEN="ce03376f-6cf9-43ea-b678-12055cc20a7c"
railway init --name "mcp-max-v2"
./scripts/deploy-railway.sh
```

## Post-Deployment

1. **Check deployment status**:
   ```bash
   railway logs
   ```

2. **Get deployment URL**:
   ```bash
   railway open
   ```

3. **Monitor health**:
   ```bash
   curl https://your-app.railway.app/health
   ```

## Resource Usage
- CPU: 32 vCPUs (16 workers × 2 vCPUs)
- Memory: 32GB (8GB hub + 24GB services)
- Connections: 32,000 concurrent (16 workers × 2000)

## Next Steps
After deployment, register your 20 app servers:
```bash
curl -X POST https://your-app.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "app1-server",
    "host": "app1.railway.internal",
    "port": 8001,
    "capabilities": ["capability1", "capability2"]
  }'
```
