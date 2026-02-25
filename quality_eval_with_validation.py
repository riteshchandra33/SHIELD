"""
UPDATED QUALITY EVALUATION WITH ONTOLOGY VALIDATION
Evaluates the integrated RAG-LLM system with built-in validation.
"""

import json
import time
from datetime import datetime
from typing import Dict, List
from integrated_rag_validated import IntegratedRAGLLM


# ============================================================================
# UPDATED QUALITY EVALUATOR
# ============================================================================

class UpdatedQualityEvaluator:
    """Quality evaluator using the integrated validation system."""

    def __init__(self, db_path: str = "./chroma_db", protocol_path: str = "./"):
        """Initialize evaluator with integrated RAG-LLM system."""
        print("\n" + "=" * 70)
        print("INITIALIZING UPDATED QUALITY EVALUATOR")
        print("=" * 70)

        self.rag_system = IntegratedRAGLLM(
            db_path=db_path,
            protocol_path=protocol_path
        )

        self.test_results = []

        print("=" * 70)
        print(" Evaluator ready with integrated validation")
        print("=" * 70 + "\n")

    def define_test_cases(self) -> List[Dict]:
        """Define comprehensive test cases."""
        return [
            # EXPLAIN MODE - Good cases
            {
                "name": "EXPLAIN: Information gathering",
                "query": "What questions should I ask the caller about the accident?",
                "mode": "explain",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },
            {
                "name": "EXPLAIN: No-injury protocol",
                "query": "How do I handle an accident with no injuries?",
                "mode": "explain",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },
            {
                "name": "EXPLAIN: Traffic blocking",
                "query": "What is the protocol for accidents blocking traffic?",
                "mode": "explain",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },

            # VARIANT MODE
            {
                "name": "VARIANT: Generate scenario",
                "query": "Create a variant vehicle accident scenario",
                "mode": "variant",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },
            {
                "name": "VARIANT: Different vehicles",
                "query": "Generate a similar accident with different vehicles",
                "mode": "variant",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },

            # QUESTION MODE
            {
                "name": "QUESTION: Protocol quiz",
                "query": "Generate quiz questions on dispatcher protocols",
                "mode": "question",
                "category": "vehicle_accident",
                "expected_result": "PASS"
            },

            # EDGE CASES
            {
                "name": "EDGE: Very short query",
                "query": "accident",
                "mode": "explain",
                "category": "vehicle_accident",
                "expected_result": "REVIEW"
            },
            {
                "name": "EDGE: Vague question",
                "query": "what do I do",
                "mode": "explain",
                "category": "vehicle_accident",
                "expected_result": "REVIEW"
            }
        ]

    def run_evaluation(self) -> List[Dict]:
        """Run comprehensive evaluation with validation."""
        print("\n" + "" + "" * 68 + "")
        print("" + " " * 20 + "RUNNING EVALUATION" + " " * 29 + "")
        print("" + "" * 68 + "\n")

        test_cases = self.define_test_cases()
        print(f" Total test cases: {len(test_cases)}\n")

        results = []

        for idx, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"TEST {idx}/{len(test_cases)}: {test_case['name']}")
            print(f"{'='*70}")
            print(f"Query: '{test_case['query']}'")
            print(f"Mode: {test_case['mode']}")
            print(f"Expected: {test_case['expected_result']}")
            print("-" * 70)

            try:
                # Query the system (with validation enabled)
                response = self.rag_system.query(
                    user_query=test_case["query"],
                    mode=test_case["mode"],
                    top_k=3,
                    validate=True,
                    category=test_case["category"]
                )

                # Extract validation results
                validation = response.get("validation", {})

                result = {
                    "test_id": idx,
                    "name": test_case["name"],
                    "query": test_case["query"],
                    "mode": test_case["mode"],
                    "category": test_case["category"],
                    "expected_result": test_case["expected_result"],
                    "retrieved_count": len(response["retrieved_scenarios"]),
                    "generated_length": len(response["generated_content"]),
                    "time_taken": response["metadata"]["total_time"],
                    "validation_status": validation.get("status", "N/A"),
                    "validation_valid": validation.get("valid", False),
                    "validation_confidence": validation.get("confidence", 0.0),
                    "validation_issues": validation.get("issues", []),
                    "validation_corrections": validation.get("corrections", []),
                    "validation_details": validation.get("details", {}),
                    "generated_content": response["generated_content"],
                    "retrieved_scenarios": response["retrieved_scenarios"],
                    "error": None
                }

                # Check if result matches expectation
                result["matches_expectation"] = (
                    result["validation_status"] == test_case["expected_result"]
                )

                # Print summary
                print(f"\n{''*70}")
                print("RESULT SUMMARY")
                print(f"{''*70}")
                print(f" Time: {result['time_taken']}s")
                print(f" Retrieved: {result['retrieved_count']} scenarios")
                print(f" Generated: {result['generated_length']} chars")
                print(f"\n VALIDATION:")
                print(f"   Status: {result['validation_status']}")
                print(f"   Valid: {result['validation_valid']}")
                print(f"   Confidence: {result['validation_confidence']:.2f}")
                print(f"   Issues: {len(result['validation_issues'])}")
                print(f"   Corrections: {len(result['validation_corrections'])}")
                print(f"\n Expected: {test_case['expected_result']} | " +
                      f"Got: {result['validation_status']} | " +
                      f"Match: {'' if result['matches_expectation'] else ''}")
                print(f"{''*70}")

            except Exception as e:
                print(f"\n ERROR: {str(e)}")
                result = {
                    "test_id": idx,
                    "name": test_case["name"],
                    "query": test_case["query"],
                    "mode": test_case["mode"],
                    "error": str(e),
                    "validation_status": "ERROR",
                    "matches_expectation": False
                }

            results.append(result)

        self.test_results = results

        print(f"\n\n{'='*70}")
        print(f" EVALUATION COMPLETE - {len(results)} tests executed")
        print(f"{'='*70}\n")

        return results

    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive metrics."""
        if not self.test_results:
            return {}

        valid_results = [r for r in self.test_results if not r.get("error")]
        total_tests = len(self.test_results)

        # Validation status distribution
        pass_count = sum(1 for r in valid_results if r.get("validation_status") == "PASS")
        review_count = sum(1 for r in valid_results if r.get("validation_status") == "REVIEW")
        fail_count = sum(1 for r in valid_results if r.get("validation_status") == "FAIL")

        # Expectation matching
        match_count = sum(1 for r in valid_results if r.get("matches_expectation", False))

        # Confidence metrics
        confidences = [r.get("validation_confidence", 0) for r in valid_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Issue metrics
        total_issues = sum(len(r.get("validation_issues", [])) for r in valid_results)
        avg_issues_per_test = total_issues / len(valid_results) if valid_results else 0

        # Protocol coverage (from validation details)
        coverages = []
        for r in valid_results:
            protocol_check = r.get("validation_details", {}).get("protocol_check", {})
            coverage = protocol_check.get("coverage_score", 0)
            if coverage > 0:
                coverages.append(coverage)
        avg_coverage = sum(coverages) / len(coverages) if coverages else 0

        # Safety violations
        safety_violations = sum(
            1 for r in valid_results 
            if not r.get("validation_details", {}).get("unsafe_check", {}).get("is_safe", True)
        )

        # Hallucinations
        total_hallucinations = sum(
            r.get("validation_details", {}).get("hallucination_check", {}).get("hallucination_count", 0)
            for r in valid_results
        )

        # Performance
        times = [r.get("time_taken", 0) for r in valid_results if r.get("time_taken")]
        avg_time = sum(times) / len(times) if times else 0

        metrics = {
            "total_tests": total_tests,
            "successful_tests": len(valid_results),
            "failed_tests": total_tests - len(valid_results),
            "validation_distribution": {
                "pass": pass_count,
                "review": review_count,
                "fail": fail_count
            },
            "pass_rate": round((pass_count / len(valid_results)) * 100, 1) if valid_results else 0,
            "expectation_match_rate": round((match_count / len(valid_results)) * 100, 1) if valid_results else 0,
            "avg_confidence": round(avg_confidence, 3),
            "avg_protocol_coverage": round(avg_coverage * 100, 1),
            "total_issues": total_issues,
            "avg_issues_per_test": round(avg_issues_per_test, 2),
            "safety_violations": safety_violations,
            "total_hallucinations": total_hallucinations,
            "avg_time": round(avg_time, 2),
            "overall_score": 0  # Will calculate below
        }

        # Calculate overall score
        # Pass rate (40%) + Confidence (30%) + Coverage (20%) + Match rate (10%)
        overall = (
            (metrics["pass_rate"] / 100) * 40 +
            metrics["avg_confidence"] * 30 +
            (metrics["avg_protocol_coverage"] / 100) * 20 +
            (metrics["expectation_match_rate"] / 100) * 10
        )
        metrics["overall_score"] = round(overall, 1)

        # Recommendation
        if metrics["overall_score"] >= 80 and metrics["safety_violations"] == 0:
            metrics["recommendation"] = "READY FOR DEPLOYMENT"
        elif metrics["overall_score"] >= 60 and metrics["safety_violations"] == 0:
            metrics["recommendation"] = "NEEDS MINOR IMPROVEMENTS"
        else:
            metrics["recommendation"] = "REQUIRES SIGNIFICANT IMPROVEMENTS"

        return metrics

    def generate_report(self, output_file: str = "validation_evaluation_report.txt") -> None:
        """Generate comprehensive evaluation report."""
        print(f"\n Generating evaluation report...")

        if not self.test_results:
            print("  No test results available")
            return

        metrics = self.calculate_metrics()

        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("ONTOLOGY VALIDATION - QUALITY EVALUATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Tests: {metrics['total_tests']}")
        lines.append(f"Overall Score: {metrics['overall_score']}/100")
        lines.append(f"Recommendation: {metrics['recommendation']}")
        lines.append("=" * 80)
        lines.append("")

        # Metrics Summary
        lines.append("" + "" * 78 + "")
        lines.append("" + " " * 30 + "METRICS SUMMARY" + " " * 33 + "")
        lines.append("" + "" * 78 + "")
        lines.append("")

        lines.append("1. VALIDATION STATUS DISTRIBUTION")
        lines.append("-" * 80)
        lines.append(f"    PASS: {metrics['validation_distribution']['pass']} " +
                    f"({metrics['pass_rate']}%)")
        lines.append(f"     REVIEW: {metrics['validation_distribution']['review']}")
        lines.append(f"    FAIL: {metrics['validation_distribution']['fail']}")
        lines.append("")

        lines.append("2. QUALITY METRICS")
        lines.append("-" * 80)
        lines.append(f"   Average Confidence: {metrics['avg_confidence']:.3f}")
        lines.append(f"   Average Protocol Coverage: {metrics['avg_protocol_coverage']}%")
        lines.append(f"   Expectation Match Rate: {metrics['expectation_match_rate']}%")
        lines.append(f"   Average Time: {metrics['avg_time']}s")
        lines.append("")

        lines.append("3. SAFETY & COMPLIANCE")
        lines.append("-" * 80)
        lines.append(f"   Safety Violations: {metrics['safety_violations']} " +
                    f"{' CRITICAL' if metrics['safety_violations'] > 0 else ' NONE'}")
        lines.append(f"   Total Hallucinations: {metrics['total_hallucinations']}")
        lines.append(f"   Total Issues: {metrics['total_issues']}")
        lines.append(f"   Avg Issues per Test: {metrics['avg_issues_per_test']}")
        lines.append("")

        lines.append("4. OVERALL ASSESSMENT")
        lines.append("-" * 80)
        lines.append(f"   Overall Score: {metrics['overall_score']}/100")
        lines.append(f"   Recommendation: {metrics['recommendation']}")
        lines.append("")
        lines.append("")

        # Detailed Results
        lines.append("=" * 80)
        lines.append("DETAILED TEST RESULTS")
        lines.append("=" * 80)
        lines.append("")

        for result in self.test_results:
            lines.append(f"\n{'#' * 80}")
            lines.append(f"TEST #{result['test_id']}: {result['name']}")
            lines.append(f"{'#' * 80}")
            lines.append(f"Query: {result['query']}")
            lines.append(f"Mode: {result['mode']}")
            lines.append(f"Category: {result.get('category', 'N/A')}")
            lines.append("")

            if result.get("error"):
                lines.append(f" ERROR: {result['error']}")
                lines.append("")
                continue

            lines.append("-" * 80)
            lines.append("VALIDATION RESULTS")
            lines.append("-" * 80)
            lines.append(f"Status: {result.get('validation_status', 'N/A')}")
            lines.append(f"Valid: {result.get('validation_valid', False)}")
            lines.append(f"Confidence: {result.get('validation_confidence', 0):.3f}")
            lines.append(f"Expected: {result.get('expected_result', 'N/A')}")
            lines.append(f"Matches Expectation: {' YES' if result.get('matches_expectation') else ' NO'}")
            lines.append("")

            # Issues
            issues = result.get("validation_issues", [])
            if issues:
                lines.append(f"ISSUES ({len(issues)}):")
                for i, issue in enumerate(issues, 1):
                    lines.append(f"   {i}. {issue}")
                lines.append("")

            # Corrections
            corrections = result.get("validation_corrections", [])
            if corrections:
                lines.append(f"CORRECTIONS ({len(corrections)}):")
                for i, corr in enumerate(corrections, 1):
                    lines.append(f"   {i}. {corr}")
                lines.append("")

            # Validation details
            details = result.get("validation_details", {})
            if details:
                lines.append("VALIDATION DETAILS:")

                # Unsafe check
                unsafe = details.get("unsafe_check", {})
                lines.append(f"   Unsafe Content: {' SAFE' if unsafe.get('is_safe', True) else ' VIOLATIONS'}")
                if unsafe.get("violations"):
                    for v in unsafe["violations"]:
                        lines.append(f"      - {v}")

                # Protocol check
                protocol = details.get("protocol_check", {})
                if protocol:
                    lines.append(f"   Protocol Coverage: {protocol.get('coverage_score', 0):.1%}")
                    if protocol.get("missing_categories"):
                        lines.append(f"      Missing: {', '.join(protocol['missing_categories'])}")

                # Hallucination check
                halluc = details.get("hallucination_check", {})
                if halluc:
                    lines.append(f"   Hallucinations: {halluc.get('hallucination_count', 0)}")
                    if halluc.get("hallucinations"):
                        for h in halluc["hallucinations"]:
                            lines.append(f"      - {h}")

                lines.append("")

            lines.append("-" * 80)
            lines.append("GENERATED CONTENT:")
            lines.append("-" * 80)
            lines.append(result.get("generated_content", "N/A")[:500] + "...")
            lines.append("")
            lines.append("_" * 80)
            lines.append("")

        # Footer
        lines.append("\n" + "=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        # Write report
        report_content = "\n".join(lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # Save JSON
        json_output = {
            "metrics": metrics,
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        json_file = output_file.replace(".txt", ".json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)

        print(f" Report saved to: {output_file}")
        print(f" JSON data saved to: {json_file}")

        # Print key metrics
        print(f"\n KEY METRICS:")
        print(f"   Overall Score: {metrics['overall_score']}/100")
        print(f"   Pass Rate: {metrics['pass_rate']}%")
        print(f"   Avg Confidence: {metrics['avg_confidence']:.3f}")
        print(f"   Protocol Coverage: {metrics['avg_protocol_coverage']}%")
        print(f"   Safety Violations: {metrics['safety_violations']}")
        print(f"   Recommendation: {metrics['recommendation']}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run evaluation with integrated validation."""
    print("\n" + "" + "" * 68 + "")
    print("" + " " * 10 + "QUALITY EVALUATION WITH ONTOLOGY VALIDATION" + " " * 14 + "")
    print("" + "" * 68 + "\n")

    evaluator = UpdatedQualityEvaluator(
        db_path="./chroma_db",
        protocol_path="./"
    )

    # Run evaluation
    results = evaluator.run_evaluation()

    # Calculate metrics
    metrics = evaluator.calculate_metrics()

    # Print summary
    print("\n" + "" + "" * 68 + "")
    print("" + " " * 25 + "SUMMARY" + " " * 36 + "")
    print("" + "" * 68 + "\n")
    print(f" Overall Score: {metrics['overall_score']}/100")
    print(f" Pass Rate: {metrics['pass_rate']}%")
    print(f" Avg Confidence: {metrics['avg_confidence']:.3f}")
    print(f" Protocol Coverage: {metrics['avg_protocol_coverage']}%")
    print(f"  Safety Violations: {metrics['safety_violations']}")
    print(f" Total Hallucinations: {metrics['total_hallucinations']}")
    print(f"\n Recommendation: {metrics['recommendation']}")

    # Generate report
    evaluator.generate_report("validation_evaluation_report.txt")

    print("\n" + "" + "" * 68 + "")
    print("" + " " * 22 + "EVALUATION COMPLETE!" + " " * 24 + "")
    print("" + "" * 68 + "\n")


if __name__ == "__main__":
    main()
