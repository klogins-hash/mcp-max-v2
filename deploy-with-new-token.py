#!/usr/bin/env python3
"""
Deploy to Railway using the new API token
"""

import requests
import json
import sys
import subprocess
import os

# New Railway API token
RAILWAY_TOKEN = "0bc37f0c-3477-4ad6-a430-a50ed86a1680"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

def test_token():
    """Test if the token is valid"""
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Simple query to test authentication
    query = """
    query {
        me {
            id
            email
        }
    }
    """
    
    response = requests.post(
        RAILWAY_API_URL,
        json={"query": query},
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        if "data" in result and result["data"]["me"]:
            print(f"✅ Token is valid! User: {result['data']['me'].get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ Token is invalid or expired")
            return False
    else:
        print(f"❌ Failed to authenticate: {response.status_code}")
        print(response.text)
        return False

def deploy_with_cli():
    """Try to deploy using CLI with token"""
    print("\n🚀 Attempting deployment with Railway CLI...")
    
    # Set up environment
    env = os.environ.copy()
    env["RAILWAY_TOKEN"] = RAILWAY_TOKEN
    
    # Try to deploy
    try:
        # First try to link or create project
        result = subprocess.run(
            ["railway", "init", "--name", "mcp-max-v2"],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Project might already exist, trying to deploy...")
        
        # Deploy
        result = subprocess.run(
            ["railway", "up", "--detach"],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Deployment started successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

def create_auth_config():
    """Create Railway auth configuration"""
    config_dir = os.path.expanduser("~/.config/railway")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "config.json")
    config = {
        "token": RAILWAY_TOKEN,
        "user": {},
        "projects": {}
    }
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created Railway config at: {config_path}")

if __name__ == "__main__":
    print("🔧 Testing Railway API token...")
    
    if test_token():
        # Create auth config
        create_auth_config()
        
        # Try deployment
        if deploy_with_cli():
            print("\n🎉 Deployment successful!")
            print("\nNext steps:")
            print("1. Check deployment status: railway status")
            print("2. View logs: railway logs")
            print("3. Get domain: railway domain")
        else:
            print("\n❌ Deployment failed. The token might not have the right permissions.")
    else:
        print("\n❌ Invalid token. Please check your Railway API token.")
        sys.exit(1)
