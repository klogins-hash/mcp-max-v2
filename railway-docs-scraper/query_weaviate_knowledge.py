#!/usr/bin/env python3
"""
Query Weaviate for Railway deployment knowledge and APIs
"""

import weaviate
import json

WEAVIATE_URL = "https://weaviate-production-5bc1.up.railway.app"

class WeaviateKnowledgeQuery:
    def __init__(self):
        self.client = weaviate.Client(url=WEAVIATE_URL)
        
    def query_railway_deployment_docs(self):
        """Query Railway deployment best practices"""
        print("Querying Railway deployment documentation...")
        
        # Query for deployment-related docs
        deployment_keywords = ["deploy", "dockerfile", "build", "environment", "variables", "config", "railway.json", "nixpacks"]
        
        results = []
        for keyword in deployment_keywords:
            query = (
                self.client.query
                .get("RailwayDocs", ["title", "content", "url"])
                .with_where({
                    "path": ["content"],
                    "operator": "Like",
                    "valueText": f"*{keyword}*"
                })
                .with_limit(5)
            )
            result = query.do()
            docs = result.get('data', {}).get('Get', {}).get('RailwayDocs', [])
            results.extend(docs)
            
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for doc in results:
            if doc['url'] not in seen_urls:
                seen_urls.add(doc['url'])
                unique_results.append(doc)
                
        print(f"Found {len(unique_results)} relevant deployment docs")
        return unique_results
    
    def query_api_credentials(self):
        """Query for API credentials and documentation"""
        print("\nQuerying API credentials and documentation...")
        
        # Query Document collection for API-related content
        api_query = (
            self.client.query
            .get("Document", ["title", "content", "api_key", "endpoint", "service_name"])
            .with_where({
                "path": ["content"],
                "operator": "Like", 
                "valueText": "*api*key*"
            })
            .with_limit(20)
        )
        
        result = api_query.do()
        api_docs = result.get('data', {}).get('Get', {}).get('Document', [])
        
        # Also check CohereKnowledge for API info
        cohere_query = (
            self.client.query
            .get("CohereKnowledge", ["title", "content"])
            .with_where({
                "path": ["content"],
                "operator": "Like",
                "valueText": "*api*"
            })
            .with_limit(10)
        )
        
        cohere_result = cohere_query.do()
        cohere_docs = cohere_result.get('data', {}).get('Get', {}).get('CohereKnowledge', [])
        
        print(f"Found {len(api_docs)} API documents and {len(cohere_docs)} knowledge entries")
        
        return {
            "api_documents": api_docs,
            "cohere_knowledge": cohere_docs
        }
    
    def save_results(self, deployment_docs, api_info):
        """Save query results to file"""
        results = {
            "railway_deployment": deployment_docs,
            "api_credentials": api_info
        }
        
        with open("weaviate_knowledge.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print("\nResults saved to weaviate_knowledge.json")
        
        # Print summary
        print("\nKey deployment topics found:")
        for doc in deployment_docs[:5]:
            print(f"  - {doc['title']}")
            
if __name__ == "__main__":
    query = WeaviateKnowledgeQuery()
    
    # Get deployment docs
    deployment_docs = query.query_railway_deployment_docs()
    
    # Get API credentials
    api_info = query.query_api_credentials()
    
    # Save results
    query.save_results(deployment_docs, api_info)
