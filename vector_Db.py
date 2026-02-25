import json
from sentence_transformers import SentenceTransformer

# Load 768-dimensional embedding model
embedding_model = SentenceTransformer('all-mpnet-base-v2')


def create_embedding_ready_scenarios(input_json, output_json):
    """
    Extract and format scenarios for vector database insertion:
    - id: scenario_id
    - text: complaint_expanded (text for embedding)
    - metadata: source, category, severity, tags, confidence, status
    - embedding: 768-dim vector
    """

    with open(input_json, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"\n{'=' * 70}")
    print("CREATING VECTOR DATABASE FORMAT")
    print(f"{'=' * 70}")
    print(f"Total scenarios to process: {len(scenarios)}")
    print(f"Embedding model: all-mpnet-base-v2 (768 dimensions)")
    print(f"{'=' * 70}\n")

    embedding_ready = []

    for idx, scenario in enumerate(scenarios, 1):
        scenario_id = scenario.get("scenario_id", f"Scenario_{idx}")

        # Extract text for embedding
        # Priority: complaint_expanded > complaint_shorthand
        text_for_embedding = (
                scenario.get("complaint_expanded") or
                scenario.get("complaint_shorthand") or
                scenario.get("event_type_expanded") or
                ""
        )

        if not text_for_embedding.strip():
            print(f"  Warning: {scenario_id} has no text for embedding, skipping...")
            continue

        # Build metadata
        metadata = {
            "source": scenario_id,
            "category": scenario.get("primary_category", "unknown"),
            "sub_category": scenario.get("sub_category", ""),
            "incident_type": scenario.get("incident_type", ""),
            "severity": scenario.get("severity", "medium"),
            "tags": scenario.get("controlled_tags", []),
            "validation_status": scenario.get("validation_status", "unknown"),
            "completeness_score": scenario.get("completeness_score", 0.0),
            "semantic_similarity": scenario.get("semantic_similarity_score", 0.0),
            "answer_relevancy": scenario.get("answer_relevancy_score", 0.0),
            "is_complete": scenario.get("is_complete", False),
            "event_type": scenario.get("event_type_expanded", ""),
            "location": scenario.get("location_details", {})
        }

        # Generate embedding (768-dim vector)
        print(f"Generating embedding {idx}/{len(scenarios)}: {scenario_id}...")
        embedding = embedding_model.encode(
            text_for_embedding,
            normalize_embeddings=True
        ).tolist()

        # Create vector DB record
        embedding_record = {
            "id": scenario_id,
            "text": text_for_embedding,
            "metadata": metadata,
            "embedding": embedding  # 768-dimensional vector
        }

        embedding_ready.append(embedding_record)

    # Save embedding-ready scenarios
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(embedding_ready, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'=' * 70}")
    print("EMBEDDING GENERATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total scenarios embedded: {len(embedding_ready)}")
    print(f"Embedding dimensions: {len(embedding_ready[0]['embedding']) if embedding_ready else 0}")
    print(f"Output saved to: {output_json}")
    print(f"{'=' * 70}")
    print(f"\n Ready for vector database insertion!")
    print(f"   Compatible with: ChromaDB, Pinecone, Milvus, Qdrant, Weaviate\n")


if __name__ == "__main__":
    # Input: fully validated scenarios (from Step 4)
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_validated.json"

    # Output: embedding-ready format for vector DB
    output_json = "/Users/riteshchandra/PycharmProjects/SHIELD/embedding_ready_scenarios.json"

    create_embedding_ready_scenarios(input_json, output_json)
