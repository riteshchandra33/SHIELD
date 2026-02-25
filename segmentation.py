import json
import re

def segment_from_json(input_json_path, output_json_path, min_len=20):
    with open(input_json_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    segments = []
    serial = 1
    for entry in scenarios:
        text = entry.get("raw_text") or entry.get("text") or ""
        # Split at "Event type" marker only if not already segmented into scenarios
        blocks = re.split(r'(?=Event\s*[Tt]ype[:\s])', text, flags=re.IGNORECASE) if serial == 1 else [text]
        for block in blocks:
            block_clean = "\n".join([line for line in block.splitlines() if line.strip() != ""]).strip()
            if len(block_clean) < min_len:  # Skip trivial/doc title/empty blocks
                continue
            segment = {
                "scenario_id": f"Scenario_{serial:03d}",
                "raw_text": block_clean,
                "line_count": len(block_clean.splitlines()),
                "character_count": len(block_clean),
            }
            segments.append(segment)
            serial += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)
    print(f"Segmented scenarios saved to {output_json_path}")

if __name__ == "__main__":
    input_json = "/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_scenarios.json"
    output_json = "/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_segments_complaint.json"
    segment_from_json(input_json, output_json)
