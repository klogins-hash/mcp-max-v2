#!/bin/bash

# Projects to delete
projects_to_delete=(
    "mcp-max-v1"
    "empowering-clarity"
    "helpful-enjoyment"
    "efficient-nourishment"
    "unknown-tomatoes"
    "terrible-fuel"
    "wakeful-wax"
    "courageous-stop"
    "railway-shell-sync-demo"
    "32gb-windsurf"
)

echo "🧹 Starting Railway cleanup..."

# Delete each project
for project in "${projects_to_delete[@]}"; do
    echo "Deleting project: $project"
    # Railway CLI doesn't have a direct delete command, so we'll use the API
    railway link "$project" --environment production 2>/dev/null
    if [ $? -eq 0 ]; then
        # Get project ID and delete via API
        project_id=$(railway status --json 2>/dev/null | jq -r '.projectId')
        if [ ! -z "$project_id" ]; then
            echo "Found project ID: $project_id"
            # Note: Railway CLI doesn't expose delete, need to use web UI
        fi
    fi
done

echo "⚠️  Railway CLI doesn't support project deletion."
echo "Please delete these projects manually in the Railway dashboard:"
echo ""
for project in "${projects_to_delete[@]}"; do
    echo "  - $project"
done
echo ""
echo "Also delete the duplicate mcp-max-v2 (the one without deployments)"
