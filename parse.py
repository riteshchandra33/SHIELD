import json
import re

def extract_fields(raw_text):
    # Case-insensitive, captures up to the next label or line-end
    event_type = re.search(r'Event\s*type[:\s]*([A-Z]+)', raw_text, re.IGNORECASE)
    location = re.search(r'Location[:\s]*([^\n:]+?)(?=Name:|Phone:|Complaint:|\n|$)', raw_text, re.IGNORECASE)
    name = re.search(r'Name[:\s]*([^\n:]+?)(?=Phone:|Complaint:|\n|$)', raw_text, re.IGNORECASE)
    phone = re.search(r'Phone[:\s]*([\d\-\(\) ]+)', raw_text, re.IGNORECASE)
    complaint = re.search(r'Complaint[:\s]*([^\n]*)', raw_text, re.IGNORECASE)
    return {
        "event_type": event_type.group(1).strip() if event_type else "",
        "location": location.group(1).strip() if location else "",
        "name": name.group(1).strip() if name else "",
        "phone": phone.group(1).strip() if phone else "",
        "complaint": complaint.group(1).strip() if complaint else "",
    }

def parse_file(input_path, parsed_output_path, report_output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    parsed = []
    field_counters = {f: 0 for f in ["event_type", "location", "name", "phone", "complaint"]}
    all_fields = ["event_type", "location", "name", "phone", "complaint"]
    success = 0
    partial = 0

    for entry in scenarios:
        fields = extract_fields(entry["raw_text"])
        found = [k for k, v in fields.items() if v.strip()]
        status = "success" if len(found) == len(all_fields) else "partial" if found else "fail"
        if status == "success":
            success += 1
        elif status == "partial":
            partial += 1
        for k in found:
            field_counters[k] += 1
        parsed.append({
            "scenario_id": entry["scenario_id"],
            **fields,
            "parse_status": status,
            "fields_found": found,
            "fields_missing": [k for k in all_fields if k not in found],
            "raw_text": entry["raw_text"]
        })

    total = len(parsed)
    stats = {
        "total_scenarios": total,
        "full_success": success,
        "partial": partial,
        "none": total - success - partial,
        "field_stats": {k: f"{field_counters[k]} found ({field_counters[k]/total*100:.1f}%)" for k in all_fields},
        "success_rate": f"{success/total*100:.1f}%",
        "partial_rate": f"{partial/total*100:.1f}%"
    }

    with open(parsed_output_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(f"Parsing Report\n{'='*60}\n")
        f.write(json.dumps(stats, indent=2, ensure_ascii=False))
        f.write("\n\nField extraction counts and %:\n")
        for k in all_fields:
            f.write(f"{k}: {field_counters[k]} ({field_counters[k]/total*100:.1f}%)\n")
        f.write(f"\nScenarios with all fields: {success}\n")
        f.write(f"Scenarios with some fields: {partial}\n")
        f.write(f"Scenarios with no fields: {total-success-partial}\n")
        f.write(f"\nOverall success rate: {stats['success_rate']}\n")

    # Print summary
    print("Parsing complete.")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_segments_complaint.json"
    parsed_output = "/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_parsed.json"
    report_output = "/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_parse_report.txt"

    parse_file(input_json, parsed_output, report_output)
