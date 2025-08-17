# Weaviate MCP Manager

A comprehensive MCP (Model Context Protocol) server for managing your Weaviate vector database and integrating with other tools.

## Features

### Weaviate Manager (`server.py`)
- **Schema Management**: View all collections, properties, and object counts
- **Cleanup Utilities**: Remove old data, delete empty collections
- **Data Migration**: Merge duplicate collections
- **Universal Search**: Search across all collections
- **Collection Management**: Delete entire collections

### MCP Integration Hub (`mcp_integration_hub.py`)
- **Central Hub**: Connect Weaviate with all other MCP tools
- **Multi-Source Search**: Search across Weaviate, filesystem, GitHub, etc.
- **Server Status**: Monitor all MCP server connections
- **Unified Interface**: Single point of access for all tools

### Cleanup Script (`cleanup_weaviate.py`)
- **Database Analysis**: Get insights into your collections
- **Consolidation**: Merge similar collections (Knowledge, KnowledgeV3, etc.)
- **Optimization**: Create optimized schema for tool integration
- **Automated Cleanup**: Remove empty collections

## Current Database Status

Your Weaviate instance contains:
- **10 collections** with **12,500+ documents**
- Major collections:
  - `Document`: 10,012 objects
  - `BackupDocuments`: 2,323 objects
  - `RailwayDocs`: 169 objects
  - `WeaviateDocumentation`: 17 objects
  - Various Knowledge collections

## Installation

```bash
cd /Users/dp/CascadeProjects/mcp\ max\ v2/mcp-weaviate-manager
pip3 install -r requirements.txt
```

## Usage

### 1. Run Cleanup Script (Recommended First Step)
```bash
python3 cleanup_weaviate.py
```

Options:
1. Consolidate knowledge collections into UnifiedKnowledge
2. Remove empty collections
3. Create optimized schema for MCP integration
4. Perform all cleanup operations

### 2. Configure MCP Servers

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "weaviate-manager": {
      "command": "python3",
      "args": ["/Users/dp/CascadeProjects/mcp max v2/mcp-weaviate-manager/server.py"]
    }
  }
}
```

### 3. Available MCP Tools

Once configured, you'll have access to:

- `weaviate_schema_info`: View all collections and counts
- `weaviate_cleanup_class`: Clean old data from specific collections
- `weaviate_merge_classes`: Merge duplicate collections
- `weaviate_delete_class`: Delete entire collections
- `weaviate_search`: Search across all collections

## Recommendations

Based on your current database:

1. **Consolidate Knowledge Collections**: You have multiple knowledge-related collections (Knowledge, KnowledgeV3, CohereKnowledge). Consider merging them into UnifiedKnowledge.

2. **Clean Document Collections**: With 10,000+ documents in the Document collection and 2,300+ in BackupDocuments, consider:
   - Archiving old documents
   - Merging BackupDocuments into Document
   - Implementing date-based cleanup

3. **Remove Empty Collections**: ToolDocumentation has 0 objects and can be removed or repopulated.

4. **Optimize Schema**: Create unified collections for better integration with all MCP tools.

## Integration with Other Tools

The MCP Integration Hub connects Weaviate with:
- Filesystem operations
- GitHub/GitLab repositories
- Google Maps
- Slack workspaces
- PostgreSQL/SQLite databases
- Time utilities
- HTTP fetch operations
- Browser automation (Puppeteer)
- Search engines (Brave, Exa)

## Next Steps

1. Run the cleanup script to organize your data
2. Configure the MCP servers in Claude Desktop
3. Use the unified search to query across all your tools
4. Set up automated cleanup schedules for maintaining data quality
