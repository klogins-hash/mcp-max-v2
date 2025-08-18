# MCP Server Deployment Architecture on Railway

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Railway Project                          │
│                      (mcp-max-v2)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌──────────────────────────┐ │
│  │   MCP Hub       │         │   Shared Resources       │ │
│  │  (mcp-max-v2)   │         │  - Redis (caching)       │ │
│  │   Port: 8000    │◄────────┤  - PostgreSQL (state)    │ │
│  │  16 workers     │         │  - Monitoring (Grafana)  │ │
│  └────────┬────────┘         └──────────────────────────┘ │
│           │                                                 │
│     ┌─────┴──────┬──────────┬──────────┬─────────┐        │
│     │            │          │          │         │        │
│  ┌──▼───┐  ┌────▼───┐  ┌───▼───┐  ┌──▼───┐  ┌──▼───┐   │
│  │Server│  │Server  │  │Server │  │Server│  │Server│   │
│  │  A   │  │   B    │  │   C   │  │  D   │  │  ...  │   │
│  └──────┘  └────────┘  └───────┘  └──────┘  └──────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
mcp-max-v2/
├── mcp-hub/                    # Central hub service
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── mcp-servers/                # All MCP server implementations
│   ├── spotify-server/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── railway.json
│   │
│   ├── github-server/
│   │   ├── server.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── railway.json
│   │
│   └── [category]-[tool]-server/
│       └── ...
│
├── shared/                     # Shared utilities and configs
│   ├── mcp_base/              # Base MCP server class
│   ├── auth/                  # Shared authentication
│   └── utils/                 # Common utilities
│
├── deployment/                 # Deployment configurations
│   ├── railway/
│   │   ├── hub.railway.json
│   │   └── servers/
│   │       ├── spotify.railway.json
│   │       └── ...
│   │
│   └── scripts/
│       ├── deploy-all.sh
│       ├── deploy-server.sh
│       └── health-check.sh
│
└── docs/
    ├── DEPLOYMENT.md
    ├── SERVER_TEMPLATE.md
    └── TROUBLESHOOTING.md
```

## 🏷️ Naming Conventions

### Service Names in Railway
- **Hub**: `mcp-hub-prod`
- **Servers**: `mcp-[category]-[tool]-prod`
  - Examples:
    - `mcp-music-spotify-prod`
    - `mcp-dev-github-prod`
    - `mcp-ai-openai-prod`
    - `mcp-data-postgres-prod`

### Environment Variable Prefixes
- **Global**: `MCP_`
- **Hub-specific**: `MCP_HUB_`
- **Server-specific**: `MCP_[CATEGORY]_[TOOL]_`

## 🔧 Environment Variables Strategy

### Shared Variables (Set at Project Level)
```env
# Core Configuration
MCP_ENV=production
MCP_LOG_LEVEL=info
MCP_HUB_URL=https://mcp-hub-prod.up.railway.app

# Authentication
MCP_AUTH_SECRET=shared-secret-key

# Monitoring
MCP_METRICS_ENABLED=true
MCP_METRICS_PORT=9090
```

### Hub Variables
```env
MCP_HUB_PORT=8000
MCP_HUB_WORKERS=16
MCP_HUB_REDIS_URL=${{Redis.REDIS_URL}}
MCP_HUB_DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Server-Specific Variables
```env
# Spotify Server
MCP_MUSIC_SPOTIFY_CLIENT_ID=xxx
MCP_MUSIC_SPOTIFY_CLIENT_SECRET=xxx
MCP_MUSIC_SPOTIFY_REDIRECT_URI=xxx

# GitHub Server
MCP_DEV_GITHUB_TOKEN=xxx
MCP_DEV_GITHUB_ORG=xxx
```

## 🚀 Deployment Strategy

### 1. Service Grouping by Category
- **Development Tools**: GitHub, GitLab, Jira
- **AI/ML Services**: OpenAI, Anthropic, Cohere
- **Data Services**: PostgreSQL, MongoDB, Redis
- **Communication**: Slack, Discord, Email
- **Productivity**: Notion, Linear, Asana
- **Media**: Spotify, YouTube, Unsplash

### 2. Resource Allocation
```yaml
Hub:
  CPU: 4 vCPU
  Memory: 8GB
  Replicas: 2-4

High-Traffic Servers (OpenAI, GitHub):
  CPU: 2 vCPU
  Memory: 2GB
  Replicas: 2

Standard Servers:
  CPU: 1 vCPU
  Memory: 1GB
  Replicas: 1

Low-Traffic Servers:
  CPU: 0.5 vCPU
  Memory: 512MB
  Replicas: 1
```

### 3. Health Monitoring
- Each server exposes `/health` endpoint
- Hub monitors all servers every 30s
- Automatic restart on 3 consecutive failures
- Alerts via Discord/Slack webhook

## 📊 Service Discovery & Registration

### Automatic Registration
```python
# Each server auto-registers on startup
async def register_with_hub():
    await hub_client.register({
        "name": "spotify-server",
        "category": "music",
        "endpoint": os.getenv("RAILWAY_PUBLIC_DOMAIN"),
        "capabilities": ["play", "pause", "search"],
        "health_check": "/health"
    })
```

### Service Mesh Benefits
- Automatic failover
- Load balancing
- Circuit breaking
- Request retry

## 🔐 Security Considerations

1. **Inter-Service Communication**
   - Use Railway's private networking
   - mTLS between services
   - Rotate auth tokens monthly

2. **External API Keys**
   - Store in Railway variables
   - Use separate keys per environment
   - Implement key rotation

3. **Rate Limiting**
   - Hub-level rate limiting
   - Per-server quotas
   - User-based throttling

## 📈 Scaling Strategy

### Horizontal Scaling
- Add server replicas for high-traffic services
- Use Railway's autoscaling features
- Load balance at hub level

### Vertical Scaling
- Monitor memory/CPU usage
- Scale individual services as needed
- Keep hub well-provisioned

## 🛠️ Maintenance & Updates

### Zero-Downtime Deployments
1. Deploy new version alongside old
2. Health check new version
3. Gradually shift traffic
4. Remove old version

### Rollback Strategy
- Tag all deployments
- Keep 3 previous versions
- One-command rollback script

## 📝 Best Practices

1. **Consistent Logging**
   - JSON structured logs
   - Include trace IDs
   - Log to centralized system

2. **Error Handling**
   - Graceful degradation
   - Retry with exponential backoff
   - Circuit breakers for external APIs

3. **Documentation**
   - README for each server
   - API documentation
   - Deployment runbooks

4. **Testing**
   - Unit tests for each server
   - Integration tests with hub
   - Load testing for scaling

## 🚦 Deployment Checklist

- [ ] Create service in Railway
- [ ] Set environment variables
- [ ] Configure resource limits
- [ ] Set up health checks
- [ ] Enable monitoring
- [ ] Test registration with hub
- [ ] Verify in Claude desktop config
- [ ] Document in service registry
