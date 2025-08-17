#!/usr/bin/env python3
"""Deploy to Railway using GraphQL API with proper authentication"""

import requests
import json
import subprocess
import sys

# Railway API configuration
RAILWAY_API_TOKEN = "ce03376f-6cf9-43ea-b678-12055cc20a7c"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

headers = {
    "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
    "Content-Type": "application/json"
}

def test_auth():
    """Test if the API token is valid"""
    query = """
    query Me {
        me {
            id
            email
            name
        }
    }
    """
    
    response = requests.post(RAILWAY_API_URL, json={"query": query}, headers=headers)
    data = response.json()
    
    if "errors" in data:
        print(f"Authentication failed: {data['errors']}")
        return False
    
    if "data" in data and data["data"]["me"]:
        user = data["data"]["me"]
        print(f"Authenticated as: {user.get('name', 'Unknown')} ({user.get('email', 'Unknown')})")
        return True
    
    return False

def list_projects():
    """List existing projects"""
    query = """
    query Projects {
        projects {
            edges {
                node {
                    id
                    name
                    createdAt
                }
            }
        }
    }
    """
    
    response = requests.post(RAILWAY_API_URL, json={"query": query}, headers=headers)
    data = response.json()
    
    if "errors" in data:
        print(f"Error listing projects: {data['errors']}")
        return []
    
    projects = []
    if "data" in data and data["data"]["projects"]:
        for edge in data["data"]["projects"]["edges"]:
            projects.append(edge["node"])
    
    return projects

def create_project_with_service():
    """Create a new project with a service using Railway API"""
    # First create the project
    create_project_query = """
    mutation CreateProject {
        projectCreate(input: {
            name: "mcp-max-v2"
            description: "MCP Hub with 20+ MCP servers"
            isPublic: false
            prDeploys: false
            defaultEnvironmentName: "production"
        }) {
            id
            name
            defaultEnvironmentId
        }
    }
    """
    
    response = requests.post(RAILWAY_API_URL, json={"query": create_project_query}, headers=headers)
    data = response.json()
    
    if "errors" in data:
        print(f"Error creating project: {data['errors']}")
        return None, None
    
    project = data["data"]["projectCreate"]
    project_id = project["id"]
    environment_id = project["defaultEnvironmentId"]
    
    print(f"Created project: {project['name']} (ID: {project_id})")
    
    # Create a service in the project
    create_service_query = """
    mutation CreateService($projectId: String!, $environmentId: String!) {
        serviceCreate(input: {
            projectId: $projectId
            name: "mcp-hub"
            source: {
                repo: {
                    fullRepoName: "railwayapp/starters"
                    branch: "master"
                }
            }
        }) {
            id
            name
        }
    }
    """
    
    service_response = requests.post(
        RAILWAY_API_URL,
        json={
            "query": create_service_query,
            "variables": {
                "projectId": project_id,
                "environmentId": environment_id
            }
        },
        headers=headers
    )
    
    service_data = service_response.json()
    
    if "errors" in service_data:
        print(f"Error creating service: {service_data['errors']}")
        # Try without source
        create_empty_service_query = """
        mutation CreateService($projectId: String!) {
            serviceCreate(input: {
                projectId: $projectId
                name: "mcp-hub"
            }) {
                id
                name
            }
        }
        """
        
        service_response = requests.post(
            RAILWAY_API_URL,
            json={
                "query": create_empty_service_query,
                "variables": {
                    "projectId": project_id
                }
            },
            headers=headers
        )
        service_data = service_response.json()
        
        if "errors" in service_data:
            print(f"Error creating empty service: {service_data['errors']}")
            return project_id, None
    
    if "data" in service_data and service_data["data"]["serviceCreate"]:
        service = service_data["data"]["serviceCreate"]
        print(f"Created service: {service['name']} (ID: {service['id']})")
        return project_id, service["id"]
    
    return project_id, None

def get_project_token(project_id):
    """Get a project token for deployment"""
    query = """
    mutation CreateProjectToken($projectId: String!) {
        projectTokenCreate(input: {
            projectId: $projectId
            name: "Deployment Token"
            environmentId: null
        }) {
            token
        }
    }
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={
            "query": query,
            "variables": {"projectId": project_id}
        },
        headers=headers
    )
    data = response.json()
    
    if "errors" in data:
        print(f"Error creating project token: {data['errors']}")
        return None
    
    if "data" in data and data["data"]["projectTokenCreate"]:
        return data["data"]["projectTokenCreate"]["token"]
    
    return None

def main():
    print("Testing Railway API authentication...")
    
    if not test_auth():
        print("\nAuthentication failed. Please check your API token.")
        sys.exit(1)
    
    print("\nListing existing projects...")
    projects = list_projects()
    
    mcp_project = None
    if projects:
        print(f"Found {len(projects)} existing projects:")
        for p in projects:
            print(f"  - {p['name']} (ID: {p['id']})")
            if "mcp" in p['name'].lower():
                mcp_project = p
    
    if mcp_project:
        print(f"\nUsing existing project: {mcp_project['name']} (ID: {mcp_project['id']})")
        project_id = mcp_project['id']
        
        # Get a project token for deployment
        print("\nCreating project token for deployment...")
        project_token = get_project_token(project_id)
        
        if project_token:
            print(f"\nProject token created successfully!")
            print(f"\nTo deploy using Railway CLI:")
            print(f"export RAILWAY_TOKEN={project_token}")
            print(f"railway link {project_id}")
            print(f"railway up")
            
            # Save token to file for easy access
            with open(".railway-token", "w") as f:
                f.write(project_token)
            print(f"\nToken saved to .railway-token")
    else:
        print("\nCreating new project for MCP Max v2...")
        project_id, service_id = create_project_with_service()
        
        if project_id:
            print(f"\nProject created successfully!")
            print(f"Project ID: {project_id}")
            if service_id:
                print(f"Service ID: {service_id}")
            print(f"\nView your project at: https://railway.app/project/{project_id}")

if __name__ == "__main__":
    main()
