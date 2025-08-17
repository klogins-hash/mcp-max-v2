#!/usr/bin/env python3
"""
Direct Railway deployment using API
"""

import requests
import json
import base64
import os
import sys

# Railway API configuration
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
RAILWAY_TOKEN = "ce03376f-6cf9-43ea-b678-12055cc20a7c"

def create_deployment():
    """Create a new deployment directly via Railway API"""
    
    # First, let's create a project
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Create project
    create_project_query = """
    mutation {
        projectCreate(input: {
            name: "mcp-max-v2",
            description: "MCP Hub for 20+ services",
            isPublic: false
        }) {
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
    
    response = requests.post(
        RAILWAY_API_URL,
        json={"query": create_project_query},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create project: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    if "errors" in result:
        print(f"❌ GraphQL errors: {result['errors']}")
        return False
    
    project = result["data"]["projectCreate"]
    project_id = project["id"]
    
    # Get production environment
    env_id = None
    for env in project["environments"]["edges"]:
        if env["node"]["name"] == "production":
            env_id = env["node"]["id"]
            break
    
    print(f"✅ Created project: {project['name']} (ID: {project_id})")
    print(f"✅ Environment ID: {env_id}")
    
    # Set environment variables
    env_vars = {
        "PORT": "8000",
        "MCP_HUB_PORT": "8000",
        "GUNICORN_WORKERS": "16",
        "GUNICORN_WORKER_CLASS": "uvicorn.workers.UvicornWorker",
        "GUNICORN_WORKER_CONNECTIONS": "2000",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1"
    }
    
    for key, value in env_vars.items():
        set_var_query = f"""
        mutation {{
            variableUpsert(
                projectId: "{project_id}",
                environmentId: "{env_id}",
                name: "{key}",
                value: "{value}"
            )
        }}
        """
        
        requests.post(
            RAILWAY_API_URL,
            json={"query": set_var_query},
            headers=headers
        )
    
    print(f"✅ Set {len(env_vars)} environment variables")
    
    # Create service
    create_service_query = f"""
    mutation {{
        serviceCreate(
            projectId: "{project_id}",
            environmentId: "{env_id}",
            name: "mcp-hub",
            source: {{
                repo: "https://github.com/railwayapp/nixpacks"
            }}
        ) {{
            id
            name
        }}
    }}
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={"query": create_service_query},
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Service created")
        print(f"\n📝 Project ID: {project_id}")
        print(f"🌍 Environment ID: {env_id}")
        
        # Save configuration
        with open(".railway-config.json", "w") as f:
            json.dump({
                "projectId": project_id,
                "environmentId": env_id,
                "token": RAILWAY_TOKEN
            }, f, indent=2)
        
        print("\n✅ Configuration saved to .railway-config.json")
        print("\n🚀 Next steps:")
        print("1. Link this directory to the project:")
        print(f"   railway link {project_id}")
        print("2. Deploy your code:")
        print("   railway up")
        
        return True
    else:
        print(f"❌ Failed to create service: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Railway deployment...")
    success = create_deployment()
    sys.exit(0 if success else 1)
