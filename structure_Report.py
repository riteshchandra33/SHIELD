import json
from collections import Counter

def main():
    input_path = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios.json"
    output_path = "/Users/riteshchandra/PycharmProjects/SHIELD/structuring_report.txt"

    with open(input_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    category_counts = Counter(sc.get("primary_category", "unknown") for sc in scenarios)
    subcat_counts = Counter(sc.get("sub_category", "unknown") for sc in scenarios)
    incident_counts = Counter(sc.get("incident_type", "unspecified") for sc in scenarios)
    severity_counts = Counter(sc.get("severity", "medium") for sc in scenarios)
    tag_counter = Counter(tag for sc in scenarios for tag in sc.get("controlled_tags", []))
    unique_tags = sorted(set(tag_counter))
    avg_tags = sum(len(sc.get("controlled_tags", [])) for sc in scenarios) / len(scenarios)
    complete_scenarios = sum(1 for sc in scenarios if sc.get("summary_quality_ok"))
    total = len(scenarios)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Scenario Structuring Report\n==============================\n")
        f.write(f"Total Scenarios: {total}\n")
        f.write(f"Primary Category Counts: {dict(category_counts)}\n")
        f.write(f"Sub-category Counts: {dict(subcat_counts)}\n")
        f.write(f"Incident Type Counts: {dict(incident_counts)}\n")
        f.write(f"Severity Counts: {dict(severity_counts)}\n")
        f.write(f"Unique Tags Used: {unique_tags}\n")
        f.write(f"Tag Usage: {dict(tag_counter)}\n")
        f.write(f"Average tags per scenario: {avg_tags:.2f}\n")
        f.write(f"Complete scenarios: {complete_scenarios} ({complete_scenarios/total*100:.1f}%)\n")
        assessment = ("Assessment: Successful (all scenarios classified well)"
                      if complete_scenarios == total and len(unique_tags) >= 12
                      else "Assessment: Needs review (see counts above for issues)")
        f.write(assessment + "\n")
    print(f"Structuring report complete: {output_path}")

if __name__ == "__main__":
    main()
