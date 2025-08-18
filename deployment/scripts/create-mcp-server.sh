#!/bin/bash

# Create a new MCP server from template
# Usage: ./create-mcp-server.sh <category> <tool-name>

CATEGORY=$1
TOOL_NAME=$2

if [ -z "$CATEGORY" ] || [ -z "$TOOL_NAME" ]; then
    echo "Usage: ./create-mcp-server.sh <category> <tool-name>"
    echo "Example: ./create-mcp-server.sh dev github"
    echo ""
    echo "Categories: dev, ai, data, comm, productivity, media, finance, security"
    exit 1
fi

SERVER_NAME="${CATEGORY}-${TOOL_NAME}"
SERVER_DIR="mcp-servers/${SERVER_NAME}-server"

echo "🔨 Creating MCP server: $SERVER_NAME"

# Create directory structure
mkdir -p "$SERVER_DIR"

# Create server.py from template
cat > "$SERVER_DIR/server.py" << 'EOF'
#!/usr/bin/env python3
"""
MCP Server for TOOL_NAME_PLACEHOLDER
Category: CATEGORY_PLACEHOLDER
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List

# MCP Protocol Handler
class TOOL_NAMEServer:
    def __init__(self):
        self.name = "TOOL_NAME_PLACEHOLDER-server"
        self.category = "CATEGORY_PLACEHOLDER"
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        
        if method == "tools/list":
            return await self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(request.get("params", {}))
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": "example_tool",
                    "description": "Example tool for TOOL_NAME_PLACEHOLDER",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Query parameter"}
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with given parameters"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "example_tool":
            # Implement your tool logic here
            query = arguments.get("query")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Executed {tool_name} with query: {query}"
                    }
                ]
            }
        
        return {"error": f"Unknown tool: {tool_name}"}

async def main():
    """Main entry point for MCP server"""
    server = TOOL_NAMEServer()
    
    # Read from stdin and write to stdout (MCP protocol)
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line)
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Replace placeholders
sed -i '' "s/TOOL_NAME_PLACEHOLDER/${TOOL_NAME}/g" "$SERVER_DIR/server.py"
sed -i '' "s/CATEGORY_PLACEHOLDER/${CATEGORY}/g" "$SERVER_DIR/server.py"
sed -i '' "s/TOOL_NAME/${TOOL_NAME^}/g" "$SERVER_DIR/server.py"

# Create requirements.txt
cat > "$SERVER_DIR/requirements.txt" << EOF
# Core dependencies
asyncio
aiohttp>=3.9.0

# Add tool-specific dependencies below
# example: openai>=1.0.0
EOF

# Create Dockerfile
cat > "$SERVER_DIR/Dockerfile" << EOF
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .
COPY register.py .

# Make executable
RUN chmod +x server.py

# Run server
CMD ["python", "server.py"]
EOF

# Create registration script
cat > "$SERVER_DIR/register.py" << EOF
#!/usr/bin/env python3
"""Register ${TOOL_NAME} server with MCP Hub"""

import os
import requests
import json

HUB_URL = os.getenv("MCP_HUB_URL", "http://localhost:8000")
SERVER_NAME = "${SERVER_NAME}-server"
CATEGORY = "${CATEGORY}"

def register():
    """Register this server with the MCP Hub"""
    registration_data = {
        "name": SERVER_NAME,
        "category": CATEGORY,
        "endpoint": os.getenv("RAILWAY_PUBLIC_DOMAIN", f"http://localhost:8001"),
        "capabilities": ["example_tool"],  # Update with actual tools
        "health_check": "/health"
    }
    
    try:
        response = requests.post(
            f"{HUB_URL}/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully registered {SERVER_NAME} with hub")
        else:
            print(f"❌ Failed to register: {response.text}")
            
    except Exception as e:
        print(f"❌ Error registering with hub: {e}")

if __name__ == "__main__":
    register()
EOF

# Create railway.json
cat > "$SERVER_DIR/railway.json" << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF

# Create README
cat > "$SERVER_DIR/README.md" << EOF
# MCP ${TOOL_NAME^} Server

Category: ${CATEGORY}

## Description

MCP server implementation for ${TOOL_NAME^} integration.

## Environment Variables

\`\`\`env
# Required
MCP_${CATEGORY^^}_${TOOL_NAME^^}_API_KEY=your-api-key

# Optional
MCP_${CATEGORY^^}_${TOOL_NAME^^}_TIMEOUT=30
\`\`\`

## Available Tools

1. **example_tool** - Example tool implementation
   - Parameters: query (string)

## Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python server.py

# Deploy to Railway
../deployment/scripts/deploy-mcp-server.sh ${TOOL_NAME}
\`\`\`
EOF

echo "✅ Created MCP server template at: $SERVER_DIR"
echo ""
echo "Next steps:"
echo "1. Update server.py with actual ${TOOL_NAME} implementation"
echo "2. Add required dependencies to requirements.txt"
echo "3. Set environment variables in Railway"
echo "4. Deploy with: ./deployment/scripts/deploy-mcp-server.sh ${TOOL_NAME}"
