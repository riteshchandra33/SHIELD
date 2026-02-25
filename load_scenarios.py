#!/usr/bin/env python3
"""
Load pre-computed embeddings from embedding_ready_scenarios.json into ChromaDB.
This script handles the gold standard scenarios with their existing embeddings.
"""

import json
import chromadb
from chromadb.config import Settings
from pathlib import Path

def load_scenarios_to_chromadb():
    """Load scenarios with pre-computed embeddings into ChromaDB."""
    
    # Paths
    json_file = Path("/Users/riteshchandra/PycharmProjects/SHIELD/embedding_ready_scenarios.json")
    db_path = Path("/Users/riteshchandra/PycharmProjects/SHIELD/pythonProject4/chroma_db")
    
    print(f" Loading scenarios from: {json_file}")
    
    # Load the JSON file
    with open(json_file, 'r') as f:
        scenarios = json.load(f)
    
    print(f" Loaded {len(scenarios)} scenarios")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create the collection  
    collection_name = "emergency_scenarios"
    
    # Delete existing collection if it exists to avoid conflicts
    try:
        client.delete_collection(collection_name)
        print(f"  Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create new collection WITHOUT embedding function
    # We're providing pre-computed 384-dim embeddings, so no function needed here
    collection = client.create_collection(name=collection_name)
    print(f" Created collection: {collection_name} (using pre-computed 384-dim embeddings)")
    
    # Prepare data for batch insertion
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for scenario in scenarios:
        ids.append(scenario['id'])
        documents.append(scenario['text'])
        embeddings.append(scenario['embedding'])
        
        # Clean metadata (ChromaDB doesn't accept nested dicts)
        metadata = scenario.get('metadata', {})
        flat_metadata = {
            'source': metadata.get('source', ''),
            'category': metadata.get('category', ''),
            'sub_category': metadata.get('sub_category', ''),
            'incident_type': metadata.get('incident_type', ''),
            'severity': metadata.get('severity', 'unknown'),
            'event_type': metadata.get('event_type', ''),
            'validation_status': metadata.get('validation_status', 'APPROVED'),
            'completeness_score': str(metadata.get('completeness_score', 1.0)),
            'is_complete': str(metadata.get('is_complete', True))
        }
        metadatas.append(flat_metadata)
    
    # Batch insert all scenarios with their embeddings
    print(f" Inserting {len(ids)} scenarios into ChromaDB...")
    
    # ChromaDB has a limit on batch size, so we'll do it in chunks
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"   Inserted scenarios {i+1} to {end_idx}")
    
    print(f"\n Successfully loaded {len(ids)} scenarios into ChromaDB!")
    print(f" Collection: {collection_name}")
    print(f" Database path: {db_path}")
    
    # Verify
    count = collection.count()
    print(f" Verification: Collection has {count} items")
    
    return count

if __name__ == "__main__":
    try:
        count = load_scenarios_to_chromadb()
        print(f"\n Done! {count} scenarios are now ready for use in the training system.")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
