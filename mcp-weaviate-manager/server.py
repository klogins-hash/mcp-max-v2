#!/usr/bin/env python3
"""
MCP Server for Weaviate Database Management
Provides tools for managing, cleaning, and integrating with Weaviate vector database
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import weaviate
from weaviate.client import Client
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.tools import Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                logger.info("Connected to Weaviate successfully")
                return True
            else:
                logger.error("Weaviate client is not ready")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
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
    
    def merge_duplicate_classes(self, source_class: str, target_class: str) -> Dict[str, Any]:
        """Merge data from source class into target class"""
        if not self.client:
            return {"error": "Not connected to Weaviate"}
        
        try:
            # Get all objects from source class
            result = self.client.query.get(source_class).with_additional(['id']).do()
            source_objects = result.get('data', {}).get('Get', {}).get(source_class, [])
            
            if not source_objects:
                return {"message": f"No objects found in source class {source_class}"}
            
            # Get schema for both classes
            schema = self.client.schema.get()
            source_schema = next((c for c in schema['classes'] if c['class'] == source_class), None)
            target_schema = next((c for c in schema['classes'] if c['class'] == target_class), None)
            
            if not source_schema or not target_schema:
                return {"error": "Could not find schema for source or target class"}
            
            # Map properties
            migrated_count = 0
            for obj in source_objects:
                # Remove additional fields
                obj_data = {k: v for k, v in obj.items() if not k.startswith('_')}
                
                # Only include properties that exist in target schema
                target_props = {p['name'] for p in target_schema['properties']}
                filtered_data = {k: v for k, v in obj_data.items() if k in target_props}
                
                if filtered_data:
                    try:
                        self.client.data_object.create(filtered_data, target_class)
                        migrated_count += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate object: {e}")
            
            return {
                "source_class": source_class,
                "target_class": target_class,
                "total_objects": len(source_objects),
                "migrated_objects": migrated_count
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def delete_class(self, class_name: str) -> Dict[str, Any]:
        """Delete an entire class and all its data"""
        if not self.client:
            return {"error": "Not connected to Weaviate"}
        
        try:
            self.client.schema.delete_class(class_name)
            return {"message": f"Successfully deleted class {class_name}"}
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

# Initialize MCP server
weaviate_manager = WeaviateManager(WEAVIATE_URL)
server = Server("weaviate-manager")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available Weaviate management tools"""
    return [
        Tool(
            name="weaviate_schema_info",
            description="Get detailed schema information including all classes and object counts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="weaviate_cleanup_class",
            description="Clean up a specific class by removing old or duplicate data",
            inputSchema={
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
        ),
        Tool(
            name="weaviate_merge_classes",
            description="Merge data from source class into target class",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_class": {
                        "type": "string",
                        "description": "Source class to merge from"
                    },
                    "target_class": {
                        "type": "string",
                        "description": "Target class to merge into"
                    }
                },
                "required": ["source_class", "target_class"]
            }
        ),
        Tool(
            name="weaviate_delete_class",
            description="Delete an entire class and all its data",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Name of the class to delete"
                    }
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="weaviate_search",
            description="Search across all classes for relevant content",
            inputSchema={
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
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
    """Handle tool execution"""
    
    # Ensure connection
    if not weaviate_manager.client or not weaviate_manager.client.is_ready():
        if not weaviate_manager.connect():
            return [TextContent(type="text", text=json.dumps({"error": "Failed to connect to Weaviate"}))]
    
    try:
        if name == "weaviate_schema_info":
            result = weaviate_manager.get_schema_info()
            
        elif name == "weaviate_cleanup_class":
            class_name = arguments.get("class_name")
            keep_recent = arguments.get("keep_recent", True)
            days = arguments.get("days", 30)
            result = weaviate_manager.cleanup_class(class_name, keep_recent, days)
            
        elif name == "weaviate_merge_classes":
            source_class = arguments.get("source_class")
            target_class = arguments.get("target_class")
            result = weaviate_manager.merge_duplicate_classes(source_class, target_class)
            
        elif name == "weaviate_delete_class":
            class_name = arguments.get("class_name")
            result = weaviate_manager.delete_class(class_name)
            
        elif name == "weaviate_search":
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            result = weaviate_manager.search_across_classes(query, limit)
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the MCP server"""
    logger.info("Starting Weaviate Manager MCP Server...")
    
    # Initial connection attempt
    weaviate_manager.connect()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weaviate-manager",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
