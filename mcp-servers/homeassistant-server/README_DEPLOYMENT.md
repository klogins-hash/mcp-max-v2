# Home Assistant MCP Server - Railway Deployment

## Deployment Steps

### 1. Set Environment Variables in Railway

In your Railway project, add these environment variables:

```
HOMEASSISTANT_URL=https://f530xzyua6tlmxk3nc0epcqgabztmouj.ui.nabu.casa
HOMEASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiY2JmZGU4NDA3ODM0ODMyOGRkYWJmMGY5ODNjOTRlMCIsImlhdCI6MTc1NTM5NTU4NywiZXhwIjoyMDcwNzU1NTg3fQ.19EaM0_E1Rvc-7UZKzg9cJMJHijWFyLFDB1JefsDGnQ
```

### 2. Deploy to Railway

Option A - Using Railway CLI:
```bash
cd /Users/dp/CascadeProjects/mcp\ max\ v2/mcp-servers/homeassistant-server
railway link
railway up
```

Option B - Using GitHub:
1. Push this directory to a GitHub repository
2. Connect the repo to Railway
3. Railway will auto-deploy on push

### 3. Service Endpoints

Once deployed, your service will have these endpoints:

- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/call` - Call a specific tool
- `POST /mcp` - Raw MCP protocol endpoint

### 4. Example API Calls

**List tools:**
```bash
curl https://your-service.railway.app/tools
```

**Get all states:**
```bash
curl -X POST https://your-service.railway.app/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ha_get_states",
    "arguments": {}
  }'
```

**Turn on a light:**
```bash
curl -X POST https://your-service.railway.app/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ha_call_service",
    "arguments": {
      "domain": "light",
      "service": "turn_on",
      "entity_id": "light.living_room"
    }
  }'
```

### 5. Integration with MCP Hub

Update your MCP Hub registration to use the Railway URL:

```python
# In your hub registration code
register_server({
    "name": "homeassistant",
    "url": "https://your-service.railway.app",
    "endpoints": {
        "mcp": "/mcp",
        "tools": "/tools",
        "call": "/tools/call"
    }
})
```

## Monitoring

- Check Railway dashboard for logs
- Use `/health` endpoint for uptime monitoring
- Railway provides automatic restart on failure

## Security Notes

- Environment variables are encrypted in Railway
- Use Railway's private networking for hub communication
- Consider adding API key authentication for production
