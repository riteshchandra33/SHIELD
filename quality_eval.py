"""
SHIELD RAG-LLM Quality Metrics Evaluation - ENHANCED VERSION

Includes:
- Performance metrics (generation time, retrieval similarity)
- Automated format validation
- Comprehensive metrics tracking
- Overall system recommendations
"""

import json
import time
import re
from datetime import datetime
from typing import Dict, List, Tuple
from integrated_rag import IntegratedRAGLLM


# ============================================================================
# AUTOMATED VALIDATORS
# ============================================================================

class AutomatedValidator:
    """Automated validation checks for format compliance."""

    @staticmethod
    def validate_explain_format(content: str) -> Dict[str, bool]:
        """Validate EXPLAIN mode format."""
        checks = {
            "has_sections": False,
            "has_classification_section": False,
            "has_information_section": False,
            "has_protocol_section": False,
            "sufficient_length": False
        }

        content_lower = content.lower()

        # Check for numbered sections or headers
        checks["has_sections"] = bool(re.search(r'\d\.|\n##|\*\*', content))

        # Check for key sections
        checks["has_classification_section"] = any(word in content_lower for word in
                                                   ["classification", "classify", "type of accident", "severity"])
        checks["has_information_section"] = any(word in content_lower for word in
                                                ["information", "gather", "ask caller", "questions"])
        checks["has_protocol_section"] = any(word in content_lower for word in
                                             ["protocol", "procedure", "dispatch", "notify"])

        # Length check (should be comprehensive
        checks["sufficient_length"] = len(content) >= 200

        return checks

    @staticmethod
    def validate_variant_format(content: str) -> Dict[str, bool]:
        """Validate VARIANT mode format."""
        checks = {
            "uses_double_slash": False,
            "has_vehicle_count": False,
            "has_injury_status": False,
            "has_location": False,
            "has_caller": False,
            "has_phone_10digit": False,
            "has_virginia_area_code": False
        }

        # Check for // separator
        checks["uses_double_slash"] = "//" in content

        # Check for vehicle count
        checks["has_vehicle_count"] = bool(re.search(r'\d+\s*vehicle', content.lower()))

        # Check for injury status
        injury_terms = ["no injuries", "injuries reported", "minor injuries",
                        "serious injuries", "possible injuries"]
        checks["has_injury_status"] = any(term in content.lower() for term in injury_terms)

        # Check for location indicators
        location_terms = ["route", "i-", "highway", "pike", "road", "street", "blocking"]
        checks["has_location"] = any(term in content.lower() for term in location_terms)

        # Check for caller info
        checks["has_caller"] = "caller:" in content.lower()

        # Check for 10-digit phone
        phone_pattern = r'\d{3}-\d{3}-\d{4}'
        phone_match = re.search(phone_pattern, content)
        checks["has_phone_10digit"] = bool(phone_match)

        # Check for Virginia area codes
        if phone_match:
            area_code = phone_match.group(0)[:3]
            checks["has_virginia_area_code"] = area_code in ["703", "571", "540", "202", "301"]

        return checks

    @staticmethod
    def validate_question_format(content: str) -> Dict[str, bool]:
        """Validate QUESTION mode format."""
        checks = {
            "has_q1": False,
            "has_q2": False,
            "has_q3": False,
            "has_all_options": False,
            "has_answers": False,
            "has_explanations": False,
            "proper_structure": False
        }

        # Check for questions
        checks["has_q1"] = "Q1:" in content or "q1:" in content.lower()
        checks["has_q2"] = "Q2:" in content or "q2:" in content.lower()
        checks["has_q3"] = "Q3:" in content or "q3:" in content.lower()

        # Check for all options (A, B, C, D)
        a_count = content.count("A)")
        b_count = content.count("B)")
        c_count = content.count("C)")
        d_count = content.count("D)")
        checks["has_all_options"] = (a_count >= 3 and b_count >= 3 and
                                     c_count >= 3 and d_count >= 3)

        # Check for answer markers
        checks["has_answers"] = content.count("Answer:") >= 3

        # Check for explanations
        checks["has_explanations"] = content.count("Explanation:") >= 3

        # Proper structure check
        checks["proper_structure"] = (checks["has_q1"] and checks["has_q2"] and
                                      checks["has_q3"] and checks["has_answers"])

        return checks

    @staticmethod
    def calculate_format_score(checks: Dict[str, bool]) -> float:
        """Calculate format compliance score as percentage."""
        total_checks = len(checks)
        passed_checks = sum(checks.values())
        return (passed_checks / total_checks) * 100 if total_checks > 0 else 0


