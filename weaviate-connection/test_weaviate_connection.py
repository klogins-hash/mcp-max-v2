#!/usr/bin/env python3
"""
Test connection to Weaviate instance on Railway
"""

import weaviate
from weaviate.auth import AuthApiKey
import requests
import json

# Weaviate instance URL
WEAVIATE_URL = "https://weaviate-production-5bc1.up.railway.app"

def test_direct_connection():
    """Test direct HTTP connection to Weaviate"""
    print("Testing direct HTTP connection...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{WEAVIATE_URL}/v1")
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        
        # Test ready endpoint
        response = requests.get(f"{WEAVIATE_URL}/v1/meta")
        print(f"\nMeta endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("Meta info:", json.dumps(response.json(), indent=2))
            
        # Test schema endpoint
        response = requests.get(f"{WEAVIATE_URL}/v1/schema")
        print(f"\nSchema endpoint status: {response.status_code}")
        if response.status_code == 200:
            schema = response.json()
            print(f"Number of classes: {len(schema.get('classes', []))}")
            for cls in schema.get('classes', []):
                print(f"  - Class: {cls.get('class')}")
                
    except Exception as e:
        print(f"Direct connection error: {e}")

def test_weaviate_client():
    """Test connection using Weaviate Python client"""
    print("\n\nTesting Weaviate Python client connection...")
    
    try:
        # Try connecting without authentication first
        client = weaviate.Client(
            url=WEAVIATE_URL,
            timeout_config=(5, 15)  # 5 second connect, 15 second read timeout
        )
        
        # Test if client is ready
        if client.is_ready():
            print("✓ Weaviate client connected successfully!")
            
            # Get meta information
            meta = client.get_meta()
            print(f"\nWeaviate version: {meta.get('version')}")
            
            # Get schema
            schema = client.schema.get()
            print(f"\nNumber of classes in schema: {len(schema.get('classes', []))}")
            
            # List all classes
            for cls in schema.get('classes', []):
                class_name = cls.get('class')
                print(f"\nClass: {class_name}")
                
                # Get object count for this class
                try:
                    result = client.query.aggregate(class_name).with_meta_count().do()
                    count = result.get('data', {}).get('Aggregate', {}).get(class_name, [{}])[0].get('meta', {}).get('count', 0)
                    print(f"  Objects: {count}")
                except:
                    print(f"  Objects: Unable to count")
                
                # Show properties
                properties = cls.get('properties', [])
                if properties:
                    print(f"  Properties ({len(properties)}):")
                    for prop in properties[:5]:  # Show first 5 properties
                        print(f"    - {prop.get('name')} ({prop.get('dataType', [])})")
                    if len(properties) > 5:
                        print(f"    ... and {len(properties) - 5} more")
        else:
            print("✗ Weaviate client is not ready")
            
    except Exception as e:
        print(f"Weaviate client error: {e}")
        print("\nTrying with authentication...")
        
        # You might need to add authentication
        # client = weaviate.Client(
        #     url=WEAVIATE_URL,
        #     auth_client_secret=AuthApiKey(api_key="YOUR_API_KEY")
        # )

if __name__ == "__main__":
    print(f"Connecting to Weaviate at: {WEAVIATE_URL}\n")
    
    # Test direct HTTP connection
    test_direct_connection()
    
    # Test Weaviate client
    test_weaviate_client()
