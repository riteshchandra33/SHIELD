import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load embedding model for semantic similarity
model = SentenceTransformer('all-mpnet-base-v2')

# Define key questions for answer relevancy
KEY_QUESTIONS = [
    {
        "question": "What type of event happened?",
        "required_fields": ["event_type_expanded", "primary_category"],
        "weight": 1.0
    },
    {
        "question": "Where did it happen?",
        "required_fields": ["location_details"],
        "weight": 1.0
    },
    {
        "question": "Who reported it?",
        "required_fields": ["event_type_shorthand", "scenario_id"],
        "weight": 0.5
    },
    {
        "question": "What happened?",
        "required_fields": ["complaint_expanded", "incident_type"],
        "weight": 1.0
    },
    {
        "question": "Any injuries?",
        "required_fields": ["injury_details"],
        "weight": 1.0
    }
]

# Define critical fields for context precision/recall
CRITICAL_CONTEXT_FIELDS = [
    "scenario_id",
    "event_type_expanded",
    "complaint_expanded",
    "primary_category",
    "incident_type",
    "severity"
]


def calculate_semantic_similarity(text1, text2):
    """Calculate cosine similarity between two texts using embeddings"""
    if not text1 or not text2:
        return 0.0

    emb1 = model.encode([text1], normalize_embeddings=True)
    emb2 = model.encode([text2], normalize_embeddings=True)
    similarity = cosine_similarity(emb1, emb2)[0][0]
    return float(similarity)


def calculate_bertscore_proxy(original, expanded):
    """
    Calculate BERTScore-like metric using semantic similarity
    This is a proxy since full BERTScore requires the bert-score library
    Scale: 0.0 to 1.0
    """
    # Calculate bidirectional similarity
    similarity = calculate_semantic_similarity(original, expanded)

    # Penalize if expanded is significantly longer (possible hallucination)
    len_ratio = len(expanded) / len(original) if len(original) > 0 else 1.0
    if len_ratio > 2.0:  # Expanded is more than 2x longer
        hallucination_penalty = 0.9
    elif len_ratio > 1.5:
        hallucination_penalty = 0.95
    else:
        hallucination_penalty = 1.0

    bertscore = similarity * hallucination_penalty
    return round(bertscore, 3)


def check_faithfulness(original, expanded):
    """
    Check if expanded text is faithful to original (no hallucinations)
    Returns score 0.0-1.0
    """
    # High semantic similarity = high faithfulness
    similarity = calculate_semantic_similarity(original, expanded)

    # Check for key term preservation
    original_words = set(original.lower().split())
    expanded_words = set(expanded.lower().split())

    # Calculate word overlap (Jaccard similarity)
    if len(original_words) > 0:
        overlap = len(original_words & expanded_words) / len(original_words)
    else:
        overlap = 0.0

    # Faithfulness is weighted average of semantic similarity and word overlap
    faithfulness = 0.7 * similarity + 0.3 * overlap
    return round(faithfulness, 3)


def can_answer_question(scenario, question_spec):
    """Check if scenario has data to answer a specific question"""
    required_fields = question_spec["required_fields"]

    for field in required_fields:
        value = scenario.get(field)
        if value is not None:
            if isinstance(value, str) and value.strip():
                return True
            elif isinstance(value, dict) and any(value.values()):
                return True
            elif isinstance(value, list) and value:
                return True
    return False


def check_context_precision_recall(scenario):
    """
    Check context precision and recall for critical fields
    Precision: Are critical fields non-empty/valid?
    Recall: Are all critical fields captured?
    """
    captured_fields = []
    valid_fields = []

    for field in CRITICAL_CONTEXT_FIELDS:
        value = scenario.get(field)

        # Check if field is captured (exists)
        if value is not None:
            captured_fields.append(field)

            # Check if field is valid (not empty/meaningful)
            if isinstance(value, str) and value.strip():
                valid_fields.append(field)
            elif isinstance(value, dict) and any(value.values()):
                valid_fields.append(field)
            elif isinstance(value, list) and value:
                valid_fields.append(field)
            elif not isinstance(value, (str, dict, list)):
                valid_fields.append(field)

    total_critical = len(CRITICAL_CONTEXT_FIELDS)

    # Recall: How many critical fields were captured?
    context_recall = len(captured_fields) / total_critical if total_critical > 0 else 0.0

    # Precision: Of captured fields, how many are valid/non-junk?
    context_precision = len(valid_fields) / len(captured_fields) if len(captured_fields) > 0 else 0.0

    return {
        "context_precision": round(context_precision, 2),
        "context_recall": round(context_recall, 2),
        "captured_fields": captured_fields,
        "valid_fields": valid_fields
    }


