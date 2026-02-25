import json

REQUIRED_FIELDS = [
    "scenario_id",
    "event_type_expanded",
    "complaint_expanded",
    "primary_category",
    "sub_category",
    "incident_type",
    "severity",
    "vehicle_details",
    "injury_details",
    "location_details"
]


def check_field_completeness(scenario):
    """Check which required fields are present and calculate completeness score"""
    present_fields = []
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = scenario.get(field)
        if value is not None:
            if isinstance(value, str) and value.strip():
                present_fields.append(field)
            elif isinstance(value, dict) and value:
                present_fields.append(field)
            elif isinstance(value, list) and value:
                present_fields.append(field)
            elif not isinstance(value, (str, dict, list)):
                present_fields.append(field)
            else:
                missing_fields.append(field)
        else:
            missing_fields.append(field)

    total_fields = len(REQUIRED_FIELDS)
    present_count = len(present_fields)
    completeness_score = present_count / total_fields if total_fields > 0 else 0.0
    is_complete = completeness_score >= 0.8

    return {
        "completeness_score": round(completeness_score, 2),
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "present_fields": present_fields,
        "fields_present_count": present_count,
        "fields_total_count": total_fields
    }


def add_completeness_metrics(input_json, output_json):
    """Add completeness metrics to all scenarios"""

    with open(input_json, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"Checking completeness for {len(scenarios)} scenarios...")
    print(f"Required fields: {REQUIRED_FIELDS}\n")

    complete_count = 0
    incomplete_count = 0

    for scenario in scenarios:
        completeness_info = check_field_completeness(scenario)

        scenario["completeness_score"] = completeness_info["completeness_score"]
        scenario["is_complete"] = completeness_info["is_complete"]
        scenario["missing_fields"] = completeness_info["missing_fields"]
        scenario["fields_present_count"] = completeness_info["fields_present_count"]
        scenario["fields_total_count"] = completeness_info["fields_total_count"]

        if completeness_info["is_complete"]:
            complete_count += 1
        else:
            incomplete_count += 1
            print(f"  {scenario.get('scenario_id', 'Unknown')}: "
                  f"{completeness_info['completeness_score'] * 100:.0f}% complete "
                  f"(Missing: {', '.join(completeness_info['missing_fields'])})")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print("COMPLETENESS CHECK SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total scenarios: {len(scenarios)}")
    print(f"Complete (≥80%): {complete_count} ({complete_count / len(scenarios) * 100:.1f}%)")
    print(f"Incomplete (<80%): {incomplete_count} ({incomplete_count / len(scenarios) * 100:.1f}%)")
    print(f"\nOutput saved to: {output_json}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    # Use the ACTUAL file from your folder
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios.json"
    output_json = "/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios_with_completeness.json"

    add_completeness_metrics(input_json, output_json)
