#!/usr/bin/env python3
"""
Railway Admin MCP Server
Provides comprehensive Railway platform management via MCP protocol
"""

import asyncio
import json
import sys
import os
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailwayAPIClient:
    """Async client for Railway GraphQL API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://backboard.railway.app/graphql/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
            
        async with self.session.post(self.base_url, headers=self.headers, json=payload) as response:
            response.raise_for_status()
            result = await response.json()
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            return result.get("data", {})

class RailwayMCPServer:
    """MCP Server for Railway administration"""
    
    def __init__(self):
        self.railway_token = os.environ.get("RAILWAY_API_TOKEN")
        if not self.railway_token:
            raise ValueError("RAILWAY_API_TOKEN environment variable is required")
        self.client = None
        
    async def initialize(self):
        """Initialize the server"""
        self.client = await RailwayAPIClient(self.railway_token).__aenter__()
        logger.info("Railway MCP Server initialized")
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            else:
                return self.error_response(request_id, -32601, "Method not found")
                
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self.error_response(request_id, -32603, str(e))
    
    def error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
    
    async def list_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": "list_projects",
                    "description": "List all Railway projects",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_project",
                    "description": "Get details of a specific project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Railway project ID"
                            }
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "list_services",
                    "description": "List services in a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Railway project ID"
                            }
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "get_service_logs",
                    "description": "Get logs for a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "Railway service ID"
                            },
                            "deployment_id": {
                                "type": "string",
                                "description": "Deployment ID (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of log lines to retrieve",
                                "default": 100
                            }
                        },
                        "required": ["service_id"]
                    }
                },
                {
                    "name": "get_deployments",
                    "description": "List deployments for a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "Railway service ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            }
                        },
                        "required": ["service_id"]
                    }
                },
                {
                    "name": "redeploy_service",
                    "description": "Trigger a redeployment of a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "Railway service ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            }
                        },
                        "required": ["service_id", "environment_id"]
                    }
                },
                {
                    "name": "set_environment_variable",
                    "description": "Set an environment variable for a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Railway project ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            },
                            "service_id": {
                                "type": "string",
                                "description": "Service ID (optional, for service-specific vars)"
                            },
                            "name": {
                                "type": "string",
                                "description": "Variable name"
                            },
                            "value": {
                                "type": "string",
                                "description": "Variable value"
                            }
                        },
                        "required": ["project_id", "environment_id", "name", "value"]
                    }
                },
                {
                    "name": "delete_environment_variable",
                    "description": "Delete an environment variable",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Railway project ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            },
                            "service_id": {
                                "type": "string",
                                "description": "Service ID (optional)"
                            },
                            "name": {
                                "type": "string",
                                "description": "Variable name"
                            }
                        },
                        "required": ["project_id", "environment_id", "name"]
                    }
                },
                {
                    "name": "get_service_metrics",
                    "description": "Get metrics for a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "Railway service ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            }
                        },
                        "required": ["service_id", "environment_id"]
                    }
                },
                {
                    "name": "restart_service",
                    "description": "Restart a service",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_id": {
                                "type": "string",
                                "description": "Railway service ID"
                            },
                            "environment_id": {
                                "type": "string",
                                "description": "Environment ID"
                            }
                        },
                        "required": ["service_id", "environment_id"]
                    }
                }
            ]
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Any:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        tool_map = {
            "list_projects": self.list_projects,
            "get_project": self.get_project,
            "list_services": self.list_services,
            "get_service_logs": self.get_service_logs,
            "get_deployments": self.get_deployments,
            "redeploy_service": self.redeploy_service,
            "set_environment_variable": self.set_environment_variable,
            "delete_environment_variable": self.delete_environment_variable,
            "get_service_metrics": self.get_service_metrics,
            "restart_service": self.restart_service
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        return await tool_map[tool_name](**arguments)
    
    async def list_projects(self) -> Dict[str, Any]:
        """List all Railway projects"""
        query = """
        query {
            me {
                projects {
                    edges {
                        node {
                            id
                            name
                            description
                            createdAt
                            updatedAt
                        }
                    }
                }
            }
        }
        """
        
        result = await self.client.query(query)
        projects = []
        for edge in result.get("me", {}).get("projects", {}).get("edges", []):
            projects.append(edge["node"])
        
        return {"projects": projects}
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        query = """
        query($projectId: String!) {
            project(id: $projectId) {
                id
                name
                description
                createdAt
                updatedAt
                environments {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
                services {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        result = await self.client.query(query, {"projectId": project_id})
        return {"project": result.get("project")}
    
    async def list_services(self, project_id: str) -> Dict[str, Any]:
        """List services in a project"""
        query = """
        query($projectId: String!) {
            project(id: $projectId) {
                services {
                    edges {
                        node {
                            id
                            name
                            createdAt
                            updatedAt
                        }
                    }
                }
            }
        }
        """
        
        result = await self.client.query(query, {"projectId": project_id})
        services = []
        for edge in result.get("project", {}).get("services", {}).get("edges", []):
            services.append(edge["node"])
        
        return {"services": services}
    
    async def get_service_logs(self, service_id: str, deployment_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get service logs"""
        if deployment_id:
            query = """
            query($deploymentId: String!, $limit: Int!) {
                deploymentLogs(deploymentId: $deploymentId, limit: $limit) {
                    message
                    timestamp
                }
            }
            """
            variables = {"deploymentId": deployment_id, "limit": limit}
        else:
            # Get latest deployment logs
            query = """
            query($serviceId: String!, $limit: Int!) {
                service(id: $serviceId) {
                    deployments(first: 1) {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
            }
            """
            result = await self.client.query(query, {"serviceId": service_id, "limit": limit})
            deployments = result.get("service", {}).get("deployments", {}).get("edges", [])
            if not deployments:
                return {"logs": [], "message": "No deployments found"}
            
            deployment_id = deployments[0]["node"]["id"]
            return await self.get_service_logs(service_id, deployment_id, limit)
        
        result = await self.client.query(query, variables)
        return {"logs": result.get("deploymentLogs", [])}
    
    async def get_deployments(self, service_id: str, environment_id: Optional[str] = None) -> Dict[str, Any]:
        """List deployments for a service"""
        query = """
        query($serviceId: String!) {
            service(id: $serviceId) {
                deployments(first: 20) {
                    edges {
                        node {
                            id
                            status
                            createdAt
                            updatedAt
                            environmentId
                        }
                    }
                }
            }
        }
        """
        
        result = await self.client.query(query, {"serviceId": service_id})
        deployments = []
        for edge in result.get("service", {}).get("deployments", {}).get("edges", []):
            deployment = edge["node"]
            if not environment_id or deployment.get("environmentId") == environment_id:
                deployments.append(deployment)
        
        return {"deployments": deployments}
    
    async def redeploy_service(self, service_id: str, environment_id: str) -> Dict[str, Any]:
        """Trigger service redeployment"""
        mutation = """
        mutation($serviceId: String!, $environmentId: String!) {
            serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
        }
        """
        
        result = await self.client.query(mutation, {
            "serviceId": service_id,
            "environmentId": environment_id
        })
        
        return {"success": True, "message": "Redeployment triggered"}
    
    async def set_environment_variable(self, project_id: str, environment_id: str, name: str, value: str, service_id: Optional[str] = None) -> Dict[str, Any]:
        """Set environment variable"""
        mutation = """
        mutation($input: VariableUpsertInput!) {
            variableUpsert(input: $input)
        }
        """
        
        input_data = {
            "projectId": project_id,
            "environmentId": environment_id,
            "name": name,
            "value": value
        }
        
        if service_id:
            input_data["serviceId"] = service_id
        
        result = await self.client.query(mutation, {"input": input_data})
        return {"success": True, "message": f"Variable {name} set successfully"}
    
    async def delete_environment_variable(self, project_id: str, environment_id: str, name: str, service_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete environment variable"""
        mutation = """
        mutation($input: VariableDeleteInput!) {
            variableDelete(input: $input)
        }
        """
        
        input_data = {
            "projectId": project_id,
            "environmentId": environment_id,
            "name": name
        }
        
        if service_id:
            input_data["serviceId"] = service_id
        
        result = await self.client.query(mutation, {"input": input_data})
        return {"success": True, "message": f"Variable {name} deleted successfully"}
    
    async def get_service_metrics(self, service_id: str, environment_id: str) -> Dict[str, Any]:
        """Get service metrics"""
        query = """
        query($serviceId: String!, $environmentId: String!) {
            metrics(serviceId: $serviceId, environmentId: $environmentId) {
                cpu {
                    current
                    limit
                }
                memory {
                    current
                    limit
                }
                network {
                    rxBytes
                    txBytes
                }
                disk {
                    current
                    limit
                }
            }
        }
        """
        
        result = await self.client.query(query, {
            "serviceId": service_id,
            "environmentId": environment_id
        })
        
        return {"metrics": result.get("metrics", {})}
    
    async def restart_service(self, service_id: str, environment_id: str) -> Dict[str, Any]:
        """Restart a service"""
        mutation = """
        mutation($serviceId: String!, $environmentId: String!) {
            serviceInstanceRestart(serviceId: $serviceId, environmentId: $environmentId)
        }
        """
        
        result = await self.client.query(mutation, {
            "serviceId": service_id,
            "environmentId": environment_id
        })
        
        return {"success": True, "message": "Service restart initiated"}

async def main():
    """Main entry point"""
    server = RailwayMCPServer()
    await server.initialize()
    
    logger.info("Railway Admin MCP Server started")
    
    # Read from stdin and write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer = sys.stdout
    
    while True:
        try:
            # Read line from stdin
            line = await reader.readline()
            if not line:
                break
                
            # Parse JSON-RPC request
            request = json.loads(line.decode())
            
            # Handle request
            response = await server.handle_request(request)
            
            # Write response
            writer.write(json.dumps(response).encode() + b'\n')
            writer.flush()
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": None
            }
            writer.write(json.dumps(error_response).encode() + b'\n')
            writer.flush()
    
    await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
