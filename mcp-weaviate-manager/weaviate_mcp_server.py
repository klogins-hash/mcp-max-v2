#!/usr/bin/env python3
"""
Standalone MCP Server for Weaviate Database Management
Works directly with Claude Desktop without external MCP dependencies
"""

import sys
import json
import asyncio
import weaviate
from datetime import datetime
from typing import Any, Dict, List, Optional

# Weaviate configuration
WEAVIATE_URL = "https://weaviate-production-5bc1.up.railway.app"

class WeaviateManager:
    """Manages Weaviate database operations"""
    
    def __init__(self, url: str):
        self.url = url
        self.client = None
        
    def connect(self):
        """Connect to Weaviate instance"""
        try:
            self.client = weaviate.Client(
                url=self.url,
                timeout_config=(5, 15)
            )
            if self.client.is_ready():
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information including all classes and their properties"""
        if not self.client:
            return {"error": "Not connected to Weaviate"}
        
        try:
            schema = self.client.schema.get()
            meta = self.client.get_meta()
            
            # Get detailed info for each class
            class_info = []
            for cls in schema.get('classes', []):
                class_name = cls.get('class')
                
                # Get object count
                try:
                    result = self.client.query.aggregate(class_name).with_meta_count().do()
                    count = result.get('data', {}).get('Aggregate', {}).get(class_name, [{}])[0].get('meta', {}).get('count', 0)
                except:
                    count = 0
                
                class_info.append({
                    'name': class_name,
                    'object_count': count,
                    'properties': [{'name': p.get('name'), 'dataType': p.get('dataType')} for p in cls.get('properties', [])]
                })
            
            return {
                'version': meta.get('version'),
                'total_classes': len(schema.get('classes', [])),
                'classes': class_info
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_class(self, class_name: str, keep_recent: bool = True, days: int = 30) -> Dict[str, Any]:
        """Clean up a specific class by removing old or duplicate data"""
        if not self.client:
            return {"error": "Not connected to Weaviate"}
        
        try:
            # Get all objects from the class
            result = self.client.query.get(class_name).with_additional(['id', 'creationTimeUnix']).do()
            objects = result.get('data', {}).get('Get', {}).get(class_name, [])
            
            if not objects:
                return {"message": f"No objects found in class {class_name}"}
            
            deleted_count = 0
            
            # If keep_recent is True, only delete objects older than specified days
            if keep_recent:
                cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
                for obj in objects:
                    creation_time = obj.get('_additional', {}).get('creationTimeUnix', 0) / 1000
                    if creation_time < cutoff_time:
                        obj_id = obj.get('_additional', {}).get('id')
                        if obj_id:
                            self.client.data_object.delete(obj_id, class_name)
                            deleted_count += 1
            
            return {
                "class": class_name,
                "total_objects": len(objects),
                "deleted_objects": deleted_count,
                "remaining_objects": len(objects) - deleted_count
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_across_classes(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search across all classes for relevant content"""
        if not self.client:
            return {"error": "Not connected to Weaviate"}
        
        try:
            schema = self.client.schema.get()
            all_results = []
            
            for cls in schema.get('classes', []):
                class_name = cls.get('class')
                
                # Get text properties for this class
                text_props = [p['name'] for p in cls.get('properties', []) 
                             if 'text' in p.get('dataType', [])]
                
                if not text_props:
                    continue
                
                try:
                    # Search in this class
                    result = (self.client.query
                             .get(class_name, text_props[:5])  # Limit to first 5 text properties
                             .with_near_text({"concepts": [query]})
                             .with_limit(limit)
                             .with_additional(['distance'])
                             .do())
                    
                    objects = result.get('data', {}).get('Get', {}).get(class_name, [])
                    for obj in objects:
                        all_results.append({
                            'class': class_name,
                            'data': obj,
                            'distance': obj.get('_additional', {}).get('distance', 1.0)
                        })
                except:
                    continue
            
            # Sort by distance (lower is better)
            all_results.sort(key=lambda x: x['distance'])
            
            return {
                "query": query,
                "total_results": len(all_results),
                "results": all_results[:limit]
            }
            
        except Exception as e:
            return {"error": str(e)}

# Initialize Weaviate manager
weaviate_manager = WeaviateManager(WEAVIATE_URL)

def handle_request(request):
    """Handle incoming MCP requests"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # Ensure connection
    if not weaviate_manager.client or not weaviate_manager.client.is_ready():
        if not weaviate_manager.connect():
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": "Failed to connect to Weaviate"}
            }
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "weaviate_schema_info",
                        "description": "Get detailed schema information including all classes and object counts",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "weaviate_cleanup_class",
                        "description": "Clean up a specific class by removing old or duplicate data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "class_name": {
                                    "type": "string",
                                    "description": "Name of the class to clean up"
                                },
                                "keep_recent": {
                                    "type": "boolean",
                                    "description": "Whether to keep recent data (default: true)"
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days to keep data for (default: 30)"
                                }
                            },
                            "required": ["class_name"]
                        }
                    },
                    {
                        "name": "weaviate_search",
                        "description": "Search across all classes for relevant content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results (default: 10)"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "weaviate_schema_info":
                result = weaviate_manager.get_schema_info()
            elif tool_name == "weaviate_cleanup_class":
                class_name = arguments.get("class_name")
                keep_recent = arguments.get("keep_recent", True)
                days = arguments.get("days", 30)
                result = weaviate_manager.cleanup_class(class_name, keep_recent, days)
            elif tool_name == "weaviate_search":
                query = arguments.get("query")
                limit = arguments.get("limit", 10)
                result = weaviate_manager.search_across_classes(query, limit)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(e)}
            }
    
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "weaviate-manager",
                    "version": "1.0.0"
                }
            }
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

async def main():
    """Run the MCP server"""
    # Connect to Weaviate on startup
    weaviate_manager.connect()
    
    while True:
        try:
            # Read request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line)
            response = handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
