#!/usr/bin/env python3
"""
MCP Integration Hub - Central connector for all MCP tools
Provides a unified interface to connect Weaviate with all other MCP servers
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import subprocess
import os
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.tools import Tool
from mcp.types import TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPIntegrationHub:
    """Central hub for managing all MCP tool connections"""
    
    def __init__(self):
        self.connected_servers = {}
        self.server_configs = {
            "weaviate": {
                "name": "weaviate-manager",
                "path": "/Users/dp/CascadeProjects/mcp max v2/mcp-weaviate-manager/server.py",
                "description": "Weaviate vector database management"
            },
            "filesystem": {
                "name": "filesystem",
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "args": ["/Users/dp/CascadeProjects/mcp max v2"],
                "description": "File system operations"
            },
            "github": {
                "name": "github",
                "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")},
                "description": "GitHub repository management"
            },
            "gitlab": {
                "name": "gitlab",
                "command": ["npx", "-y", "@modelcontextprotocol/server-gitlab"],
                "env": {"GITLAB_PERSONAL_ACCESS_TOKEN": os.getenv("GITLAB_TOKEN", "")},
                "description": "GitLab repository management"
            },
            "google-maps": {
                "name": "google-maps",
                "command": ["npx", "-y", "@modelcontextprotocol/server-google-maps"],
                "env": {"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY", "")},
                "description": "Google Maps integration"
            },
            "slack": {
                "name": "slack",
                "command": ["npx", "-y", "@modelcontextprotocol/server-slack"],
                "env": {"SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", "")},
                "description": "Slack workspace integration"
            },
            "postgres": {
                "name": "postgres",
                "command": ["npx", "-y", "@modelcontextprotocol/server-postgres"],
                "args": [os.getenv("POSTGRES_CONNECTION_STRING", "")],
                "description": "PostgreSQL database operations"
            },
            "sqlite": {
                "name": "sqlite",
                "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                "args": ["--db-path", "/Users/dp/CascadeProjects/mcp max v2/data/sqlite.db"],
                "description": "SQLite database operations"
            },
            "time": {
                "name": "time",
                "command": ["npx", "-y", "@modelcontextprotocol/server-time"],
                "description": "Time and timezone utilities"
            },
            "fetch": {
                "name": "fetch",
                "command": ["npx", "-y", "@modelcontextprotocol/server-fetch"],
                "description": "HTTP/HTTPS fetch operations"
            },
            "memory": {
                "name": "memory",
                "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                "description": "Knowledge graph memory"
            },
            "puppeteer": {
                "name": "puppeteer",
                "command": ["npx", "-y", "@modelcontextprotocol/server-puppeteer"],
                "description": "Browser automation"
            },
            "brave-search": {
                "name": "brave-search",
                "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
                "env": {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")},
                "description": "Brave search integration"
            },
            "exa": {
                "name": "exa",
                "command": ["npx", "-y", "@modelcontextprotocol/server-exa"],
                "env": {"EXA_API_KEY": os.getenv("EXA_API_KEY", "")},
                "description": "Exa search integration"
            }
        }
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all configured MCP servers"""
        status = {
            "total_servers": len(self.server_configs),
            "connected": len(self.connected_servers),
            "servers": []
        }
        
        for name, config in self.server_configs.items():
            server_info = {
                "name": name,
                "description": config.get("description"),
                "connected": name in self.connected_servers,
                "has_credentials": True
            }
            
            # Check if required environment variables are set
            if "env" in config:
                for env_var, value in config["env"].items():
                    if not value:
                        server_info["has_credentials"] = False
                        server_info["missing_env"] = env_var
            
            status["servers"].append(server_info)
        
        return status
    
    async def connect_to_weaviate(self) -> Dict[str, Any]:
        """Connect to Weaviate MCP server and perform operations"""
        try:
            # Import the Weaviate manager
            import sys
            sys.path.append('/Users/dp/CascadeProjects/mcp max v2/mcp-weaviate-manager')
            from server import weaviate_manager
            
            # Connect to Weaviate
            if weaviate_manager.connect():
                self.connected_servers["weaviate"] = weaviate_manager
                return {"status": "connected", "message": "Successfully connected to Weaviate"}
            else:
                return {"status": "failed", "message": "Failed to connect to Weaviate"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def query_weaviate(self, query: str, operation: str = "search") -> Dict[str, Any]:
        """Query Weaviate through the MCP interface"""
        if "weaviate" not in self.connected_servers:
            await self.connect_to_weaviate()
        
        if "weaviate" in self.connected_servers:
            weaviate = self.connected_servers["weaviate"]
            
            if operation == "search":
                return weaviate.search_across_classes(query)
            elif operation == "schema":
                return weaviate.get_schema_info()
            else:
                return {"error": f"Unknown operation: {operation}"}
        else:
            return {"error": "Not connected to Weaviate"}
    
    def create_unified_search(self, query: str, sources: List[str] = None) -> Dict[str, Any]:
        """Search across multiple MCP sources"""
        if sources is None:
            sources = ["weaviate", "filesystem", "github"]
        
        results = {
            "query": query,
            "sources": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for source in sources:
            if source == "weaviate" and source in self.connected_servers:
                try:
                    weaviate_results = self.connected_servers[source].search_across_classes(query, limit=5)
                    results["sources"][source] = weaviate_results
                except Exception as e:
                    results["sources"][source] = {"error": str(e)}
            else:
                results["sources"][source] = {"status": "not_implemented"}
        
        return results

# Initialize MCP server
hub = MCPIntegrationHub()
server = Server("mcp-integration-hub")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available integration tools"""
    return [
        Tool(
            name="hub_status",
            description="Get status of all MCP servers and connections",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="hub_connect_weaviate",
            description="Connect to Weaviate MCP server",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="hub_query_weaviate",
            description="Query Weaviate through MCP interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or operation"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["search", "schema"],
                        "description": "Operation type (default: search)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="hub_unified_search",
            description="Search across multiple MCP sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of sources to search (default: weaviate, filesystem, github)"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
    """Handle tool execution"""
    
    try:
        if name == "hub_status":
            result = hub.get_server_status()
            
        elif name == "hub_connect_weaviate":
            result = await hub.connect_to_weaviate()
            
        elif name == "hub_query_weaviate":
            query = arguments.get("query")
            operation = arguments.get("operation", "search")
            result = await hub.query_weaviate(query, operation)
            
        elif name == "hub_unified_search":
            query = arguments.get("query")
            sources = arguments.get("sources")
            result = hub.create_unified_search(query, sources)
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the MCP Integration Hub server"""
    logger.info("Starting MCP Integration Hub...")
    
    # Initial connection to Weaviate
    await hub.connect_to_weaviate()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-integration-hub",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
