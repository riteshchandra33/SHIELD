import json
import re
import pandas as pd

def load_abbreviation_dict(excel_path, key_col, val_col):
    df = pd.read_excel(excel_path, dtype=str)
    abbr_dict = {}
    for _, row in df.iterrows():
        key = str(row[key_col]).strip() if pd.notnull(row[key_col]) else ""
        val = str(row[val_col]).strip() if pd.notnull(row[val_col]) else ""
        if key and val and key.lower() != val.lower():
            abbr_dict[key] = val
    return abbr_dict

def case_preserving_replace(word, repl):
    # Lowercase, uppercase, or title as appropriate
    if word.islower():
        return repl.lower()
    elif word.isupper():
        return repl.upper()
    elif word.istitle():
        return repl.title()
    else:
        return repl

def is_likely_abbreviation(token):
    # Flag token if ALL CAPS 2-5 chars, or letter/number mix, or contains / or -
    return ((token.isupper() and 2 <= len(token) <= 5) or
            (re.match(r"^[A-Z0-9]{2,5}$", token)) or
            (re.match(r"^[A-Z]{1,3}/[A-Z]{1,3}$", token)) or
            (any(c in "/-&" for c in token)))

def strict_expand_abbreviations(text, abbr_dict, unknown_abbrs, case_sensitive=True):
    found = []
    tokens = re.findall(r'\b\w+\b|\W+', text)
    expanded_tokens = []
    abbr_keys = set(abbr_dict.keys()) if case_sensitive else set(k.lower() for k in abbr_dict.keys())
    seen = set()
    for token in tokens:
        token_key = token if case_sensitive else token.lower()
        found_abbr = False
        for abbr in abbr_dict:
            match_abbr = abbr if case_sensitive else abbr.lower()
            if token_key == match_abbr and token_key not in seen:
                found.append(abbr)
                expanded_tokens.append(case_preserving_replace(token, abbr_dict[abbr]))
                seen.add(token_key)
                found_abbr = True
                break
        if not found_abbr:
            expanded_tokens.append(token)
            # Only flag as unknown if abbreviation-like
            if (is_likely_abbreviation(token) and
                token_key not in abbr_keys and
                token_key not in seen):
                unknown_abbrs.add(token)
    expanded = ''.join(expanded_tokens)
    return expanded, found

def run_pipeline(parsed_json_path, event_excel, event_key, event_val,
                 short_excel, short_key, short_val,
                 output_expanded_path, output_report_path, unknown_abbr_path):
    with open(parsed_json_path, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    event_dict = load_abbreviation_dict(event_excel, event_key, event_val)
    short_dict = load_abbreviation_dict(short_excel, short_key, short_val)
    full_short_dict = {**event_dict, **short_dict}
    expansion_stats = {
        'total_scenarios': len(scenarios),
        'expanded_scenarios': 0,
        'field_counts': {'event_type': 0, 'complaint': 0},
        'unknown_abbrs': set()
    }
    expanded_scenarios = []

    for scen in scenarios:
        unknown_abbrs_this = set()
        event_type_shorthand = scen.get('event_type', '').strip()
        complaint_shorthand = scen.get('complaint', '').strip()
        # Event type: strict, case sensitive
        expanded_event_type, found_event_type = strict_expand_abbreviations(
            event_type_shorthand, event_dict, unknown_abbrs_this, case_sensitive=True)
        # Complaint: strict, case insensitive
        expanded_complaint, found_complaint = strict_expand_abbreviations(
            complaint_shorthand, full_short_dict, unknown_abbrs_this, case_sensitive=False)
        scenario_expanded = {
            "scenario_id": scen["scenario_id"],
            "event_type_shorthand": event_type_shorthand,
            "event_type_expanded": expanded_event_type,
            "complaint_shorthand": complaint_shorthand,
            "complaint_expanded": expanded_complaint,
            "event_expanded_abbrs": list(set(found_event_type)),
            "complaint_expanded_abbrs": list(set(found_complaint)),
            "unknown_abbrs": sorted(list(unknown_abbrs_this)),
            "n_expanded_event_type": len(found_event_type),
            "n_expanded_complaint": len(found_complaint)
        }
        expansion_stats['unknown_abbrs'].update(unknown_abbrs_this)
        if found_event_type:
            expansion_stats['field_counts']['event_type'] += 1
        if found_complaint:
            expansion_stats['field_counts']['complaint'] += 1
        if found_event_type or found_complaint:
            expansion_stats['expanded_scenarios'] += 1
        expanded_scenarios.append(scenario_expanded)

    with open(output_expanded_path, "w", encoding="utf-8") as f:
        json.dump(expanded_scenarios, f, indent=2, ensure_ascii=False)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump({
            'total_scenarios': expansion_stats['total_scenarios'],
            'scenarios_with_expansions': expansion_stats['expanded_scenarios'],
            'field_expansion_counts': expansion_stats['field_counts'],
            'unknown_abbreviations': sorted(list(expansion_stats['unknown_abbrs']))
        }, f, indent=2)
    with open(unknown_abbr_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(expansion_stats['unknown_abbrs'])), f, indent=2, ensure_ascii=False)
    print(f"Abbreviation expansion complete.\nOutputs: {output_expanded_path}, {output_report_path}, {unknown_abbr_path}")

if __name__ == "__main__":
    parsed_json_path = '/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_parsed.json'
    event_excel = '/Users/riteshchandra/PycharmProjects/SHIELD/Abbreviations_Event_type.xlsx'
    short_excel = '/Users/riteshchandra/PycharmProjects/SHIELD/Abbreviations_short_forms.xlsx'
    event_key, event_val = 'Acronym', 'Abbreviations'
    short_key, short_val = 'Unnamed: 1', 'Unnamed: 2'
    output_expanded_path = '/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_expanded.json'
    output_report_path = '/Users/riteshchandra/PycharmProjects/SHIELD/property_damage_expansion_report.txt'
    unknown_abbr_path = '/Users/riteshchandra/PycharmProjects/SHIELD/unexpandable_abbrs.json'
    run_pipeline(parsed_json_path, event_excel, event_key, event_val,
                 short_excel, short_key, short_val,
                 output_expanded_path, output_report_path, unknown_abbr_path)
