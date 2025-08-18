# MCP Server Creation & Connection Prompt

Copy and paste this prompt when you need to create a new MCP server and connect it to your MCP Max v2 Hub:

---

I need to create a new MCP server for **[TOOL_NAME]** and connect it to my existing MCP Max v2 Hub.

## Project Details
- **MCP Hub Location**: `/Users/dp/CascadeProjects/mcp max v2`
- **Hub is deployed on Railway** (run `railway open` in project directory to get URL)
- **Railway API Token**: `ce03376f-6cf9-43ea-b678-12055cc20a7c`
- **GitHub Repo**: `https://github.com/klogins-hash/mcp-max-v2`
- **Architecture**: Hub-and-spoke pattern with central routing

## Requirements
Please create an MCP server that:
1. Goes in: `/Users/dp/CascadeProjects/mcp max v2/mcp-servers/[toolname]-server/`
2. Follows the standard MCP protocol (stdin/stdout JSON-RPC)
3. Implements `tools/list` and `tools/call` methods
4. Includes proper error handling and async support
5. Uses the existing project structure and patterns

## Tool Capabilities Needed
The server should integrate with **[TOOL_NAME]** API and provide these capabilities:
- [CAPABILITY 1: e.g., "send messages to channels"]
- [CAPABILITY 2: e.g., "read recent messages"]
- [CAPABILITY 3: e.g., "manage user permissions"]
- [Add more as needed]

## Post-Creation Steps
After creating the server:
1. Add it to `/Users/dp/CascadeProjects/mcp max v2/mcp-weaviate-manager/claude_mcp_config.json`
2. Create a registration script to connect it to the MCP Hub
3. Include any required API keys as environment variables
4. Test the connection locally
5. Update the main README with the new server info

## API Credentials
- **[TOOL_NAME] API Key**: [Provide key or say "Need to obtain from [URL]"]
- **[Other Required Credential]**: [Provide or specify how to get]
- **Environment Variables to Set**: [List any env vars needed]

## Technical Context
The existing hub uses:
- 16 Gunicorn workers with uvloop
- Least-connections load balancing  
- Health checks at `/health` endpoint
- Service registry for dynamic registration
- Python 3.11 with FastAPI
- Optimized for Railway's 32 vCPU/32GB RAM

## Example Tools Already Connected
- Weaviate vector database manager
- Filesystem operations
- GitHub integration
- Time utilities
- Web fetch capabilities
- Memory management
- Puppeteer browser automation

---

**Replace all [BRACKETED] placeholders with your specific information before using this prompt.**
