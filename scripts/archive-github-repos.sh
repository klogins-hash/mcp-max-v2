#!/bin/bash

# GitHub Repository Archival Script
# Archives repositories that are no longer relevant

echo "🗄️ GitHub Repository Archival Script"
echo "===================================="

# Repositories to archive
repos_to_archive=(
    # Test/Demo projects
    "devin-test-repo"
    "minecraft-java"
    "Host-and-Deploy-Creations-on-Azure-Cloud-Server"
    "azure-web-deployment"
    "windsurf-mamma-bear-migration"
    
    # Documentation/Migration
    "docs"
    "azure-to-railway-migration"
    
    # Duplicates
    "weave-embedding-cohere"
    "windsurf-settings-sync"
    "firecrawl-app-examples"
    "firecrawl-platform-complete"
    
    # Obsolete Windsurf projects
    "windsurf.manus"
    "windsurf-local-manus"
    "windsurf-development-toolkit"
    "windsurf-vision-agent"
    
    # Other obsolete
    "collectiv-v1.0"
    "idea-craft-bot"
    "manus-chat-manager"
)

# Archive each repository
for repo in "${repos_to_archive[@]}"; do
    echo ""
    echo "Archiving: $repo"
    gh repo archive "klogins-hash/$repo" --yes
    if [ $? -eq 0 ]; then
        echo "✅ Archived: $repo"
    else
        echo "❌ Failed to archive: $repo"
    fi
done

echo ""
echo "✨ Archival process complete!"
echo ""
echo "Repositories that need manual review before archiving:"
echo "- chatweave-devin-handoff"
echo "- manus-open-source"
echo "- chatweave-data"
echo "- chatweave-data-updated"
echo "- business-disruptor-ai"
echo "- spark-reach-craft"
