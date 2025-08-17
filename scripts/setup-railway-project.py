#!/usr/bin/env python3
"""
Railway Project Setup Script for MCP Max v2
Automatically configures Railway project with optimal settings
"""

import os
import sys
import json
import subprocess
import requests
from typing import Dict, Any

# Railway API configuration
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
RAILWAY_TOKEN = "ce03376f-6cf9-43ea-b678-12055cc20a7c"

# Project configuration
PROJECT_NAME = "mcp-max-v2"
ENVIRONMENT_NAME = "production"

# Environment variables for Railway
ENV_VARS = {
    "MCP_HUB_PORT": "8000",
    "GUNICORN_WORKERS": "16",
    "GUNICORN_WORKER_CLASS": "uvicorn.workers.UvicornWorker",
    "GUNICORN_WORKER_CONNECTIONS": "2000",
    "GUNICORN_MAX_REQUESTS": "10000",
    "GUNICORN_MAX_REQUESTS_JITTER": "1000",
    "PYTHONUNBUFFERED": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHON_VERSION": "3.11",
    "PORT": "8000"
}

def make_graphql_request(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a GraphQL request to Railway API"""
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(RAILWAY_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def create_project():
    """Create a new Railway project"""
    query = """
    mutation CreateProject($input: ProjectCreateInput!) {
        projectCreate(input: $input) {
            id
            name
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "input": {
            "name": PROJECT_NAME,
            "description": "MCP Hub for 20+ services - Optimized for 32 vCPU/32GB RAM",
            "isPublic": False
        }
    }
    
    try:
        result = make_graphql_request(query, variables)
        project = result["data"]["projectCreate"]
        print(f"✅ Created project: {project['name']} (ID: {project['id']})")
        
        # Get production environment ID
        for env in project["environments"]["edges"]:
            if env["node"]["name"] == "production":
                return project["id"], env["node"]["id"]
        
        return project["id"], None
    except Exception as e:
        print(f"❌ Failed to create project: {e}")
        sys.exit(1)

def set_environment_variables(project_id: str, environment_id: str):
    """Set environment variables for the project"""
    query = """
    mutation SetEnvVars($projectId: String!, $environmentId: String!, $variables: EnvironmentVariablesInput!) {
        variableCollectionUpsert(
            projectId: $projectId
            environmentId: $environmentId
            variables: $variables
        )
    }
    """
    
    # Convert env vars to Railway format
    railway_vars = {}
    for key, value in ENV_VARS.items():
        railway_vars[key] = value
    
    variables = {
        "projectId": project_id,
        "environmentId": environment_id,
        "variables": railway_vars
    }
    
    try:
        make_graphql_request(query, variables)
        print(f"✅ Set {len(ENV_VARS)} environment variables")
    except Exception as e:
        print(f"❌ Failed to set environment variables: {e}")

def setup_deployment_config(project_id: str):
    """Configure deployment settings"""
    # Create railway.toml for deployment configuration
    config = {
        "build": {
            "builder": "DOCKERFILE",
            "dockerfilePath": "./deployment/docker/Dockerfile.railway"
        },
        "deploy": {
            "startCommand": "gunicorn mcp_hub.main:app --workers 16 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 3
        }
    }
    
    with open("railway.toml", "w") as f:
        import toml
        toml.dump(config, f)
    
    print("✅ Created railway.toml configuration")

def main():
    """Main setup function"""
    print("🚀 Setting up MCP Max v2 on Railway...")
    
    # Check if we're in the right directory
    if not os.path.exists("mcp-hub"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create project
    project_id, environment_id = create_project()
    
    if not environment_id:
        print("❌ Could not find production environment")
        sys.exit(1)
    
    # Set environment variables
    set_environment_variables(project_id, environment_id)
    
    # Setup deployment config
    setup_deployment_config(project_id)
    
    print("\n✅ Railway project setup complete!")
    print(f"📝 Project ID: {project_id}")
    print(f"🌍 Environment ID: {environment_id}")
    print("\n🚂 To deploy, run: railway up")
    
    # Save project info for future use
    with open(".railway-project.json", "w") as f:
        json.dump({
            "projectId": project_id,
            "environmentId": environment_id,
            "projectName": PROJECT_NAME
        }, f, indent=2)

if __name__ == "__main__":
    main()
