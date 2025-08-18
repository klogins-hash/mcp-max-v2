# Railway Deployment Instructions

## Create a New Service in Railway

1. Go to your Railway project dashboard: https://railway.app/project/08459bbc-9b07-4212-b80d-a5e9372a412c

2. Click "New Service" → "GitHub Repo" or "Empty Service"

3. If using GitHub:
   - Connect this directory as a new repo
   - Railway will auto-deploy

4. If using Empty Service:
   - Name it: `homeassistant-mcp-server`
   - Then use Railway CLI:
   ```bash
   railway link
   railway service homeassistant-mcp-server
   railway up
   ```

## Set Environment Variables

In the Railway dashboard for the new service, add:

```
HOMEASSISTANT_URL=https://f530xzyua6tlmxk3nc0epcqgabztmouj.ui.nabu.casa
HOMEASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiY2JmZGU4NDA3ODM0ODMyOGRkYWJmMGY5ODNjOTRlMCIsImlhdCI6MTc1NTM5NTU4NywiZXhwIjoyMDcwNzU1NTg3fQ.19EaM0_E1Rvc-7UZKzg9cJMJHijWFyLFDB1JefsDGnQ
```

## Service URL

Once deployed, your service will be available at:
`https://homeassistant-mcp-server-production.up.railway.app`

## Test the Service

```bash
# Health check
curl https://homeassistant-mcp-server-production.up.railway.app/health

# List tools
curl https://homeassistant-mcp-server-production.up.railway.app/tools
```
