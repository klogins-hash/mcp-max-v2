#!/usr/bin/env python3
"""Test Home Assistant connection"""

import asyncio
import aiohttp
import json
import os

async def test_connection():
    url = "https://f530xzyua6tlmxk3nc0epcqgabztmouj.ui.nabu.casa"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiY2JmZGU4NDA3ODM0ODMyOGRkYWJmMGY5ODNjOTRlMCIsImlhdCI6MTc1NTM5NTU4NywiZXhwIjoyMDcwNzU1NTg3fQ.19EaM0_E1Rvc-7UZKzg9cJMJHijWFyLFDB1JefsDGnQ"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Test API connection
        print(f"Testing connection to {url}")
        try:
            async with session.get(f"{url}/api/", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ API connection successful!")
                    print(f"Response: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ API error: {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return
        
        # Get config
        try:
            async with session.get(f"{url}/api/config", headers=headers) as response:
                if response.status == 200:
                    config = await response.json()
                    print(f"\n✅ Home Assistant version: {config.get('version', 'Unknown')}")
                    print(f"Location: {config.get('location_name', 'Unknown')}")
                    print(f"Components: {len(config.get('components', []))} loaded")
        except Exception as e:
            print(f"❌ Config error: {str(e)}")
        
        # Get some states
        try:
            async with session.get(f"{url}/api/states", headers=headers) as response:
                if response.status == 200:
                    states = await response.json()
                    print(f"\n✅ Found {len(states)} entities")
                    
                    # Show first few entities
                    print("\nFirst 5 entities:")
                    for entity in states[:5]:
                        print(f"  - {entity['entity_id']}: {entity['state']}")
        except Exception as e:
            print(f"❌ States error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
