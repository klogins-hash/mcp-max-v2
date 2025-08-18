#!/usr/bin/env python3
"""
Home Assistant MCP Server
Provides MCP protocol access to Home Assistant REST API
"""

import json
import sys
import asyncio
import os
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

class HomeAssistantClient:
    """Async client for Home Assistant REST API"""
    
    def __init__(self, url: str, token: str):
        self.base_url = url.rstrip('/')
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
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to Home Assistant API"""
        url = f"{self.base_url}/api{endpoint}"
        async with self.session.get(url, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to Home Assistant API"""
        url = f"{self.base_url}/api{endpoint}"
        async with self.session.post(url, headers=self.headers, json=data) as response:
            response.raise_for_status()
            return await response.json()

# Tool definitions
TOOLS = [
    {
        "name": "ha_get_states",
        "description": "Get all entity states or filter by domain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Optional domain filter (e.g., 'light', 'switch', 'sensor')"
                }
            }
        }
    },
    {
        "name": "ha_get_state",
        "description": "Get the state of a specific entity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID (e.g., 'light.living_room')"
                }
            },
            "required": ["entity_id"]
        }
    },
    {
        "name": "ha_set_state",
        "description": "Set the state of an entity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID"
                },
                "state": {
                    "type": "string",
                    "description": "New state value"
                },
                "attributes": {
                    "type": "object",
                    "description": "Optional attributes to set"
                }
            },
            "required": ["entity_id", "state"]
        }
    },
    {
        "name": "ha_call_service",
        "description": "Call a Home Assistant service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Service domain (e.g., 'light', 'switch')"
                },
                "service": {
                    "type": "string",
                    "description": "Service name (e.g., 'turn_on', 'toggle')"
                },
                "entity_id": {
                    "type": ["string", "array"],
                    "description": "Optional entity ID(s) to target"
                },
                "service_data": {
                    "type": "object",
                    "description": "Optional service data"
                }
            },
            "required": ["domain", "service"]
        }
    },
    {
        "name": "ha_get_services",
        "description": "Get all available services",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Optional domain filter"
                }
            }
        }
    },
    {
        "name": "ha_get_history",
        "description": "Get entity state history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID"
                },
                "start_time": {
                    "type": "string",
                    "description": "Optional start time (ISO format)"
                },
                "end_time": {
                    "type": "string",
                    "description": "Optional end time (ISO format)"
                }
            },
            "required": ["entity_id"]
        }
    },
    {
        "name": "ha_get_config",
        "description": "Get Home Assistant configuration",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "ha_fire_event",
        "description": "Fire a custom event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Event type name"
                },
                "event_data": {
                    "type": "object",
                    "description": "Optional event data"
                }
            },
            "required": ["event_type"]
        }
    },
    {
        "name": "ha_get_logbook",
        "description": "Get logbook entries",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Optional entity filter"
                },
                "start_time": {
                    "type": "string",
                    "description": "Optional start time (ISO format)"
                },
                "end_time": {
                    "type": "string",
                    "description": "Optional end time (ISO format)"
                }
            }
        }
    }
]

async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming MCP protocol requests"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": TOOLS
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        # Get Home Assistant credentials from environment
        ha_url = os.environ.get("HOMEASSISTANT_URL", "http://localhost:8123")
        ha_token = os.environ.get("HOMEASSISTANT_TOKEN")
        
        if not ha_token:
            return {
                "content": [{"type": "text", "text": "Error: HOMEASSISTANT_TOKEN environment variable not set"}],
                "isError": True
            }
        
        try:
            async with HomeAssistantClient(ha_url, ha_token) as client:
                if tool_name == "ha_get_states":
                    states = await client.get("/states")
                    if args.get("domain"):
                        states = [s for s in states if s["entity_id"].startswith(f"{args['domain']}.")]
                    return {
                        "content": [{"type": "text", "text": json.dumps(states, indent=2)}]
                    }
                
                elif tool_name == "ha_get_state":
                    entity_id = args["entity_id"]
                    state = await client.get(f"/states/{entity_id}")
                    return {
                        "content": [{"type": "text", "text": json.dumps(state, indent=2)}]
                    }
                
                elif tool_name == "ha_set_state":
                    entity_id = args["entity_id"]
                    data = {
                        "state": args["state"],
                        "attributes": args.get("attributes", {})
                    }
                    result = await client.post(f"/states/{entity_id}", data)
                    return {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                
                elif tool_name == "ha_call_service":
                    domain = args["domain"]
                    service = args["service"]
                    data = args.get("service_data", {})
                    if "entity_id" in args:
                        data["entity_id"] = args["entity_id"]
                    result = await client.post(f"/services/{domain}/{service}", data)
                    return {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                
                elif tool_name == "ha_get_services":
                    services = await client.get("/services")
                    if args.get("domain"):
                        services = {k: v for k, v in services.items() if k == args["domain"]}
                    return {
                        "content": [{"type": "text", "text": json.dumps(services, indent=2)}]
                    }
                
                elif tool_name == "ha_get_history":
                    entity_id = args["entity_id"]
                    params = []
                    if "start_time" in args:
                        params.append(f"start_time={args['start_time']}")
                    if "end_time" in args:
                        params.append(f"end_time={args['end_time']}")
                    query = "?" + "&".join(params) if params else ""
                    history = await client.get(f"/history/period/{entity_id}{query}")
                    return {
                        "content": [{"type": "text", "text": json.dumps(history, indent=2)}]
                    }
                
                elif tool_name == "ha_get_config":
                    config = await client.get("/config")
                    return {
                        "content": [{"type": "text", "text": json.dumps(config, indent=2)}]
                    }
                
                elif tool_name == "ha_fire_event":
                    event_type = args["event_type"]
                    event_data = args.get("event_data", {})
                    result = await client.post(f"/events/{event_type}", event_data)
                    return {
                        "content": [{"type": "text", "text": f"Event '{event_type}' fired successfully"}]
                    }
                
                elif tool_name == "ha_get_logbook":
                    params = []
                    if "entity_id" in args:
                        params.append(f"entity={args['entity_id']}")
                    if "start_time" in args:
                        params.append(f"start_time={args['start_time']}")
                    if "end_time" in args:
                        params.append(f"end_time={args['end_time']}")
                    query = "?" + "&".join(params) if params else ""
                    logbook = await client.get(f"/logbook{query}")
                    return {
                        "content": [{"type": "text", "text": json.dumps(logbook, indent=2)}]
                    }
                
                else:
                    return {
                        "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                        "isError": True
                    }
                    
        except aiohttp.ClientError as e:
            return {
                "content": [{"type": "text", "text": f"API Error: {str(e)}"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    return {
        "error": "Unknown method"
    }

async def main():
    """Main loop for handling stdin/stdout communication"""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    while True:
        try:
            line = await reader.readline()
            if not line:
                break
                
            request = json.loads(line.decode())
            
            # Handle request
            result = await handle_request(request)
            
            # Send response
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result
            }
            
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            sys.stdout.write(json.dumps(error_response) + '\n')
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
