import json
import os
from datetime import datetime
from collections import Counter


def check_file_exists(filepath):
    """Check if file exists and return size"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return True, size
    return False, 0


def format_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def generate_validation_report(base_path, validated_json, embedding_json):
    """
    Generate comprehensive validation report with:
    - Validation status checkboxes
    - Quality metrics summary
    - File inventory
    - Deployment readiness assessment
    """

    report_path = os.path.join(base_path, "validation_summary_report.txt")

    # Load validated scenarios
    with open(validated_json, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    # Load embedding-ready scenarios if exists
    embedding_ready = []
    embedding_exists = os.path.exists(embedding_json)
    if embedding_exists:
        with open(embedding_json, "r", encoding="utf-8") as f:
            embedding_ready = json.load(f)

    # Collect statistics
    total = len(scenarios)
    status_counts = Counter(s.get("validation_status", "unknown") for s in scenarios)

    # Quality metrics averages
    avg_completeness = sum(s.get("completeness_score", 0) for s in scenarios) / total if total > 0 else 0
    avg_similarity = sum(s.get("semantic_similarity_score", 0) for s in scenarios) / total if total > 0 else 0
    avg_relevancy = sum(s.get("answer_relevancy_score", 0) for s in scenarios) / total if total > 0 else 0
    avg_context_p = sum(s.get("context_precision", 0) for s in scenarios) / total if total > 0 else 0
    avg_context_r = sum(s.get("context_recall", 0) for s in scenarios) / total if total > 0 else 0

    # Count passes
    completeness_pass = sum(1 for s in scenarios if s.get("is_complete", False))
    similarity_pass = sum(1 for s in scenarios if s.get("semantic_similarity_pass", False))
    relevancy_pass = sum(1 for s in scenarios if s.get("answer_relevancy_pass", False))

    # Embedding info
    embedding_dim = len(embedding_ready[0]["embedding"]) if embedding_ready and "embedding" in embedding_ready[0] else 0

    # Build report
    lines = []
    lines.append("=" * 80)
    lines.append("SHIELD EMERGENCY RESPONSE SYSTEM")
    lines.append("VALIDATION SUMMARY REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Report Version: 1.0")
    lines.append("")

    # ===== VALIDATION COMPLETED CHECKBOXES =====
    lines.append("=" * 80)
    lines.append(" VALIDATION COMPLETED")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"[{'' if completeness_pass == total else ''}] Completeness Check")
    lines.append(f"    - Passed: {completeness_pass}/{total} ({completeness_pass / total * 100:.1f}%)")
    lines.append(f"    - Average Score: {avg_completeness:.2f}")
    lines.append("")
    lines.append(f"[{'' if similarity_pass >= total * 0.8 else ''}] Semantic Similarity Check")
    lines.append(f"    - Passed: {similarity_pass}/{total} ({similarity_pass / total * 100:.1f}%)")
    lines.append(f"    - Average Score: {avg_similarity:.3f}")
    lines.append("")
    lines.append(f"[{'' if relevancy_pass >= total * 0.8 else ''}] Answer Relevancy Check")
    lines.append(f"    - Passed: {relevancy_pass}/{total} ({relevancy_pass / total * 100:.1f}%)")
    lines.append(f"    - Average Score: {avg_relevancy:.2f}")
    lines.append("")
    lines.append(f"[{'' if avg_context_p >= 0.8 else ''}] Context Precision")
    lines.append(f"    - Average Score: {avg_context_p:.2f}")
    lines.append("")
    lines.append(f"[{'' if avg_context_r >= 0.7 else ''}] Context Recall")
    lines.append(f"    - Average Score: {avg_context_r:.2f}")
    lines.append("")
    lines.append(f"[{'' if embedding_exists else ''}] Embedding Generation")
    lines.append(f"    - Status: {'Complete' if embedding_exists else 'Not Started'}")
    if embedding_exists:
        lines.append(f"    - Total Embeddings: {len(embedding_ready)}")
        lines.append(f"    - Dimensions: {embedding_dim}")
    lines.append("")

    # ===== FILES READY =====
    lines.append("=" * 80)
    lines.append(" FILES READY")
    lines.append("=" * 80)
    lines.append("")

    files_to_check = {
        "Data Files": [
            ("final_scenarios.json", "Original classified scenarios"),
            ("final_scenarios_with_completeness.json", "Scenarios with completeness metrics"),
            ("final_scenarios_validated_complete.json", "Fully validated scenarios"),
            ("embedding_ready_scenarios.json", "Vector database ready scenarios")
        ],
        "Reports": [
            ("property_damage_expansion_report.txt", "Abbreviation expansion report"),
            ("property_damage_parse_report.txt", "Parsing report"),
            ("structuring_report.txt", "Classification report"),
            ("quality_validation_report.txt", "Quality validation report"),
            ("validation_summary_report.txt", "This summary report")
        ],
        "Reference Files": [
            ("Abbreviations_Event_type.xlsx", "Event type abbreviations"),
            ("Abbreviations_short_forms.xlsx", "General abbreviations"),
            ("property_damage_expanded.json", "Expanded scenarios"),
            ("property_damage_parsed.json", "Parsed scenarios")
        ]
    }

    for category, files in files_to_check.items():
        lines.append(f"{category}:")
        for filename, description in files:
            filepath = os.path.join(base_path, filename)
            exists, size = check_file_exists(filepath)
            status = "" if exists else ""
            size_str = format_size(size) if exists else "N/A"
            lines.append(f"  [{status}] {filename}")
            lines.append(f"      {description}")
            lines.append(f"      Size: {size_str}")
        lines.append("")

    # ===== QUALITY ASSURANCE METRICS =====
    lines.append("=" * 80)
    lines.append(" QUALITY ASSURANCE - KEY NUMBERS")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Dataset Size:")
    lines.append(f"  • Total Scenarios: {total}")
    lines.append(
        f"  • Approved: {status_counts.get('APPROVED', 0) + status_counts.get('APPROVED_WITH_WARNINGS', 0)} ({(status_counts.get('APPROVED', 0) + status_counts.get('APPROVED_WITH_WARNINGS', 0)) / total * 100:.1f}%)")
    lines.append(
        f"  • Review Needed: {status_counts.get('REVIEW_NEEDED', 0)} ({status_counts.get('REVIEW_NEEDED', 0) / total * 100:.1f}%)")
    lines.append(
        f"  • Rejected: {status_counts.get('REJECTED', 0)} ({status_counts.get('REJECTED', 0) / total * 100:.1f}%)")
    lines.append("")
    lines.append(f"Quality Metrics (Averages):")
    lines.append(f"  • Completeness Score: {avg_completeness:.2f} / 1.00")
    lines.append(f"  • Semantic Similarity: {avg_similarity:.3f} / 1.00")
    lines.append(f"  • Answer Relevancy: {avg_relevancy:.2f} / 1.00")
    lines.append(f"  • Context Precision: {avg_context_p:.2f} / 1.00")
    lines.append(f"  • Context Recall: {avg_context_r:.2f} / 1.00")
    lines.append("")
    lines.append(f"Pass Rates:")
    lines.append(f"  • Completeness: {completeness_pass}/{total} ({completeness_pass / total * 100:.1f}%)")
    lines.append(f"  • Semantic Similarity: {similarity_pass}/{total} ({similarity_pass / total * 100:.1f}%)")
    lines.append(f"  • Answer Relevancy: {relevancy_pass}/{total} ({relevancy_pass / total * 100:.1f}%)")
    lines.append("")

    # ===== DEPLOYMENT REQUIREMENTS =====
    lines.append("=" * 80)
    lines.append(" DEPLOYMENT REQUIREMENTS")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Embedding Model:")
    lines.append(f"  • Model: sentence-transformers/all-mpnet-base-v2")
    lines.append(f"  • Dimension: {embedding_dim if embedding_dim > 0 else 768}")
    lines.append(f"  • Normalization: True")
    lines.append("")
    lines.append(f"Chunking Strategy:")
    lines.append(f"  • Chunk Size: 512 tokens")
    lines.append(f"  • Chunk Overlap: 50 tokens")
    lines.append(f"  • Strategy: Sentence-based")
    lines.append("")
    lines.append(f"Vector Database:")
    lines.append(f"  • Type: ChromaDB (or compatible)")
    lines.append(f"  • Collection: emergency_scenarios")
    lines.append(f"  • Distance Metric: Cosine similarity")
    lines.append("")
    lines.append(f"Retrieval Settings:")
    lines.append(f"  • Top-K: 5")
    lines.append(f"  • Score Threshold: 0.7")
    lines.append("")
    lines.append(f"System Requirements:")
    lines.append(f"  • Python: 3.8+")
    lines.append(f"  • sentence-transformers: latest")
    lines.append(f"  • chromadb: latest")
    lines.append(
        f"  • Storage: ~{format_size(sum([check_file_exists(os.path.join(base_path, f))[1] for f, _ in files_to_check['Data Files']]))}")
    lines.append("")

    # ===== DEPLOYMENT READINESS =====
    lines.append("=" * 80)
    lines.append(" DEPLOYMENT READINESS ASSESSMENT")
    lines.append("=" * 80)
    lines.append("")

    # Determine readiness
    critical_pass = (
            completeness_pass >= total * 0.8 and
            similarity_pass >= total * 0.8 and
            relevancy_pass >= total * 0.8 and
            embedding_exists
    )

    if critical_pass and status_counts.get('REJECTED', 0) == 0:
        readiness = " READY FOR DEPLOYMENT"
        color = "GREEN"
    elif critical_pass:
        readiness = "  READY WITH CAUTION - Review rejected scenarios"
        color = "YELLOW"
    else:
        readiness = " NOT READY - Critical validations failed"
        color = "RED"

    lines.append(f"Status: {readiness}")
    lines.append(f"Level: {color}")
    lines.append("")
    lines.append("Checklist:")
    lines.append(f"  [{'' if total >= 10 else ''}] Minimum dataset size (≥10 scenarios)")
    lines.append(f"  [{'' if avg_completeness >= 0.8 else ''}] Average completeness ≥80%")
    lines.append(f"  [{'' if avg_similarity >= 0.7 else ''}] Average similarity ≥70%")
    lines.append(f"  [{'' if avg_relevancy >= 0.8 else ''}] Average relevancy ≥80%")
    lines.append(f"  [{'' if embedding_exists else ''}] Embeddings generated")
    lines.append(f"  [{'' if status_counts.get('REJECTED', 0) == 0 else ''}] No rejected scenarios")
    lines.append("")
    lines.append("=" * 80)

    # Save report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Print summary to console
    print("\n" + "\n".join(lines))
    print(f"\n Validation report saved to: {report_path}")

    return report_path


def generate_deployment_checklist(base_path):
    """Generate deployment checklist document"""

    checklist_path = os.path.join(base_path, "deployment_checklist.txt")

    lines = []
    lines.append("=" * 80)
    lines.append("SHIELD EMERGENCY RESPONSE SYSTEM")
    lines.append("DEPLOYMENT CHECKLIST")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("Use this checklist to ensure all steps are completed before deployment.")
    lines.append("")
    lines.append("=" * 80)
    lines.append("PRE-DEPLOYMENT CHECKLIST")
    lines.append("=" * 80)
    lines.append("")
    lines.append("[ ] 1. Data Validation")
    lines.append("    [ ] Run completeness check")
    lines.append("    [ ] Run quality validation")
    lines.append("    [ ] Review validation report")
    lines.append("    [ ] Address any rejected scenarios")
    lines.append("")
    lines.append("[ ] 2. Embedding Generation")
    lines.append("    [ ] Generate 768-dim embeddings")
    lines.append("    [ ] Verify embedding dimensions")
    lines.append("    [ ] Save embedding-ready scenarios")
    lines.append("")
    lines.append("[ ] 3. Vector Database Setup")
    lines.append("    [ ] Install ChromaDB")
    lines.append("    [ ] Create collection")
    lines.append("    [ ] Insert embeddings")
    lines.append("    [ ] Test similarity search")
    lines.append("")
    lines.append("[ ] 4. File Organization")
    lines.append("    [ ] Verify all data files present")
    lines.append("    [ ] Verify all reports generated")
    lines.append("    [ ] Backup original data")
    lines.append("    [ ] Archive intermediate files")
    lines.append("")
    lines.append("[ ] 5. Configuration")
    lines.append("    [ ] Set retrieval parameters (top-k, threshold)")
    lines.append("    [ ] Configure chunk size")
    lines.append("    [ ] Set up monitoring/logging")
    lines.append("")
    lines.append("[ ] 6. Testing")
    lines.append("    [ ] Test with sample queries")
    lines.append("    [ ] Verify retrieval accuracy")
    lines.append("    [ ] Check response times")
    lines.append("    [ ] Load testing")
    lines.append("")
    lines.append("[ ] 7. Documentation")
    lines.append("    [ ] API documentation")
    lines.append("    [ ] Usage examples")
    lines.append("    [ ] Troubleshooting guide")
    lines.append("")
    lines.append("[ ] 8. Deployment")
    lines.append("    [ ] Deploy to staging environment")
    lines.append("    [ ] Run integration tests")
    lines.append("    [ ] Deploy to production")
    lines.append("    [ ] Monitor initial performance")
    lines.append("")
    lines.append("=" * 80)
    lines.append("DEPLOYMENT SIGN-OFF")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Deployed by: _______________________  Date: ___________")
    lines.append("")
    lines.append("Reviewed by: _______________________  Date: ___________")
    lines.append("")
    lines.append("=" * 80)

    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f" Deployment checklist saved to: {checklist_path}")

    return checklist_path


if __name__ == "__main__":
    # Base path
    base_path = "/Users/riteshchandra/PycharmProjects/SHIELD"

    # Input files
    validated_json = os.path.join(base_path, "final_scenarios_validated.json")
    embedding_json = os.path.join(base_path, "embedding_ready_scenarios.json")

    # Generate reports
    print("\n Generating validation report...")
    report = generate_validation_report(base_path, validated_json, embedding_json)

    print("\n Generating deployment checklist...")
    checklist = generate_deployment_checklist(base_path)

    print("\n" + "=" * 70)
    print(" ALL REPORTS GENERATED")
    print("=" * 70)
    print(f" Validation Report: {report}")
    print(f" Deployment Checklist: {checklist}")
    print("=" * 70 + "\n")
