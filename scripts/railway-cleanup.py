#!/usr/bin/env python3
"""
Railway Project Cleanup Script
Deletes specified Railway projects using the API
"""

import requests
import sys

# Railway API configuration
RAILWAY_API_TOKEN = "ce03376f-6cf9-43ea-b678-12055cc20a7c"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

# Projects to delete
PROJECTS_TO_DELETE = [
    "mcp-max-v1",
    "empowering-clarity",
    "helpful-enjoyment",
    "efficient-nourishment",
    "unknown-tomatoes",
    "terrible-fuel",
    "wakeful-wax",
    "courageous-stop",
    "railway-shell-sync-demo",
    "32gb-windsurf"
]

def get_project_id(project_name):
    """Get project ID by name"""
    query = """
    query {
        projects {
            edges {
                node {
                    id
                    name
                }
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(RAILWAY_API_URL, json={"query": query}, headers=headers)
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        print(response.text)
        return None
        
    data = response.json()
    
    if "errors" in data:
        print(f"GraphQL Errors: {data['errors']}")
        return None
    
    if "data" not in data or "projects" not in data["data"]:
        print(f"Unexpected response structure: {data}")
        return None
    
    for edge in data["data"]["projects"]["edges"]:
        if edge["node"]["name"] == project_name:
            return edge["node"]["id"]
    return None

def delete_project(project_id, project_name):
    """Delete a project by ID"""
    mutation = """
    mutation($projectId: String!) {
        projectDelete(id: $projectId)
    }
    """
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    variables = {"projectId": project_id}
    response = requests.post(RAILWAY_API_URL, json={"query": mutation, "variables": variables}, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Deleted: {project_name}")
        return True
    else:
        print(f"❌ Failed to delete: {project_name}")
        return False

def main():
    print("🧹 Railway Cleanup Script")
    print(f"Will delete {len(PROJECTS_TO_DELETE)} projects\n")
    
    # First, find the duplicate mcp-max-v2
    print("🔍 Finding duplicate mcp-max-v2...")
    query = """
    query {
        me {
            projects {
                edges {
                    node {
                        id
                        name
                        createdAt
                        environments {
                            edges {
                                node {
                                    deployments {
                                        edges {
                                            node {
                                                id
                                                status
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(RAILWAY_API_URL, json={"query": query}, headers=headers)
    data = response.json()
    
    mcp_v2_projects = []
    for edge in data["data"]["me"]["projects"]["edges"]:
        if edge["node"]["name"] == "mcp-max-v2":
            has_deployments = False
            for env in edge["node"]["environments"]["edges"]:
                if env["node"]["deployments"]["edges"]:
                    has_deployments = True
                    break
            mcp_v2_projects.append({
                "id": edge["node"]["id"],
                "created": edge["node"]["createdAt"],
                "has_deployments": has_deployments
            })
    
    # Delete the one without deployments or the older one
    if len(mcp_v2_projects) == 2:
        # Delete the one without deployments
        for proj in mcp_v2_projects:
            if not proj["has_deployments"]:
                print(f"🗑️  Deleting duplicate mcp-max-v2 (no deployments)")
                delete_project(proj["id"], "mcp-max-v2 (duplicate)")
                break
    
    # Delete all projects in the list
    deleted_count = 0
    for project_name in PROJECTS_TO_DELETE:
        project_id = get_project_id(project_name)
        if project_id:
            if delete_project(project_id, project_name):
                deleted_count += 1
        else:
            print(f"⚠️  Not found: {project_name}")
    
    print(f"\n✨ Cleanup complete! Deleted {deleted_count} projects.")

if __name__ == "__main__":
    main()
