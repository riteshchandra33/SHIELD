import json
from datetime import datetime


def assign_final_validation_status(input_json, output_json, report_path):
    """
    Assign final validation status based on ALL metrics:
    - CRITICAL: completeness, similarity, answer_relevancy
    - RECOMMENDED: bertscore, faithfulness, context_precision, context_recall

    Status:
    - APPROVED: All critical passed + most recommended passed
    - REVIEW_NEEDED: Critical passed but some recommended failed
    - REJECTED: Any critical metric failed
    """

    with open(input_json, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"Assigning final validation status for {len(scenarios)} scenarios...\n")

    approved = 0
    review_needed = 0
    rejected = 0

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("FINAL VALIDATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("CRITICAL METRICS (Must Pass):")
    report_lines.append("  - Completeness Score ≥ 0.80")
    report_lines.append("  - Semantic Similarity ≥ 0.70")
    report_lines.append("  - Answer Relevancy ≥ 0.80")
    report_lines.append("")
    report_lines.append("RECOMMENDED METRICS:")
    report_lines.append("  - BERTScore ≥ 0.70")
    report_lines.append("  - Faithfulness ≥ 0.70")
    report_lines.append("  - Context Precision ≥ 0.80")
    report_lines.append("  - Context Recall ≥ 0.80")
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("")

    for scenario in scenarios:
        scenario_id = scenario.get("scenario_id", "Unknown")

        # Get CRITICAL metrics
        completeness = scenario.get("completeness_score", 0)
        semantic_sim = scenario.get("semantic_similarity_score", 0)
        answer_relevancy = scenario.get("answer_relevancy_score", 0)

        # Get RECOMMENDED metrics
        bertscore = scenario.get("bertscore", 0)
        faithfulness = scenario.get("faithfulness_score", 0)
        context_precision = scenario.get("context_precision", 0)
        context_recall = scenario.get("context_recall", 0)

        # Check CRITICAL metrics
        critical_pass = (
                completeness >= 0.80 and
                semantic_sim >= 0.70 and
                answer_relevancy >= 0.80
        )

        # Check RECOMMENDED metrics
        recommended_pass_count = sum([
            bertscore >= 0.70,
            faithfulness >= 0.70,
            context_precision >= 0.80,
            context_recall >= 0.80
        ])

        # Determine final status
        if not critical_pass:
            status = "REJECTED"
            rejected += 1
            icon = ""
        elif critical_pass and recommended_pass_count >= 3:
            status = "APPROVED"
            approved += 1
            icon = ""
        else:
            status = "REVIEW_NEEDED"
            review_needed += 1
            icon = ""

        # Add status to scenario
        scenario["validation_status"] = status
        scenario["critical_metrics_passed"] = critical_pass
        scenario["recommended_metrics_passed"] = recommended_pass_count
        scenario["validation_timestamp"] = datetime.now().isoformat()

        # Add to report
        report_lines.append(f"{icon} Scenario: {scenario_id}")
        report_lines.append(f"   Status: {status}")
        report_lines.append(f"   CRITICAL METRICS:")
        report_lines.append(f"     - Completeness: {completeness:.2f} {'' if completeness >= 0.80 else ''}")
        report_lines.append(f"     - Semantic Similarity: {semantic_sim:.2f} {'' if semantic_sim >= 0.70 else ''}")
        report_lines.append(
            f"     - Answer Relevancy: {answer_relevancy:.2f} {'' if answer_relevancy >= 0.80 else ''}")
        report_lines.append(f"   RECOMMENDED METRICS:")
        report_lines.append(f"     - BERTScore: {bertscore:.2f} {'' if bertscore >= 0.70 else ''}")
        report_lines.append(f"     - Faithfulness: {faithfulness:.2f} {'' if faithfulness >= 0.70 else ''}")
        report_lines.append(
            f"     - Context Precision: {context_precision:.2f} {'' if context_precision >= 0.80 else ''}")
        report_lines.append(f"     - Context Recall: {context_recall:.2f} {'' if context_recall >= 0.80 else ''}")

        if status != "APPROVED":
            missing = scenario.get("missing_fields", [])
            if missing:
                report_lines.append(f"   Missing Fields: {', '.join(missing)}")

            failed_questions = [q for q, ans in scenario.get("key_questions_results", {}).items() if not ans]
            if failed_questions:
                report_lines.append(f"   Unanswered Questions: {len(failed_questions)}")

        report_lines.append("")

    # Save validated scenarios
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)

    # Add summary to report
    report_lines.append("=" * 80)
    report_lines.append("VALIDATION SUMMARY")
    report_lines.append("=" * 80)
    report_lines.append(f"Total Scenarios: {len(scenarios)}")
    report_lines.append(f"Approved: {approved} ({approved / len(scenarios) * 100:.1f}%)")
    report_lines.append(f"Review Needed: {review_needed} ({review_needed / len(scenarios) * 100:.1f}%)")
    report_lines.append(f"Rejected: {rejected} ({rejected / len(scenarios) * 100:.1f}%)")
    report_lines.append("")

    # Determine overall status
    if rejected > 0:
        overall = "  CRITICAL FAILURES DETECTED - MANUAL REVIEW REQUIRED"
    elif review_needed > 0:
        overall = "  REVIEW NEEDED - Some scenarios require attention"
    else:
        overall = " ALL SCENARIOS APPROVED - READY FOR DEPLOYMENT"

    report_lines.append(f"Overall Status: {overall}")
    report_lines.append("=" * 80)

    # Save report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # Print summary
    print("\n" + "\n".join(report_lines[-12:]))
    print(f"\nValidated scenarios saved to: {output_json}")
    print(f"Final validation report saved to: {report_path}\n")


if __name__ == "__main__":
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_with_quality.json"
    output_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_validated.json"
    report_path = "/Users/riteshchandra/PycharmProjects/SHIELD/final_validation_report.txt"

    assign_final_validation_status(input_json, output_json, report_path)