def validate_quality_metrics(input_json, output_json):
    """
    Perform comprehensive quality validation:
    - Semantic similarity (original vs expanded)
    - BERTScore proxy
    - Faithfulness (hallucination check)
    - Answer relevancy (key questions)
    - Context precision and recall
    """

    with open(input_json, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"Running quality validation for {len(scenarios)} scenarios...")
    print(f"Metrics: Semantic Similarity, BERTScore, Faithfulness, Answer Relevancy, Context P/R\n")

    high_quality = 0
    medium_quality = 0
    low_quality = 0

    for i, scenario in enumerate(scenarios, 1):
        scenario_id = scenario.get("scenario_id", f"Scenario_{i}")

        # Get texts for comparison
        original = scenario.get("complaint_shorthand", "")
        expanded = scenario.get("complaint_expanded", "")

        # 1. Semantic Similarity
        semantic_sim = calculate_semantic_similarity(original, expanded)

        # 2. BERTScore (proxy)
        bertscore = calculate_bertscore_proxy(original, expanded)

        # 3. Faithfulness
        faithfulness = check_faithfulness(original, expanded)

        # 4. Answer Relevancy (Key Questions)
        question_results = {}
        answered_count = 0
        total_weight = 0
        answered_weight = 0

        for q_spec in KEY_QUESTIONS:
            question = q_spec["question"]
            can_answer = can_answer_question(scenario, q_spec)
            weight = q_spec["weight"]

            question_results[question] = can_answer
            total_weight += weight

            if can_answer:
                answered_count += 1
                answered_weight += weight

        answer_relevancy = answered_weight / total_weight if total_weight > 0 else 0.0

        # 5. Context Precision and Recall
        context_metrics = check_context_precision_recall(scenario)

        # Add all metrics to scenario
        scenario["quality_metrics"] = {
            "semantic_similarity": round(semantic_sim, 3),
            "bertscore": bertscore,
            "faithfulness": faithfulness,
            "answer_relevancy": round(answer_relevancy, 3),
            "context_precision": context_metrics["context_precision"],
            "context_recall": context_metrics["context_recall"]
        }

        # Store individual components
        scenario["semantic_similarity_score"] = round(semantic_sim, 3)
        scenario["bertscore"] = bertscore
        scenario["faithfulness_score"] = faithfulness
        scenario["answer_relevancy_score"] = round(answer_relevancy, 3)
        scenario["context_precision"] = context_metrics["context_precision"]
        scenario["context_recall"] = context_metrics["context_recall"]
        scenario["key_questions_results"] = question_results
        scenario["questions_answered_count"] = answered_count

        # Determine quality level
        avg_quality = (semantic_sim + bertscore + faithfulness + answer_relevancy) / 4

        if avg_quality >= 0.8:
            high_quality += 1
            status = ""
        elif avg_quality >= 0.6:
            medium_quality += 1
            status = ""
        else:
            low_quality += 1
            status = ""

        # Print progress
        print(f"{status} {scenario_id}: Sim={semantic_sim:.2f}, BERT={bertscore:.2f}, "
              f"Faith={faithfulness:.2f}, Ans={answer_relevancy:.2f}, "
              f"P={context_metrics['context_precision']:.2f}, R={context_metrics['context_recall']:.2f}")

    # Save results
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'=' * 70}")
    print("QUALITY METRICS VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total scenarios: {len(scenarios)}")
    print(f"High quality (≥80%): {high_quality} ({high_quality / len(scenarios) * 100:.1f}%)")
    print(f"Medium quality (60-79%): {medium_quality} ({medium_quality / len(scenarios) * 100:.1f}%)")
    print(f"Low quality (<60%): {low_quality} ({low_quality / len(scenarios) * 100:.1f}%)")
    print(f"\nOutput saved to: {output_json}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_with_completeness.json"
    output_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_with_quality.json"

    validate_quality_metrics(input_json, output_json)
