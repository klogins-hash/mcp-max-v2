#!/usr/bin/env python3
"""Deploy to Railway using the API directly"""

import os
import requests
import json
import base64
import subprocess
import tarfile
import io
from pathlib import Path

# Railway API configuration
RAILWAY_API_TOKEN = "fJgWTDcdLr2T1T8Y8u5vQPMH"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

headers = {
    "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
    "Content-Type": "application/json"
}

def create_project():
    """Create a new Railway project"""
    query = """
    mutation CreateProject {
        projectCreate(input: {
            name: "mcp-max-v2",
            description: "MCP Hub with 20+ MCP servers"
        }) {
            id
            name
        }
    }
    """
    
    response = requests.post(RAILWAY_API_URL, json={"query": query}, headers=headers)
    data = response.json()
    
    if "errors" in data:
        print(f"Error creating project: {data['errors']}")
        return None
    
    project = data["data"]["projectCreate"]
    print(f"Created project: {project['name']} (ID: {project['id']})")
    return project["id"]

def get_project_info(project_id):
    """Get project environments"""
    query = """
    query GetProject($projectId: String!) {
        project(id: $projectId) {
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
        json={"query": query, "variables": {"projectId": project_id}}, 
        headers=headers
    )
    data = response.json()
    
    if "errors" in data:
        print(f"Error getting project: {data['errors']}")
        return None
    
    return data["data"]["project"]

def create_service(project_id, environment_id):
    """Create a service in the project"""
    query = """
    mutation CreateService($projectId: String!, $environmentId: String!) {
        serviceCreate(input: {
            projectId: $projectId,
            environmentId: $environmentId,
            name: "mcp-hub",
            source: {}
        }) {
            id
            name
        }
    }
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={
            "query": query,
            "variables": {
                "projectId": project_id,
                "environmentId": environment_id
            }
        },
        headers=headers
    )
    data = response.json()
    
    if "errors" in data:
        print(f"Error creating service: {data['errors']}")
        return None
    
    service = data["data"]["serviceCreate"]
    print(f"Created service: {service['name']} (ID: {service['id']})")
    return service["id"]

def set_environment_variables(project_id, environment_id, service_id):
    """Set environment variables for the service"""
    variables = {
        "RAILWAY_ENVIRONMENT": "production",
        "PORT": "8000",
        "GUNICORN_WORKERS": "16",
        "GUNICORN_WORKER_CONNECTIONS": "2000",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1"
    }
    
    query = """
    mutation SetVariables($projectId: String!, $environmentId: String!, $serviceId: String!, $variables: VariablesInput!) {
        variableCollectionUpsert(input: {
            projectId: $projectId,
            environmentId: $environmentId,
            serviceId: $serviceId,
            variables: $variables
        })
    }
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={
            "query": query,
            "variables": {
                "projectId": project_id,
                "environmentId": environment_id,
                "serviceId": service_id,
                "variables": variables
            }
        },
        headers=headers
    )
    data = response.json()
    
    if "errors" in data:
        print(f"Error setting variables: {data['errors']}")
        return False
    
    print("Set environment variables")
    return True

def create_tarball():
    """Create a tarball of the project"""
    print("Creating tarball of project...")
    
    # Files to exclude
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.env',
        '*.pyc',
        '.DS_Store',
        'venv',
        '.venv',
        'node_modules'
    ]
    
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if not any(pattern in file for pattern in exclude_patterns):
                    file_path = os.path.join(root, file)
                    tar.add(file_path, arcname=file_path[2:])  # Remove './' prefix
    
    tar_buffer.seek(0)
    return tar_buffer.getvalue()

def deploy_service(project_id, environment_id, service_id):
    """Deploy the service using Railway's deployment API"""
    # Create deployment
    query = """
    mutation CreateDeployment($projectId: String!, $environmentId: String!, $serviceId: String!) {
        deploymentCreate(input: {
            projectId: $projectId,
            environmentId: $environmentId,
            serviceId: $serviceId,
            meta: {
                buildCommand: "pip install -r requirements.txt",
                startCommand: "cd mcp-hub && gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers ${GUNICORN_WORKERS:-16} --worker-class uvicorn.workers.UvicornWorker"
            }
        }) {
            id
            status
        }
    }
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={
            "query": query,
            "variables": {
                "projectId": project_id,
                "environmentId": environment_id,
                "serviceId": service_id
            }
        },
        headers=headers
    )
    data = response.json()
    
    if "errors" in data:
        print(f"Error creating deployment: {data['errors']}")
        return None
    
    deployment = data["data"]["deploymentCreate"]
    print(f"Created deployment: {deployment['id']} (Status: {deployment['status']})")
    return deployment["id"]

def main():
    print("Deploying MCP Max v2 to Railway...")
    
    # Create or use existing project
    project_id = "a1c3b0f0-f3f9-4b7f-a7d5-d1b0c3e8f5a2"  # Use the existing project ID
    
    # Get project info
    project = get_project_info(project_id)
    if not project:
        print("Creating new project...")
        project_id = create_project()
        if not project_id:
            return
        project = get_project_info(project_id)
    
    # Get production environment
    environments = project["environments"]["edges"]
    production_env = next((env["node"] for env in environments if env["node"]["name"] == "production"), None)
    
    if not production_env:
        print("No production environment found")
        return
    
    environment_id = production_env["id"]
    print(f"Using environment: {production_env['name']} (ID: {environment_id})")
    
    # Create service
    service_id = create_service(project_id, environment_id)
    if not service_id:
        return
    
    # Set environment variables
    if not set_environment_variables(project_id, environment_id, service_id):
        return
    
    # Deploy
    deployment_id = deploy_service(project_id, environment_id, service_id)
    if deployment_id:
        print(f"\nDeployment initiated! ID: {deployment_id}")
        print(f"View your deployment at: https://railway.app/project/{project_id}")

if __name__ == "__main__":
    main()
