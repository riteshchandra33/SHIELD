import json
import re

# ---- Vocabularies ----
primary_categories = {
    "traffic": ["accident", "collision", "crash", "vehicle", "roadway"],
    "medical": ["medical", "injury", "illness", "ems", "emergency"],
    "fire": ["fire", "smoke", "burn", "flames"],
    "crime": ["theft", "assault", "robbery", "vandalism", "burglary"],
    "alarm": ["alarm", "system outage", "hold-up"],
    "public_service": ["public service", "assist", "check", "patrol", "complaint"]
}
sub_categories = {
    "traffic": ["vehicle_accident", "traffic_hazard", "hit_and_run", "parking_violation"],
    "medical": ["injury_scene", "cardiac_arrest", "trauma", "fall"],
    "fire": ["structure_fire", "vehicle_fire", "alarm_only"],
    "crime": ["property_damage", "personal_injury", "weapon_involved"],
    "alarm": ["commercial_alarm", "residential_alarm", "fire_alarm"],
    "public_service": ["welfare_check", "standby", "noise_complaint"]
}
incident_types = {
    "vehicle_accident": ["property_damage_only", "minor_injury", "major_injury", "fatal", "hit_and_run"],
    "structure_fire": ["small_fire", "contained_fire", "major_loss"],
    "property_damage": ["minor", "moderate", "major_loss"],
    "public_service": ["assist_person", "lockout", "lost_property"]
}
controlled_tags = {
    "vehicle_accident": [
        ("no injuries|minor damage", "property_damage_only"),
        ("injury|injuries|complains of pain", "minor_injury"),
        ("critical|fatal|not breathing", "fatal"),
        ("hit[- ]?and[- ]?run|fled|left scene", "hit_and_run"),
        ("blocking", "blocking_traffic"),
        ("not blocking", "not_blocking"),
        ("fire", "vehicle_fire"),
        ("rollover", "rollover"),
    ],
}

# ---- Classification & Extraction ----
def classify_primary_category(event_type_full):
    l = event_type_full.lower()
    for cat, patterns in primary_categories.items():
        for p in patterns:
            if p in l:
                return cat
    return "unknown"
def classify_sub_category(primary, complaint):
    l = complaint.lower()
    for sub in sub_categories.get(primary, []):
        if sub.replace("_", " ") in l:
            return sub
    if primary == "traffic":
        if "vehicle" in l:
            return "vehicle_accident"
    return "other"
def classify_incident_type(sub, complaint):
    l = complaint.lower()
    for inc in incident_types.get(sub, []):
        if inc.replace("_", " ") in l:
            return inc
    if "no injuries" in l or "no injury" in l:
        return "property_damage_only"
    return "unspecified"
def classify_severity(complaint):
    cl = complaint.lower()
    if "no injuries" in cl and "not blocking" in cl:
        return "low"
    if "critical" in cl or "fatal" in cl or "major injury" in cl:
        return "critical"
    if "minor injury" in cl or "pain" in cl or "injuries" in cl:
        return "medium"
    if "blocking" in cl or "significant damage" in cl:
        return "high"
    return "medium"
def assign_controlled_tags(sub, complaint):
    tags = set()
    tag_patterns = controlled_tags.get(sub, [])
    for pat, label in tag_patterns:
        if re.search(pat, complaint, re.I):
            tags.add(label)
    return sorted(tags)[:7]
def extract_vehicle_details(complaint):
    makes = ["toyota","honda","ford","chevy","nissan","bmw","mercedes","vw"]
    colors = ["red","blue","gray", "grey", "black", "white", "silver", "green"]
    types = ["car", "suv", "truck", "vehicle", "van", "jeep"]
    count = len(re.findall(r"\b(car|suv|truck|vehicle|van|jeep)\b", complaint, re.I))
    found_colors = [c for c in colors if c in complaint.lower()]
    found_makes = [m for m in makes if m in complaint.lower()]
    found_types = [t for t in types if t in complaint.lower()]
    return {"vehicle_count": count, "colors": found_colors, "makes": found_makes, "types": found_types}
def extract_injury_details(complaint):
    l = complaint.lower()
    if "no injury" in l or "no injuries" in l:
        return {"injury_present": False, "injury_count": 0, "severity": "none"}
    elif "injury" in l or "injuries" in l or "pain" in l:
        return {"injury_present": True, "injury_count": 1, "severity": "minor"}
    elif "critical" in l or "fatal" in l:
        return {"injury_present": True, "injury_count": 1, "severity": "critical"}
    else:
        return {"injury_present": None}
def extract_location_details(complaint):
    l = complaint.lower()
    if "parking lot" in l:
        location_type = "parking_lot"
    elif "intersection" in l:
        location_type = "intersection"
    elif "highway" in l:
        location_type = "highway"
    else:
        location_type = "unknown"
    blocking = "not blocking" not in l and "blocking" in l
    return {"location_type": location_type, "blocking": blocking}
def extract_search_keywords(complaint):
    makes = ["toyota","honda","ford","chevy","nissan","bmw","mercedes","vw"]
    colors = ["red","blue","gray", "grey", "black", "white", "silver", "green"]
    found_colors = [c for c in colors if c in complaint.lower()]
    found_makes = [m for m in makes if m in complaint.lower()]
    streets = re.findall(r"\b[A-Z][a-z]+ (Street|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln)\b", complaint)
    return {"colors": found_colors, "makes": found_makes, "streets": streets}

def enrich_scenario(sc):
    event_full = sc.get("event_type_expanded", "")
    complaint = sc.get("complaint_expanded", "")
    primary = classify_primary_category(event_full)
    sub = classify_sub_category(primary, complaint)
    incident = classify_incident_type(sub, complaint)
    severity = classify_severity(complaint)
    tags = assign_controlled_tags(sub, complaint)
    veh = extract_vehicle_details(complaint)
    inj = extract_injury_details(complaint)
    loc = extract_location_details(complaint)
    keyw = extract_search_keywords(complaint)
    sc_final = {
        **sc,
        "primary_category": primary,
        "sub_category": sub,
        "incident_type": incident,
        "severity": severity,
        "controlled_tags": tags,
        "vehicle_details": veh,
        "injury_details": inj,
        "location_details": loc,
        "keywords": keyw
    }
    sc_final['summary_quality_ok'] = all([event_full, complaint, primary != "unknown"])
    return sc_final

def main():
    with open("/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_expanded.json") as f:
        scenarios = json.load(f)
    final_scenarios = [enrich_scenario(sc) for sc in scenarios]
    with open("/Users/riteshchandra/PycharmProjects/SHIELD/final_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(final_scenarios, f, indent=2, ensure_ascii=False)
    print("Structured scenarios saved to final_scenarios.json")

if __name__ == "__main__":
    main()
