#!/usr/bin/env python3
"""
Register Railway Admin Server with MCP Hub
"""

import asyncio
import aiohttp
import os
import sys

async def register_server():
    """Register the Railway admin server with MCP Hub"""
    
    hub_url = os.getenv('MCP_HUB_URL', 'https://mcp-max-v2-production.up.railway.app')
    config = {
        "name": "railway-admin-server",
        "displayName": "Railway Admin MCP Server",
        "description": "Comprehensive Railway platform management via MCP",
        "host": "localhost",
        "port": 8084,
        "capabilities": [
            "project-management",
            "service-management", 
            "deployment-control",
            "environment-variables",
            "logs-access",
            "metrics-monitoring",
            "service-restart"
        ],
        "metadata": {
            "version": "1.0.0",
            "author": "MCP Max v2"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{hub_url}/api/v1/servers/register",
            json=config,
            headers={"Authorization": f"Bearer {os.getenv('RAILWAY_API_TOKEN')}"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Successfully registered Railway Admin Server: {result}")
            else:
                error = await response.text()
                print(f"❌ Failed to register: {response.status} - {error}")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(register_server())
