#!/bin/bash

# Manage Railway services for MCP deployment
# Usage: ./manage-railway-services.sh <command> [options]

COMMAND=$1
PROJECT="mcp-max-v2"

case "$COMMAND" in
    "status")
        echo "📊 MCP Services Status"
        echo "====================="
        railway status --json | jq -r '.services[] | "\(.name): \(.status)"'
        ;;
        
    "list")
        echo "📋 All MCP Services"
        echo "=================="
        railway service list
        ;;
        
    "logs")
        SERVICE=$2
        if [ -z "$SERVICE" ]; then
            echo "Usage: ./manage-railway-services.sh logs <service-name>"
            exit 1
        fi
        railway logs --service "$SERVICE"
        ;;
        
    "restart")
        SERVICE=$2
        if [ -z "$SERVICE" ]; then
            echo "Usage: ./manage-railway-services.sh restart <service-name>"
            exit 1
        fi
        echo "🔄 Restarting $SERVICE..."
        railway service "$SERVICE"
        railway restart
        ;;
        
    "scale")
        SERVICE=$2
        REPLICAS=$3
        if [ -z "$SERVICE" ] || [ -z "$REPLICAS" ]; then
            echo "Usage: ./manage-railway-services.sh scale <service-name> <replicas>"
            exit 1
        fi
        echo "📈 Scaling $SERVICE to $REPLICAS replicas..."
        railway service "$SERVICE"
        railway scale --replicas "$REPLICAS"
        ;;
        
    "deploy-all")
        echo "🚀 Deploying all MCP servers..."
        for dir in mcp-servers/*-server; do
            if [ -d "$dir" ]; then
                server_name=$(basename "$dir" | sed 's/-server$//')
                echo "Deploying $server_name..."
                ./deploy-mcp-server.sh "$server_name"
            fi
        done
        ;;
        
    "health")
        echo "🏥 Health Check Status"
        echo "===================="
        HUB_URL=$(railway variables --service mcp-hub-prod | grep MCP_HUB_URL | cut -d'=' -f2)
        curl -s "$HUB_URL/health" | jq '.'
        echo ""
        echo "Server Health:"
        curl -s "$HUB_URL/servers/health" | jq '.'
        ;;
        
    *)
        echo "MCP Railway Service Manager"
        echo ""
        echo "Commands:"
        echo "  status      - Show status of all services"
        echo "  list        - List all services"
        echo "  logs        - View logs for a service"
        echo "  restart     - Restart a service"
        echo "  scale       - Scale service replicas"
        echo "  deploy-all  - Deploy all MCP servers"
        echo "  health      - Check health of all services"
        ;;
esac
