"""
Scenario Standardization Module
Converts instructor input to standardized database format.
"""

import json
import re
from datetime import datetime
from typing import Dict


class ScenarioStandardizer:
    """Standardizes instructor-created scenarios to match database format."""

    def __init__(self):
        # Event type mappings with abbreviations
        self.event_types = {
            'ACC': 'Accident (ACC)',
            'MED': 'Medical (MED)',
            'FIRE': 'Fire (FIRE)',
            'ASSAULT': 'Assault (ASSAULT)',
            'ROBBERY': 'Robbery (ROBBERY)',
            'BURGLARY': 'Burglary (BURGLARY)',
            'DOMESTIC': 'Domestic (DOMESTIC)',
            'OVERDOSE': 'Overdose (OVERDOSE)',
            'CARDIAC': 'Cardiac (CARDIAC)',
            'STROKE': 'Stroke (STROKE)',
            'TRAUMA': 'Trauma (TRAUMA)',
            'OTHER': 'Other (OTHER)'
        }

    def normalize_text(self, text: str) -> str:
        """Normalize colloquial text and handle special characters."""
        if not text:
            return ""
        
        # Strip extra whitespace
        text = ' '.join(text.split())
        
        # Common colloquialisms to standard
        replacements = {
            r'\bcar\b': 'vehicle',
            r'\bgonna\b': 'going to',
            r'\bwanna\b': 'want to',
            r'\bgotta\b': 'got to',
            r'\byeah\b': 'yes',
            r'\bnope\b': 'no',
            r'\bcoz\b': 'because',
            r'\bu\b': 'you',
            r'\bur\b': 'your',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def format_event_type(self, event_type: str) -> str:
        """Format event type with abbreviation in braces."""
        if not event_type:
            return "Other (OTHER)"
        
        event_upper = event_type.upper().strip()
        
        # Check if already formatted
        if '(' in event_type and ')' in event_type:
            return event_type
        
        # Map to standard format
        return self.event_types.get(event_upper, f"{event_type} ({event_upper})")

    def generate_scenario_id(self) -> str:
        """Generate unique scenario ID with instructor prefix."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"INST_{timestamp}"

    def create_metadata(self, instructor_username: str) -> Dict:
        """Create metadata for instructor-created scenario."""
        return {
            "source_type": "instructor_created",
            "created_by": instructor_username,
            "created_at": datetime.now().isoformat(),
            "tier": "instructor_custom",
            "validated": True
        }

    def format_phone(self, phone: str) -> str:
        """Format phone to xxx-xxx-xxxx."""
        if not phone:
            return ""
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        
        return phone  # Return as-is if not 10 digits

    def convert_to_standard_format(self, raw_data: Dict, instructor_username: str) -> Dict:
        """Convert raw instructor input to standardized database format."""
        
        # Generate unique ID
        scenario_id = self.generate_scenario_id()
        
        # Normalize and format fields
        event_type = self.format_event_type(raw_data.get('event_type', ''))
        location = raw_data.get('location', '').strip()
        subtype = raw_data.get('subtype', '').strip()
        caller_name = raw_data.get('caller_name', '').strip()
        caller_phone = self.format_phone(raw_data.get('caller_phone', ''))
        complaint = self.normalize_text(raw_data.get('complaint_description', ''))
        
        # Build standardized scenario text (similar to Tier 1 format)
        scenario_text = f"""Emergency Type: {event_type}
Location: {location}
{f"Subtype: {subtype}" if subtype else ""}
Caller: {caller_name}
Callback Number: {caller_phone}

Incident Description:
{complaint}
"""
        
        # Create full scenario object
        standardized = {
            "id": scenario_id,
            "scenario_text": scenario_text.strip(),
            "event_type": event_type,
            "location": location,
            "subtype": subtype,
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "complaint_description": complaint,
            "metadata": self.create_metadata(instructor_username),
            "raw_input": raw_data  # Preserve original for reference
        }
        
        return standardized

    def validate_json(self, scenario_dict: Dict) -> tuple[bool, str]:
        """Validate that scenario can be serialized to JSON."""
        try:
            # Test JSON serialization
            json_str = json.dumps(scenario_dict, indent=2)
            
            # Test deserialization
            parsed = json.loads(json_str)
            
            # Verify required keys present
            required_keys = ['id', 'scenario_text', 'metadata']
            missing = [key for key in required_keys if key not in parsed]
            
            if missing:
                return (False, f"Missing required keys in JSON: {', '.join(missing)}")
            
            return (True, "JSON validation passed")
            
        except (TypeError, ValueError) as e:
            return (False, f"JSON serialization error: {str(e)}")

    def create_preview_comparison(self, raw_data: Dict, standardized: Dict) -> Dict:
        """Create side-by-side comparison for preview."""
        return {
            "your_input": {
                "Event Type": raw_data.get('event_type', ''),
                "Location": raw_data.get('location', ''),
                "Subtype": raw_data.get('subtype', 'N/A'),
                "Caller Name": raw_data.get('caller_name', ''),
                "Caller Phone": raw_data.get('caller_phone', ''),
                "Complaint": raw_data.get('complaint_description', '')
            },
            "standardized_format": {
                "Scenario ID": standardized['id'],
                "Event Type": standardized['event_type'],
                "Location": standardized['location'],
                "Subtype": standardized['subtype'] or 'N/A',
                "Caller Name": standardized['caller_name'],
                "Callback Number": standardized['caller_phone'],
                "Full Scenario Text": standardized['scenario_text']
            }
        }
