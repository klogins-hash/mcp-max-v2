# MCP Max v2

A scalable MCP (Model Context Protocol) server architecture for connecting 20+ applications.

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-max-v2.git
   cd mcp-max-v2
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
mcp-max-v2/
├── mcp-hub/                    # Central MCP orchestrator
│   ├── src/
│   │   ├── __init__.py
│   │   ├── router.py          # Request routing logic
│   │   ├── registry.py        # Service discovery & registration
│   │   ├── auth.py            # Authentication middleware
│   │   └── config.py          # Configuration management
│   ├── tests/
│   └── requirements.txt
│
├── mcp-servers/                # Individual MCP servers for each app
│   ├── template/              # Template for new servers
│   │   ├── server.py
│   │   ├── handlers.py
│   │   ├── manifest.json
│   │   └── README.md
│   ├── app1-server/
│   ├── app2-server/
│   └── ... (18 more servers)
│
├── shared/                     # Shared libraries and utilities
│   ├── protocols/             # Common protocol definitions
│   │   ├── __init__.py
│   │   ├── base.py           # Base protocol classes
│   │   └── messages.py       # Message types
│   ├── auth/                  # Shared authentication
│   └── utils/                 # Common utilities
│
├── deployment/                 # Deployment configurations
│   ├── docker/
│   │   ├── Dockerfile.hub
│   │   └── Dockerfile.server
│   ├── kubernetes/            # K8s manifests
│   └── docker-compose.yml     # Local development
│
├── monitoring/                 # Monitoring and observability
│   ├── prometheus/
│   └── grafana/
│
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── api-reference.md
│   └── deployment-guide.md
│
├── scripts/                    # Utility scripts
│   ├── create-server.py       # Generate new server from template
│   └── test-all.sh           # Run all tests
│
├── .gitignore
├── README.md
└── requirements-dev.txt       # Development dependencies
```

## Architecture Overview

### Hub-and-Spoke Model
The MCP Hub acts as a central orchestrator that:
- Routes requests to appropriate MCP servers
- Manages service discovery and health checks
- Handles authentication and authorization
- Provides load balancing and failover

### Benefits
- **Scalability**: Each app server can scale independently
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to add/remove apps
- **Monitoring**: Centralized logging and metrics

## Development

### Creating a New MCP Server
```bash
python scripts/create-server.py --name app21-server
```

### Running the Hub
```bash
cd mcp-hub
python -m src.main
```

### Running Tests
```bash
# Test everything
./scripts/test-all.sh

# Test specific server
pytest mcp-servers/app1-server/tests/
```

### Local Development with Docker
```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up mcp-hub app1-server app2-server
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
