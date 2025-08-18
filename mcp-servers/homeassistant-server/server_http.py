#!/usr/bin/env python3
"""
Home Assistant MCP Server - HTTP Version for Railway
Provides HTTP endpoints that wrap the MCP protocol for Home Assistant
"""

import json
import os
import asyncio
from typing import Dict, Any
import aiohttp
from aiohttp import web
import logging

# Import the existing server logic
from server import HomeAssistantClient, TOOLS, handle_request

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create web app
app = web.Application()

async def health_check(request):
    """Health check endpoint for Railway"""
    return web.json_response({"status": "healthy", "service": "homeassistant-mcp-server"})

async def handle_mcp_request(request):
    """Handle MCP requests over HTTP"""
    try:
        data = await request.json()
        
        # Process the MCP request
        result = await handle_request(data)
        
        # Wrap in JSON-RPC response
        response = {
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": result
        }
        
        return web.json_response(response)
        
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        return web.json_response({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status=500)

async def list_tools(request):
    """List available tools endpoint"""
    response = await handle_request({
        "method": "tools/list",
        "params": {}
    })
    return web.json_response(response)

async def call_tool(request):
    """Call a specific tool endpoint"""
    try:
        data = await request.json()
        response = await handle_request({
            "method": "tools/call",
            "params": data
        })
        return web.json_response(response)
    except Exception as e:
        logger.error(f"Error calling tool: {str(e)}")
        return web.json_response({
            "error": str(e)
        }, status=500)

# Setup routes
app.router.add_get('/health', health_check)
app.router.add_post('/mcp', handle_mcp_request)
app.router.add_get('/tools', list_tools)
app.router.add_post('/tools/call', call_tool)

# Add CORS middleware
async def cors_middleware(app, handler):
    async def middleware_handler(request):
        if request.method == 'OPTIONS':
            response = web.Response()
        else:
            response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return middleware_handler

app.middlewares.append(cors_middleware)

if __name__ == '__main__':
    # Get port from environment or default
    port = int(os.environ.get('PORT', 8080))
    
    # Check for required environment variables
    if not os.environ.get('HOMEASSISTANT_TOKEN'):
        logger.error("HOMEASSISTANT_TOKEN environment variable is required")
        exit(1)
    
    logger.info(f"Starting Home Assistant MCP HTTP server on port {port}")
    web.run_app(app, host='0.0.0.0', port=port)
