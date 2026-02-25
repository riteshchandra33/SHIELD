"""
ChromaDB Deployment Script for Emergency Response System
Configured for all-mpnet-base-v2 (768-dimensional embeddings)
"""

import chromadb
import json
import numpy as np
from typing import List, Dict, Tuple
import os


class ChromaDBDeployment:
    """
    ChromaDB Deployment Manager
    Handles setup, data loading, and testing of vector database
    """

    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initialize deployment manager

        Args:
            db_path: Path to ChromaDB persistent storage
        """
        self.db_path = db_path
        self.client = None
        self.collection = None
        self.collection_name = "emergency_scenarios"

    def setup_vector_database(self) -> None:
        """Setup ChromaDB persistent client and create collection"""
        print("=" * 70)
        print("STEP 1: SETUP VECTOR DATABASE")
        print("=" * 70)

        # Create persistent client
        print(f"\n[1.1] Creating ChromaDB persistent client...")
        print(f"      Database path: {self.db_path}")
        self.client = chromadb.PersistentClient(path=self.db_path)
        print("       Client created successfully")

        # Create or get collection with cosine distance metric
        print(f"\n[1.2] Creating collection '{self.collection_name}'...")
        print(f"      Distance metric: cosine")
        print(f"      Embedding dimension: 768 (all-mpnet-base-v2)")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"       Collection created")
        print(f"       Collection ID: {self.collection.id}")
        print(f"       Collection metadata: {self.collection.metadata}")

        print(f"\n Vector database setup complete!")

    def load_scenarios(self, json_file: str = "data/embedding_ready_scenarios.json") -> List[Dict]:
        """
        Load scenarios from JSON file to ChromaDB

        Args:
            json_file: Path to embedding-ready scenarios JSON file

        Returns:
            List of scenario dictionaries
        """
        print("\n" + "=" * 70)
        print("STEP 2: LOAD SCENARIOS TO DATABASE")
        print("=" * 70)

        # Read scenarios from JSON
        print(f"\n[2.1] Reading scenarios from {json_file}...")
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Scenario file not found: {json_file}")

        with open(json_file, "r") as f:
            scenarios = json.load(f)

        print(f"       Loaded {len(scenarios)} scenarios from file")

        # Extract data components
        print(f"\n[2.2] Extracting scenario components...")
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for scenario in scenarios:
            ids.append(scenario["id"])
            documents.append(scenario["text"])
            embeddings.append(scenario["embedding"])
            metadatas.append(scenario["metadata"])

        print(f"       Extracted components:")
        print(f"        • IDs: {len(ids)}")
        print(f"        • Documents: {len(documents)}")
        print(f"        • Embeddings: {len(embeddings)} (dimension: {len(embeddings[0])})")
        print(f"        • Metadata: {len(metadatas)}")

        # Verify embedding dimension
        if len(embeddings[0]) != 768:
            print(f"        WARNING: Expected 768-dim embeddings, found {len(embeddings[0])}-dim")
            print(f"          Make sure you're using all-mpnet-base-v2!")

        # Add to ChromaDB collection
        print(f"\n[2.3] Adding scenarios to ChromaDB collection...")
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"       All scenarios added successfully")

        # Verify data load
        print(f"\n[2.4] Verifying data load...")
        count = self.collection.count()
        print(f"       Total items in collection: {count}")

        if count == len(scenarios):
            print(f"       VERIFICATION PASSED: All {count} scenarios loaded correctly!")
        else:
            print(f"        WARNING: Expected {len(scenarios)} scenarios, found {count}")

        return scenarios

    def generate_query_embedding(self, query_text: str, scenarios: List[Dict]) -> List[float]:
        """
        Generate query embedding based on keyword matching

        Note: This is a simplified approach for demonstration.
        For production, use sentence-transformers with all-mpnet-base-v2.

        Args:
            query_text: Query string
            scenarios: List of scenarios with embeddings

        Returns:
            768-dimensional embedding vector
        """
        query_lower = query_text.lower()
        keywords = query_lower.split()

        # Find best matching scenario based on keywords
        scenario_scores = []
        for scenario in scenarios:
            text_lower = scenario["text"].lower()
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scenario_scores.append((score, scenario["embedding"]))

        # Sort by score
        scenario_scores.sort(reverse=True, key=lambda x: x[0])

        # Use best matching scenario's embedding as base
        base_embedding = (scenario_scores[0][1]
                          if scenario_scores[0][0] > 0
                          else scenarios[0]["embedding"])

        # Add small noise and normalize
        noise = np.random.randn(768) * 0.1
        query_embedding = np.array(base_embedding) + noise
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        return query_embedding.tolist()

    def test_retrieval(self, scenarios: List[Dict]) -> Dict:
        """
        Test retrieval with sample queries

        Args:
            scenarios: List of scenarios for embedding generation

        Returns:
            Dictionary with test results
        """
        print("\n" + "=" * 70)
        print("STEP 3: TEST RETRIEVAL")
        print("=" * 70)

        # Define test queries
        test_queries = [
            "two vehicle accident no injuries",
            "car crash blocking traffic",
            "property damage only"
        ]

        print(f"\n[3.1] Defined test queries:")
        for i, query in enumerate(test_queries, 1):
            print(f"      {i}. \"{query}\"")

        print(f"\n[3.2] Testing retrieval for each query...")
        print("=" * 70)

        results_summary = []

        for query_num, query_text in enumerate(test_queries, 1):
            print(f"\n\n QUERY {query_num}: \"{query_text}\"")
            print("-" * 70)

            # Generate query embedding
            query_embedding = self.generate_query_embedding(query_text, scenarios)

            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )

            print(f"\nTop 3 Results:")

            # Process results
            query_results = []
            for i in range(len(results['ids'][0])):
                scenario_id = results['ids'][0][i]
                document = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]

                # Calculate similarity score
                similarity = (1 - distance) * 100

                print(f"\n  Rank #{i + 1}")
                print(f"  {'' * 66}")
                print(f"  ID: {scenario_id}")
                print(f"  Similarity: {similarity:.2f}%")
                print(f"  Event Type: {metadata['event_type']}")
                print(f"  Severity: {metadata['severity']}")
                print(f"  Injuries: {metadata['injuries']}")
                print(f"  Vehicles: {metadata.get('vehicles', 'N/A')}")
                print(f"  Text: {document[:120]}...")

                # Check relevance threshold
                if similarity >= 70:
                    print(f"   RELEVANT (≥70% similarity)")
                    relevance = "PASS"
                else:
                    print(f"    LOW RELEVANCE (<70% similarity)")
                    relevance = "REVIEW"

                query_results.append({
                    'rank': i + 1,
                    'id': scenario_id,
                    'similarity': similarity,
                    'event_type': metadata['event_type'],
                    'relevance': relevance
                })

            # Store summary for this query
            top_result = query_results[0]
            results_summary.append({
                'query': query_text,
                'top_id': top_result['id'],
                'top_similarity': top_result['similarity'],
                'top_event_type': top_result['event_type'],
                'status': top_result['relevance'],
                'all_results': query_results
            })

        # Print summary
        print("\n\n" + "=" * 70)
        print(" TEST SUMMARY")
        print("=" * 70)

        pass_count = sum(1 for r in results_summary if r['top_similarity'] >= 70)

        for result in results_summary:
            status_icon = "" if result['status'] == "PASS" else ""
            print(f"\n{status_icon} Query: \"{result['query']}\"")
            print(f"   Top Match: {result['top_id']}")
            print(f"   Event Type: {result['top_event_type']}")
            print(f"   Similarity: {result['top_similarity']:.2f}%")
            print(f"   Status: {result['status']}")

        print("\n" + "=" * 70)
        print(f"Overall: {pass_count}/{len(test_queries)} queries with ≥70% similarity")

        if pass_count == len(test_queries):
            print(" ALL QUERIES RETURNED RELEVANT RESULTS")
        elif pass_count > 0:
            print("  SOME QUERIES NEED REVIEW")
        else:
            print(" LOW RELEVANCE - Consider using real embeddings with all-mpnet-base-v2")

        print("=" * 70)

        return {
            'total_queries': len(test_queries),
            'passed': pass_count,
            'results': results_summary
        }

    def deploy(self, json_file: str = "data/embedding_ready_scenarios.json") -> Dict:
        """
        Complete deployment pipeline

        Args:
            json_file: Path to scenarios JSON file

        Returns:
            Deployment results dictionary
        """
        print("\n")
        print("=" * 70)
        print("   SHIELD EMERGENCY RESPONSE SYSTEM - CHROMADB DEPLOYMENT")
        print("=" * 70)

        # Step 1: Setup database
        self.setup_vector_database()

        # Step 2: Load scenarios
        scenarios = self.load_scenarios(json_file)

        # Step 3: Test retrieval
        test_results = self.test_retrieval(scenarios)

        # Final summary
        print("\n\n" + "=" * 70)
        print(" DEPLOYMENT COMPLETE")
        print("=" * 70)
        print("\nDeployment Summary:")
        print(f"  • Database Path: {self.db_path}")
        print(f"  • Collection Name: {self.collection_name}")
        print(f"  • Total Scenarios: {self.collection.count()}")
        print(f"  • Embedding Model: all-mpnet-base-v2")
        print(f"  • Embedding Dimension: 768")
        print(f"  • Distance Metric: cosine")
        print(f"  • Retrieval Tests Passed: {test_results['passed']}/{test_results['total_queries']}")
        print(
            f"  • Status: {' Operational' if test_results['passed'] == test_results['total_queries'] else ' Needs Review'}")
        print("=" * 70)

        return {
            'database_path': self.db_path,
            'collection_name': self.collection_name,
            'total_scenarios': self.collection.count(),
            'test_results': test_results
        }


def main():
    """Main execution function"""
    # Initialize deployment
    deployer = ChromaDBDeployment(db_path="./chroma_db")

    # Run full deployment
    results = deployer.deploy(json_file="/Users/riteshchandra/PycharmProjects/SHIELD/embedding_ready_scenarios.json")

    # Additional notes
    print("\n IMPORTANT NOTES:")
    print("=" * 70)
    print("1. For production, install sentence-transformers:")
    print("   pip install sentence-transformers torch")
    print("\n2. Use all-mpnet-base-v2 model for 768-dimensional embeddings:")
    print("   from sentence_transformers import SentenceTransformer")
    print("   model = SentenceTransformer('all-mpnet-base-v2')")
    print("\n3. Generate real embeddings:")
    print("   embeddings = model.encode(texts)")
    print("\n4. Current implementation uses simulated embeddings for demo")
    print("   For production queries, use real embeddings from all-mpnet-base-v2")
    print("=" * 70)


if __name__ == "__main__":
    main()
