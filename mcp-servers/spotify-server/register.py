#!/usr/bin/env python3
"""
Register Spotify MCP Server with the Hub
"""

import requests
import subprocess
import os

# Your MCP Hub URL (from Railway deployment)
HUB_URL = "https://your-mcp-hub.railway.app"

def register_spotify_server():
    """Tell the hub about our Spotify server"""
    
    # Start the Spotify server
    server_process = subprocess.Popen(
        ["python", "server.py"],
        cwd=os.path.dirname(__file__)
    )
    
    # Register with hub
    registration = {
        "name": "spotify",
        "description": "Control Spotify playback",
        "endpoint": "http://localhost:8001",  # Where this server runs
        "capabilities": ["music_control", "playback_info"],
        "health_check_path": "/health"
    }
    
    response = requests.post(f"{HUB_URL}/register", json=registration)
    
    if response.status_code == 200:
        print("✅ Spotify server registered with hub!")
    else:
        print(f"❌ Registration failed: {response.text}")

if __name__ == "__main__":
    register_spotify_server()
