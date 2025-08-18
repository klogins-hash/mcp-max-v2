#!/usr/bin/env python3
"""
Spotify MCP Server - Control your music with AI
"""

import asyncio
import json
import sys
from typing import Dict, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# MCP protocol handlers
async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming MCP requests"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "spotify_play",
                    "description": "Play a song or playlist",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Song/artist/playlist name"}
                        }
                    }
                },
                {
                    "name": "spotify_pause",
                    "description": "Pause current playback"
                },
                {
                    "name": "spotify_next",
                    "description": "Skip to next track"
                },
                {
                    "name": "spotify_current",
                    "description": "Get current playing track"
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        # Initialize Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
            redirect_uri="http://localhost:8888/callback",
            scope="user-read-playback-state user-modify-playback-state"
        ))
        
        if tool_name == "spotify_play":
            query = args.get("query")
            results = sp.search(q=query, limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                sp.start_playback(uris=[track['uri']])
                return {"content": f"Now playing: {track['name']} by {track['artists'][0]['name']}"}
            
        elif tool_name == "spotify_pause":
            sp.pause_playback()
            return {"content": "Playback paused"}
            
        elif tool_name == "spotify_next":
            sp.next_track()
            return {"content": "Skipped to next track"}
            
        elif tool_name == "spotify_current":
            current = sp.current_playback()
            if current and current['item']:
                track = current['item']
                return {"content": f"Currently playing: {track['name']} by {track['artists'][0]['name']}"}
            return {"content": "Nothing is currently playing"}
    
    return {"error": "Unknown method"}

async def main():
    """Main loop - reads from stdin, writes to stdout"""
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
            
        try:
            request = json.loads(line)
            response = await handle_request(request)
            
            # Send response
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": response
            }))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id", 0),
                "error": {"code": -32603, "message": str(e)}
            }))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
