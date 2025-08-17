#!/usr/bin/env python3
"""
Weaviate Database Cleanup Script
Helps clean up and reorganize your Weaviate collections
"""

import weaviate
import json
from datetime import datetime
from typing import Dict, List, Any

WEAVIATE_URL = "https://weaviate-production-5bc1.up.railway.app"

class WeaviateCleanup:
    def __init__(self):
        self.client = weaviate.Client(url=WEAVIATE_URL, timeout_config=(5, 15))
        
    def analyze_collections(self) -> Dict[str, Any]:
        """Analyze all collections and provide recommendations"""
        schema = self.client.schema.get()
        analysis = {
            "total_objects": 0,
            "collections": [],
            "recommendations": []
        }
        
        for cls in schema.get('classes', []):
            class_name = cls.get('class')
            
            # Get object count
            try:
                result = self.client.query.aggregate(class_name).with_meta_count().do()
                count = result.get('data', {}).get('Aggregate', {}).get(class_name, [{}])[0].get('meta', {}).get('count', 0)
            except:
                count = 0
            
            analysis["total_objects"] += count
            
            collection_info = {
                "name": class_name,
                "object_count": count,
                "property_count": len(cls.get('properties', [])),
                "properties": [p.get('name') for p in cls.get('properties', [])][:5]
            }
            
            analysis["collections"].append(collection_info)
            
            # Add recommendations
            if count == 0:
                analysis["recommendations"].append(f"Consider removing empty collection: {class_name}")
            elif count > 10000:
                analysis["recommendations"].append(f"Large collection {class_name} ({count} objects) - consider archiving old data")
        
        # Check for similar collections
        collection_names = [c["name"] for c in analysis["collections"]]
        
        # Check for potential duplicates
        if "Knowledge" in collection_names and "KnowledgeV3" in collection_names:
            analysis["recommendations"].append("Consider merging Knowledge and KnowledgeV3 collections")
        
        if "Document" in collection_names and "BackupDocuments" in collection_names:
            analysis["recommendations"].append("Consider consolidating Document and BackupDocuments collections")
        
        return analysis
    
    def consolidate_knowledge_collections(self):
        """Merge Knowledge collections into a single unified collection"""
        print("Consolidating knowledge collections...")
        
        # Create new unified collection if it doesn't exist
        unified_class = {
            "class": "UnifiedKnowledge",
            "properties": [
                {"name": "title", "dataType": ["text"]},
                {"name": "content", "dataType": ["text"]},
                {"name": "question", "dataType": ["text"]},
                {"name": "answer", "dataType": ["text"]},
                {"name": "context", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]},
                {"name": "category", "dataType": ["text"]},
                {"name": "tags", "dataType": ["text[]"]},
                {"name": "confidence", "dataType": ["number"]},
                {"name": "createdAt", "dataType": ["date"]},
                {"name": "updatedAt", "dataType": ["date"]},
                {"name": "metadata", "dataType": ["text"]}
            ]
        }
        
        try:
            self.client.schema.create_class(unified_class)
            print("Created UnifiedKnowledge collection")
        except:
            print("UnifiedKnowledge collection already exists")
        
        # Migrate data from existing knowledge collections
        knowledge_collections = ["Knowledge", "KnowledgeV3", "CohereKnowledge"]
        migrated_count = 0
        
        for collection in knowledge_collections:
            try:
                result = self.client.query.get(collection).do()
                objects = result.get('data', {}).get('Get', {}).get(collection, [])
                
                for obj in objects:
                    # Map to unified schema
                    unified_obj = {
                        "title": obj.get("title", obj.get("question", "")),
                        "content": obj.get("content", obj.get("answer", "")),
                        "question": obj.get("question", ""),
                        "answer": obj.get("answer", ""),
                        "context": obj.get("context", ""),
                        "source": obj.get("source", collection),
                        "category": obj.get("category", obj.get("domain", "")),
                        "tags": obj.get("tags", []),
                        "confidence": obj.get("confidence", 1.0),
                        "createdAt": obj.get("createdAt", datetime.now().isoformat()),
                        "metadata": json.dumps({
                            "original_collection": collection,
                            "migrated_at": datetime.now().isoformat()
                        })
                    }
                    
                    # Remove None values
                    unified_obj = {k: v for k, v in unified_obj.items() if v is not None}
                    
                    try:
                        self.client.data_object.create(unified_obj, "UnifiedKnowledge")
                        migrated_count += 1
                    except Exception as e:
                        print(f"Failed to migrate object: {e}")
                
                print(f"Migrated {len(objects)} objects from {collection}")
                
            except Exception as e:
                print(f"Error migrating {collection}: {e}")
        
        return {"migrated_objects": migrated_count}
    
    def remove_empty_collections(self):
        """Remove collections with no objects"""
        schema = self.client.schema.get()
        removed = []
        
        for cls in schema.get('classes', []):
            class_name = cls.get('class')
            
            try:
                result = self.client.query.aggregate(class_name).with_meta_count().do()
                count = result.get('data', {}).get('Aggregate', {}).get(class_name, [{}])[0].get('meta', {}).get('count', 0)
                
                if count == 0:
                    self.client.schema.delete_class(class_name)
                    removed.append(class_name)
                    print(f"Removed empty collection: {class_name}")
                    
            except Exception as e:
                print(f"Error checking {class_name}: {e}")
        
        return {"removed_collections": removed}
    
    def create_optimized_schema(self):
        """Create an optimized schema for all tools integration"""
        schemas = [
            {
                "class": "ToolDocumentation",
                "description": "Documentation for all integrated tools and APIs",
                "properties": [
                    {"name": "tool_name", "dataType": ["text"]},
                    {"name": "title", "dataType": ["text"]},
                    {"name": "content", "dataType": ["text"]},
                    {"name": "category", "dataType": ["text"]},
                    {"name": "url", "dataType": ["text"]},
                    {"name": "version", "dataType": ["text"]},
                    {"name": "tags", "dataType": ["text[]"]},
                    {"name": "examples", "dataType": ["text[]"]},
                    {"name": "last_updated", "dataType": ["date"]},
                    {"name": "metadata", "dataType": ["text"]}
                ]
            },
            {
                "class": "MCPIntegration",
                "description": "MCP server integration configurations and data",
                "properties": [
                    {"name": "server_name", "dataType": ["text"]},
                    {"name": "server_type", "dataType": ["text"]},
                    {"name": "configuration", "dataType": ["text"]},
                    {"name": "status", "dataType": ["text"]},
                    {"name": "last_connected", "dataType": ["date"]},
                    {"name": "metadata", "dataType": ["text"]}
                ]
            },
            {
                "class": "UnifiedDocuments",
                "description": "Unified document storage for all sources",
                "properties": [
                    {"name": "title", "dataType": ["text"]},
                    {"name": "content", "dataType": ["text"]},
                    {"name": "summary", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                    {"name": "source_type", "dataType": ["text"]},
                    {"name": "url", "dataType": ["text"]},
                    {"name": "category", "dataType": ["text"]},
                    {"name": "tags", "dataType": ["text[]"]},
                    {"name": "language", "dataType": ["text"]},
                    {"name": "created_at", "dataType": ["date"]},
                    {"name": "updated_at", "dataType": ["date"]},
                    {"name": "metadata", "dataType": ["text"]}
                ]
            }
        ]
        
        created = []
        for schema in schemas:
            try:
                self.client.schema.create_class(schema)
                created.append(schema["class"])
                print(f"Created optimized collection: {schema['class']}")
            except:
                print(f"Collection {schema['class']} already exists")
        
        return {"created_collections": created}

def main():
    cleanup = WeaviateCleanup()
    
    print("=== Weaviate Database Analysis ===")
    analysis = cleanup.analyze_collections()
    
    print(f"\nTotal Objects: {analysis['total_objects']}")
    print(f"Total Collections: {len(analysis['collections'])}")
    
    print("\n=== Collections Overview ===")
    for col in sorted(analysis['collections'], key=lambda x: x['object_count'], reverse=True):
        print(f"{col['name']}: {col['object_count']} objects, {col['property_count']} properties")
    
    print("\n=== Recommendations ===")
    for rec in analysis['recommendations']:
        print(f"• {rec}")
    
    # Ask for user confirmation before proceeding
    print("\n=== Cleanup Options ===")
    print("1. Consolidate knowledge collections")
    print("2. Remove empty collections")
    print("3. Create optimized schema for MCP integration")
    print("4. Perform all cleanup operations")
    print("5. Exit without changes")
    
    choice = input("\nSelect an option (1-5): ")
    
    if choice == "1":
        result = cleanup.consolidate_knowledge_collections()
        print(f"\nConsolidation complete: {result}")
    elif choice == "2":
        result = cleanup.remove_empty_collections()
        print(f"\nRemoved collections: {result}")
    elif choice == "3":
        result = cleanup.create_optimized_schema()
        print(f"\nCreated collections: {result}")
    elif choice == "4":
        print("\nPerforming all cleanup operations...")
        cleanup.consolidate_knowledge_collections()
        cleanup.remove_empty_collections()
        cleanup.create_optimized_schema()
        print("\nAll cleanup operations completed!")
    
    print("\n=== Final Status ===")
    final_analysis = cleanup.analyze_collections()
    print(f"Total Objects: {final_analysis['total_objects']}")
    print(f"Total Collections: {len(final_analysis['collections'])}")

if __name__ == "__main__":
    main()
