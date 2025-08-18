# Railway Admin MCP Server

A comprehensive Model Context Protocol (MCP) server for managing Railway infrastructure.

## Features

- **Project Management**: List and view Railway projects
- **Service Control**: List services, view logs, restart services
- **Deployment Management**: View deployments, trigger redeployments
- **Environment Variables**: Set and delete environment variables
- **Metrics Monitoring**: View CPU, memory, network, and disk metrics
- **Service Logs**: Access deployment logs with configurable limits

## Available Tools

### Project Management
- `list_projects` - List all Railway projects
- `get_project` - Get details of a specific project

### Service Management
- `list_services` - List services in a project
- `get_service_logs` - Get logs for a service
- `restart_service` - Restart a service
- `get_service_metrics` - Get service metrics (CPU, memory, network, disk)

### Deployment Control
- `get_deployments` - List deployments for a service
- `redeploy_service` - Trigger a redeployment

### Environment Variables
- `set_environment_variable` - Set an environment variable
- `delete_environment_variable` - Delete an environment variable

## Setup

1. Set the `RAILWAY_API_TOKEN` environment variable:
   ```bash
   export RAILWAY_API_TOKEN="your-railway-api-token"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python server.py
   ```

## Docker Usage

Build and run with Docker:
```bash
docker build -t railway-admin-mcp .
docker run -e RAILWAY_API_TOKEN="your-token" railway-admin-mcp
```

## Integration with MCP Hub

To register with the MCP Hub:
```bash
python register.py
```