# ============================================================================
# ENHANCED QUALITY EVALUATOR
# ============================================================================

class QualityEvaluator:
    """Enhanced quality evaluator with comprehensive metrics."""

    def __init__(self, db_path: str = "./chroma_db"):
        """Initialize quality evaluator."""
        print("\n" + "=" * 70)
        print("ENHANCED QUALITY METRICS EVALUATION - INITIALIZING")
        print("=" * 70)

        self.rag_llm = IntegratedRAGLLM(db_path=db_path)
        self.validator = AutomatedValidator()
        self.test_results = []

        # Performance thresholds
        self.TARGET_TIME = 5.0  # seconds
        self.TARGET_SIMILARITY_TOP1 = 70.0  # percent
        self.TARGET_SIMILARITY_TOP3 = 60.0  # percent

        print("=" * 70)
        print(" Evaluator ready with automated validation")
        print(f"⏱  Target generation time: <{self.TARGET_TIME}s")
        print(f" Target similarity: Top-1 >{self.TARGET_SIMILARITY_TOP1}%, Top-3 >{self.TARGET_SIMILARITY_TOP3}%")
        print("=" * 70 + "\n")

    def define_test_queries(self) -> List[Dict]:
        """Define 10 test queries."""
        test_queries = [
            # EXPLAIN MODE (3)
            {
                "query": "What questions should I ask the caller?",
                "mode": "explain",
                "category": "explain_mode",
                "description": "Information gathering protocol"
            },
            {
                "query": "How should I handle an accident with no injuries?",
                "mode": "explain",
                "category": "explain_mode",
                "description": "No-injury accident protocol"
            },
            {
                "query": "What is the protocol for accidents blocking traffic?",
                "mode": "explain",
                "category": "explain_mode",
                "description": "Traffic blockage protocol"
            },

            # VARIANT MODE (3)
            {
                "query": "Create a variant of this accident scenario",
                "mode": "variant",
                "category": "variant_mode",
                "description": "Generic variant request"
            },
            {
                "query": "Generate a similar accident scenario with different vehicles",
                "mode": "variant",
                "category": "variant_mode",
                "description": "Vehicle variation focus"
            },
            {
                "query": "Make a different vehicle accident scenario",
                "mode": "variant",
                "category": "variant_mode",
                "description": "General variation request"
            },

            # QUESTION MODE (2)
            {
                "query": "Generate quiz questions on dispatcher protocols",
                "mode": "question",
                "category": "question_mode",
                "description": "Protocol-focused quiz"
            },
            {
                "query": "Create test questions for this accident scenario",
                "mode": "question",
                "category": "question_mode",
                "description": "Scenario-based quiz"
            },

            # EDGE CASES (2)
            {
                "query": "accident",
                "mode": "explain",
                "category": "edge_case",
                "description": "Very short query (1 word)"
            },
            {
                "query": "what do I do",
                "mode": "explain",
                "category": "edge_case",
                "description": "Ambiguous/vague question"
            }
        ]

        return test_queries

    def run_evaluation(self) -> List[Dict]:
        """Run all test queries and collect results with validation."""
        print("\n" + "" + "" * 68 + "")
        print("" + " " * 20 + "RUNNING EVALUATION" + " " * 29 + "")
        print("" + "" * 68 + "\n")

        test_queries = self.define_test_queries()

        print(f" Total test queries: {len(test_queries)}")
        print(f"   • EXPLAIN mode: {sum(1 for q in test_queries if q['category'] == 'explain_mode')}")
        print(f"   • VARIANT mode: {sum(1 for q in test_queries if q['category'] == 'variant_mode')}")
        print(f"   • QUESTION mode: {sum(1 for q in test_queries if q['category'] == 'question_mode')}")
        print(f"   • EDGE CASES: {sum(1 for q in test_queries if q['category'] == 'edge_case')}")
        print()

        results = []

        for idx, test_case in enumerate(test_queries, 1):
            print(f"\n{'=' * 70}")
            print(f"TEST {idx}/{len(test_queries)}: {test_case['description']}")
            print(f"{'=' * 70}")
            print(f"Query: '{test_case['query']}'")
            print(f"Mode: {test_case['mode']}")
            print(f"Category: {test_case['category']}")
            print("-" * 70)

            # Run query
            start_time = time.time()
            try:
                response = self.rag_llm.query(
                    user_query=test_case["query"],
                    mode=test_case["mode"],
                    top_k=3
                )
                elapsed_time = time.time() - start_time
                error = None

            except Exception as e:
                response = None
                elapsed_time = time.time() - start_time
                error = str(e)
                print(f" ERROR: {error}")

            # Initialize result
            result = {
                "test_id": idx,
                "query": test_case["query"],
                "mode": test_case["mode"],
                "category": test_case["category"],
                "description": test_case["description"],
                "time_taken": round(elapsed_time, 2),
                "error": error,
                "retrieved_scenarios": None,
                "generated_content": None,
                "metadata": None,
                "validation": {
                    "format_checks": {},
                    "format_score": 0,
                    "format_errors": [],
                    "performance_checks": {}
                }
            }

            if response:
                result["retrieved_scenarios"] = response["retrieved_scenarios"]
                result["generated_content"] = response["generated_content"]
                result["metadata"] = response["metadata"]

                # Automated format validation
                format_checks = self._validate_format(
                    content=response["generated_content"],
                    mode=test_case["mode"]
                )
                format_score = self.validator.calculate_format_score(format_checks)
                format_errors = [key for key, val in format_checks.items() if not val]

                result["validation"]["format_checks"] = format_checks
                result["validation"]["format_score"] = round(format_score, 1)
                result["validation"]["format_errors"] = format_errors

                # Performance checks
                perf_checks = self._check_performance(
                    time_taken=elapsed_time,
                    scenarios=response["retrieved_scenarios"]
                )
                result["validation"]["performance_checks"] = perf_checks

                # Print validation summary
                print(f"\n Query completed in {elapsed_time:.2f}s")
                print(f" Retrieved {len(response['retrieved_scenarios'])} scenarios")
                print(f" Generated {len(response['generated_content'])} characters")
                print(f" Format Score: {format_score:.0f}%")

                if format_errors:
                    print(f"  Format Issues: {', '.join(format_errors)}")

                if not perf_checks["time_acceptable"]:
                    print(f"  Slow generation: {elapsed_time:.2f}s (target: <{self.TARGET_TIME}s)")

                if not perf_checks["top1_similarity_acceptable"]:
                    top1_sim = response["retrieved_scenarios"][0]["similarity"]
                    print(f"  Low similarity: {top1_sim:.1f}% (target: >{self.TARGET_SIMILARITY_TOP1}%)")

            results.append(result)

        self.test_results = results

        print(f"\n\n{'=' * 70}")
        print(f" EVALUATION COMPLETE - {len(results)} tests executed")
        print(f"{'=' * 70}\n")

        return results

    def _validate_format(self, content: str, mode: str) -> Dict[str, bool]:
        """Validate format based on mode."""
        if mode == "explain":
            return self.validator.validate_explain_format(content)
        elif mode == "variant":
            return self.validator.validate_variant_format(content)
        elif mode == "question":
            return self.validator.validate_question_format(content)
        return {}

    def _check_performance(self, time_taken: float, scenarios: List[Dict]) -> Dict:
        """Check performance metrics."""
        top1_sim = scenarios[0]["similarity"] if scenarios else 0
        avg_top3_sim = sum(s["similarity"] for s in scenarios[:3]) / min(3, len(scenarios)) if scenarios else 0

        return {
            "time_taken": time_taken,
            "time_acceptable": time_taken < self.TARGET_TIME,
            "top1_similarity": round(top1_sim, 1),
            "top1_similarity_acceptable": top1_sim >= self.TARGET_SIMILARITY_TOP1,
            "avg_top3_similarity": round(avg_top3_sim, 1),
            "avg_top3_similarity_acceptable": avg_top3_sim >= self.TARGET_SIMILARITY_TOP3
        }

    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive metrics across all tests."""
        if not self.test_results:
            return {}

        # Filter out errors
        valid_results = [r for r in self.test_results if not r["error"]]
        total_tests = len(self.test_results)

        metrics = {
            # Success metrics
            "total_tests": total_tests,
            "successful_tests": len(valid_results),
            "failed_tests": total_tests - len(valid_results),
            "success_rate": round((len(valid_results) / total_tests) * 100, 1),

            # Performance metrics
            "avg_generation_time": 0,
            "min_generation_time": 0,
            "max_generation_time": 0,
            "time_threshold_violations": 0,

            # Similarity metrics
            "avg_top1_similarity": 0,
            "avg_top3_similarity": 0,
            "low_similarity_count": 0,

            # Format metrics
            "avg_format_score": 0,
            "format_error_count": 0,
            "perfect_format_count": 0,

            # Manual review placeholders
            "hallucination_count": 0,  # To be filled manually
            "contradiction_count": 0,  # To be filled manually
            "safety_issue_count": 0,  # To be filled manually

            # Overall
            "overall_quality_score": 0,
            "recommendation": ""
        }

        if valid_results:
            # Performance
            times = [r["time_taken"] for r in valid_results]
            metrics["avg_generation_time"] = round(sum(times) / len(times), 2)
            metrics["min_generation_time"] = round(min(times), 2)
            metrics["max_generation_time"] = round(max(times), 2)
            metrics["time_threshold_violations"] = sum(
                1 for r in valid_results
                if not r["validation"]["performance_checks"].get("time_acceptable", False)
            )

            # Similarity
            top1_sims = [r["validation"]["performance_checks"]["top1_similarity"]
                         for r in valid_results]
            top3_sims = [r["validation"]["performance_checks"]["avg_top3_similarity"]
                         for r in valid_results]

            metrics["avg_top1_similarity"] = round(sum(top1_sims) / len(top1_sims), 1)
            metrics["avg_top3_similarity"] = round(sum(top3_sims) / len(top3_sims), 1)
            metrics["low_similarity_count"] = sum(
                1 for sim in top1_sims if sim < self.TARGET_SIMILARITY_TOP1
            )

            # Format
            format_scores = [r["validation"]["format_score"] for r in valid_results]
            metrics["avg_format_score"] = round(sum(format_scores) / len(format_scores), 1)
            metrics["format_error_count"] = sum(
                1 for r in valid_results if r["validation"]["format_errors"]
            )
            metrics["perfect_format_count"] = sum(
                1 for score in format_scores if score == 100
            )

            # Overall quality score (weighted average)
            # Format (40%) + Performance Time (30%) + Similarity (30%)
            format_component = metrics["avg_format_score"] * 0.4

            time_score = max(0, 100 - (metrics["avg_generation_time"] / self.TARGET_TIME) * 100)
            time_component = time_score * 0.3

            similarity_component = (metrics["avg_top1_similarity"] / 100) * 100 * 0.3

            metrics["overall_quality_score"] = round(
                format_component + time_component + similarity_component, 1
            )

            # Recommendation
            if metrics["overall_quality_score"] >= 80 and metrics["success_rate"] >= 90:
                metrics["recommendation"] = "READY FOR DEPLOYMENT"
            elif metrics["overall_quality_score"] >= 60 and metrics["success_rate"] >= 70:
                metrics["recommendation"] = "NEEDS MINOR IMPROVEMENTS"
            else:
                metrics["recommendation"] = "REQUIRES SIGNIFICANT IMPROVEMENTS"

        return metrics

    def generate_manual_review_report(self, output_file: str = "quality_evaluation_report.txt") -> None:
        """Generate comprehensive report with metrics."""
        print(f"\n Generating comprehensive evaluation report...")

        if not self.test_results:
            print("  No test results available. Run evaluation first.")
            return

        # Calculate metrics
        metrics = self.calculate_metrics()

        report_lines = []

        # Header
        report_lines.append("=" * 80)
        report_lines.append("SHIELD RAG-LLM SYSTEM - COMPREHENSIVE QUALITY EVALUATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Tests: {metrics['total_tests']}")
        report_lines.append(f"Overall Recommendation: {metrics['recommendation']}")
        report_lines.append("=" * 80)
        report_lines.append("")

        # COMPREHENSIVE METRICS SECTION
        report_lines.append("" + "" * 78 + "")
        report_lines.append("" + " " * 25 + "COMPREHENSIVE METRICS" + " " * 32 + "")
        report_lines.append("" + "" * 78 + "")
        report_lines.append("")

        # Success Metrics
        report_lines.append("1. SUCCESS METRICS")
        report_lines.append("-" * 80)
        report_lines.append(
            f"   Success Rate: {metrics['success_rate']}% ({metrics['successful_tests']}/{metrics['total_tests']})")
        report_lines.append(f"   Failed Tests: {metrics['failed_tests']}")
        report_lines.append("")

        # Performance Metrics
        report_lines.append("2. PERFORMANCE METRICS")
        report_lines.append("-" * 80)
        report_lines.append(f"   Average Generation Time: {metrics['avg_generation_time']}s")
        report_lines.append(f"   Target: <{self.TARGET_TIME}s")
        status = " PASS" if metrics['avg_generation_time'] < self.TARGET_TIME else " FAIL"
        report_lines.append(f"   Status: {status}")
        report_lines.append(f"   Min Time: {metrics['min_generation_time']}s")
        report_lines.append(f"   Max Time: {metrics['max_generation_time']}s")
        report_lines.append(f"   Slow Generations: {metrics['time_threshold_violations']}")
        report_lines.append("")

        # Similarity Metrics
        report_lines.append("3. RETRIEVAL SIMILARITY METRICS")
        report_lines.append("-" * 80)
        report_lines.append(f"   Average Top-1 Similarity: {metrics['avg_top1_similarity']}%")
        report_lines.append(f"   Target: >{self.TARGET_SIMILARITY_TOP1}%")
        status = " PASS" if metrics['avg_top1_similarity'] >= self.TARGET_SIMILARITY_TOP1 else " FAIL"
        report_lines.append(f"   Status: {status}")
        report_lines.append(f"   Average Top-3 Similarity: {metrics['avg_top3_similarity']}%")
        report_lines.append(f"   Target: >{self.TARGET_SIMILARITY_TOP3}%")
        status = " PASS" if metrics['avg_top3_similarity'] >= self.TARGET_SIMILARITY_TOP3 else " FAIL"
        report_lines.append(f"   Status: {status}")
        report_lines.append(f"   Low Similarity Count: {metrics['low_similarity_count']}")
        report_lines.append("")

        # Format Metrics
        report_lines.append("4. FORMAT COMPLIANCE METRICS")
        report_lines.append("-" * 80)
        report_lines.append(f"   Average Format Score: {metrics['avg_format_score']}%")
        report_lines.append(f"   Perfect Format Count: {metrics['perfect_format_count']}/{metrics['successful_tests']}")
        report_lines.append(f"   Format Error Count: {metrics['format_error_count']}")
        report_lines.append("")

        # Manual Review Metrics (Placeholders)
        report_lines.append("5. MANUAL REVIEW METRICS (To be filled during review)")
        report_lines.append("-" * 80)
        report_lines.append(f"   Hallucination Count: [ __ ] / {metrics['successful_tests']}")
        report_lines.append(f"   Contradiction Count: [ __ ] / {metrics['successful_tests']}")
        report_lines.append(f"   Safety Issue Count: [ __ ] / {metrics['successful_tests']}")
        report_lines.append("")

        # Overall Quality Score
        report_lines.append("6. OVERALL QUALITY SCORE")
        report_lines.append("-" * 80)
        report_lines.append(f"   Quality Score: {metrics['overall_quality_score']}/100")
        report_lines.append(f"   Components:")
        report_lines.append(f"      - Format Compliance: 40%")
        report_lines.append(f"      - Generation Speed: 30%")
        report_lines.append(f"      - Retrieval Quality: 30%")
        report_lines.append(f"   Recommendation: {metrics['recommendation']}")
        report_lines.append("")
        report_lines.append("")

        # Performance Improvement Suggestions
        if metrics['avg_generation_time'] >= self.TARGET_TIME:
            report_lines.append("  PERFORMANCE IMPROVEMENT SUGGESTIONS:")
            report_lines.append("-" * 80)
            report_lines.append("   Generation time exceeds target. Consider:")
            report_lines.append("   1. Reduce max_new_tokens in LLMGenerator (current: 512)")
            report_lines.append("   2. Optimize prompt length")
            report_lines.append("   3. Use smaller/faster model variant")
            report_lines.append("   4. Implement response caching")
            report_lines.append("")

        if metrics['avg_top1_similarity'] < self.TARGET_SIMILARITY_TOP1:
            report_lines.append("  SIMILARITY IMPROVEMENT SUGGESTIONS:")
            report_lines.append("-" * 80)
            report_lines.append("   Retrieval similarity below target. Consider:")
            report_lines.append("   1. Add more diverse scenarios to database")
            report_lines.append("   2. Improve scenario embeddings with better preprocessing")
            report_lines.append("   3. Use different embedding model (try all-MiniLM-L6-v2)")
            report_lines.append("   4. Implement query expansion/reformulation")
            report_lines.append("")

        report_lines.append("")

        # Detailed test results
        report_lines.append("=" * 80)
        report_lines.append("DETAILED TEST RESULTS - MANUAL REVIEW SECTION")
        report_lines.append("=" * 80)
        report_lines.append("")

        # [Rest of the detailed results section - same as before]
        for result in self.test_results:
            report_lines.append(f"\n{'#' * 80}")
            report_lines.append(f"TEST #{result['test_id']}: {result['description']}")
            report_lines.append(f"{'#' * 80}")
            report_lines.append(f"Query: {result['query']}")
            report_lines.append(f"Mode: {result['mode']}")
            report_lines.append(f"Category: {result['category']}")
            report_lines.append(f"Time Taken: {result['time_taken']}s")

            if result.get("validation"):
                report_lines.append(f"Format Score: {result['validation']['format_score']}%")
                if result['validation']['format_errors']:
                    report_lines.append(f"Format Errors: {', '.join(result['validation']['format_errors'])}")

                perf = result['validation']['performance_checks']
                report_lines.append(f"Top-1 Similarity: {perf.get('top1_similarity', 'N/A')}%")
                report_lines.append(f"Avg Top-3 Similarity: {perf.get('avg_top3_similarity', 'N/A')}%")

            report_lines.append("")

            if result["error"]:
                report_lines.append(f" ERROR: {result['error']}")
                report_lines.append("")
                continue

            # Retrieved scenarios
            report_lines.append("-" * 80)
            report_lines.append("RETRIEVED SCENARIOS:")
            report_lines.append("-" * 80)
            for i, scenario in enumerate(result["retrieved_scenarios"], 1):
                report_lines.append(
                    f"\nScenario {i} (ID: {scenario['id']}, Similarity: {scenario['similarity']:.1f}%):")
                report_lines.append(f"  {scenario['text']}")
            report_lines.append("")

            # Generated content
            report_lines.append("-" * 80)
            report_lines.append("GENERATED CONTENT:")
            report_lines.append("-" * 80)
            report_lines.append(result["generated_content"])
            report_lines.append("")

            # Manual review checklist
            report_lines.append("-" * 80)
            report_lines.append("MANUAL REVIEW CHECKLIST:")
            report_lines.append("-" * 80)
            report_lines.append("[ ] Hallucinations: (LLM makes up facts not in scenarios)")
            report_lines.append("    Notes: _________________________________________")
            report_lines.append("")
            report_lines.append("[ ] Contradictions: (Output contradicts scenarios)")
            report_lines.append("    Notes: _________________________________________")
            report_lines.append("")
            report_lines.append("[ ] Format Errors: (Format matches requirements)")
            report_lines.append(f"    Automated Score: {result['validation']['format_score']}%")
            if result['validation']['format_errors']:
                report_lines.append(f"    Issues: {', '.join(result['validation']['format_errors'])}")
            report_lines.append("    Additional Notes: _________________________________________")
            report_lines.append("")
            report_lines.append("[ ] Safety Issues: (Unsafe advice or missing critical info)")
            report_lines.append("    Notes: _________________________________________")
            report_lines.append("")
            report_lines.append("Overall Assessment: [ ] PASS  [ ] FAIL  [ ] NEEDS REVISION")
            report_lines.append("_" * 80)
            report_lines.append("")

        # Footer
        report_lines.append("\n" + "=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)

        # Write files
        report_content = "\n".join(report_lines)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        # Save metrics and results as JSON
        json_output = {
            "metrics": metrics,
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }

        json_file = output_file.replace(".txt", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)

        print(f" Report saved to: {output_file}")
        print(f" JSON data saved to: {json_file}")
        print(f"\n KEY METRICS:")
        print(f"   Overall Quality Score: {metrics['overall_quality_score']}/100")
        print(f"   Success Rate: {metrics['success_rate']}%")
        print(f"   Avg Generation Time: {metrics['avg_generation_time']}s")
        print(f"   Avg Top-1 Similarity: {metrics['avg_top1_similarity']}%")
        print(f"   Format Score: {metrics['avg_format_score']}%")
        print(f"   Recommendation: {metrics['recommendation']}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run enhanced quality evaluation."""

    print("\n" + "" + "" * 68 + "")
    print("" + " " * 10 + "SHIELD RAG-LLM ENHANCED QUALITY EVALUATION" + " " * 15 + "")
    print("" + "" * 68 + "\n")

    evaluator = QualityEvaluator(db_path="./chroma_db")

    # Run evaluation
    results = evaluator.run_evaluation()

    # Calculate and display metrics
    metrics = evaluator.calculate_metrics()

    print("\n" + "" + "" * 68 + "")
    print("" + " " * 22 + "METRICS SUMMARY" + " " * 31 + "")
    print("" + "" * 68 + "\n")

    print(f" Overall Quality Score: {metrics['overall_quality_score']}/100")
    print(f" Success Rate: {metrics['success_rate']}%")
    print(f"⏱  Avg Generation Time: {metrics['avg_generation_time']}s (target: <{evaluator.TARGET_TIME}s)")
    print(f" Avg Top-1 Similarity: {metrics['avg_top1_similarity']}% (target: >{evaluator.TARGET_SIMILARITY_TOP1}%)")
    print(f" Avg Top-3 Similarity: {metrics['avg_top3_similarity']}% (target: >{evaluator.TARGET_SIMILARITY_TOP3}%)")
    print(f" Avg Format Score: {metrics['avg_format_score']}%")
    print(f" Format Error Count: {metrics['format_error_count']}/{metrics['successful_tests']}")
    print(f"\n Recommendation: {metrics['recommendation']}")

    # Generate report
    evaluator.generate_manual_review_report("quality_evaluation_report.txt")

    print("\n" + "" + "" * 68 + "")
    print("" + " " * 20 + "EVALUATION COMPLETE!" + " " * 26 + "")
    print("" + "" * 68 + "\n")


if __name__ == "__main__":
    main()
