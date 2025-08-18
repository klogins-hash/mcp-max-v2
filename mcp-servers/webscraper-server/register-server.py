import asyncio
import aiohttp
import os
import json
from datetime import datetime

async def register_server():
    """Register the webscraper server with MCP Hub"""
    
    hub_url = os.getenv('MCP_HUB_URL', 'https://mcp-max-v2-production.up.railway.app')
    config = {
        "name": "webscraper-server",
        "displayName": "Web Scraper MCP Server",
        "description": "MCP server for web scraping and content extraction",
        "version": "1.0.0",
        "protocol": "stdio",
        "features": {
            "tools": True,
            "resources": False,
            "prompts": False
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
                print(f"Successfully registered {config['name']}")
                print(f"Server ID: {result.get('serverId')}")
            else:
                error = await response.text()
                print(f"Failed to register: {response.status} - {error}")

if __name__ == "__main__":
    asyncio.run(register_server())
