"""
Scenario Validation Module
Validates instructor-created scenarios for quality and compliance.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings


@dataclass
class ValidationResult:
    """Result of scenario validation."""
    passed: bool
    critical_failures: List[str]
    warnings: List[str]
    checks_passed: int
    checks_total: int
    details: Dict


class ScenarioValidator:
    """Validates instructor-created scenarios."""

    def __init__(self, chroma_collection=None):
        self.chroma_collection = chroma_collection
        
        # Profanity word list (basic - can be expanded)
        self.profanity_list = [
            'fuck', 'shit', 'damn', 'bitch', 'asshole', 'bastard',
            'crap', 'hell', 'piss', 'dick', 'cock', 'pussy'
        ]
        
        # PII patterns
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.full_address_pattern = re.compile(r'\b\d{3,5}\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd)\b', re.IGNORECASE)

    def validate_required_fields(self, scenario_data: Dict) -> Tuple[bool, List[str]]:
        """Check if all required fields are present and valid."""
        required_fields = ['event_type', 'location', 'caller_name', 'caller_phone', 'complaint_description']
        missing_fields = []
        
        for field in required_fields:
            if field not in scenario_data or not scenario_data[field] or str(scenario_data[field]).strip() == '':
                missing_fields.append(field)
        
        # Validate phone format (10 digits)
        if 'caller_phone' in scenario_data and scenario_data['caller_phone']:
            phone = re.sub(r'\D', '', scenario_data['caller_phone'])
            if len(phone) != 10:
                missing_fields.append('caller_phone (invalid format)')
        
        return (len(missing_fields) == 0, missing_fields)

    def check_profanity(self, text: str) -> Tuple[bool, List[str]]:
        """Check for profanity in text."""
        if not text:
            return (True, [])
        
        text_lower = text.lower()
        found_profanity = [word for word in self.profanity_list if word in text_lower]
        
        return (len(found_profanity) == 0, found_profanity)

    def check_complaint_structure(self, complaint: str) -> Tuple[bool, str]:
        """Verify complaint has basic structure (verb + subject)."""
        if not complaint or len(complaint.strip()) < 10:
            return (False, "Complaint too short (minimum 10 characters)")
        
        # Simple heuristic: check for common verbs
        common_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'need', 'needs', 
                       'hit', 'crashed', 'fell', 'injured', 'hurt', 'burning', 'fire', 
                       'stuck', 'trapped', 'bleeding', 'unconscious', 'breathing']
        
        complaint_lower = complaint.lower()
        has_verb = any(verb in complaint_lower for verb in common_verbs)
        
        # Check for nouns/subjects (basic)
        has_subject = any(word in complaint_lower for word in ['person', 'car', 'vehicle', 'man', 'woman', 
                                                                'child', 'accident', 'fire', 'patient'])
        
        if not has_verb:
            return (False, "Complaint missing action verb")
        if not has_subject:
            return (False, "Complaint missing subject")
        
        return (True, "")

    def check_pii(self, text: str) -> Tuple[bool, List[str]]:
        """Check for personal identifying information beyond caller name."""
        if not text:
            return (True, [])
        
        pii_found = []
        
        # Check for SSN
        if self.ssn_pattern.search(text):
            pii_found.append("Social Security Number")
        
        # Check for full addresses (victims - caller location is OK)
        # This is a simple check - might need refinement
        
        return (len(pii_found) == 0, pii_found)

    def find_similar_scenarios(self, complaint: str, threshold: float = 0.9) -> List[Dict]:
        """Find similar scenarios in database using vector similarity."""
        if not self.chroma_collection or not complaint:
            return []
        
        try:
            # Query ChromaDB for similar scenarios
            results = self.chroma_collection.query(
                query_texts=[complaint],
                n_results=5
            )
            
            similar_scenarios = []
            if results['ids'] and results['distances']:
                for i, scenario_id in enumerate(results['ids'][0]):
                    # ChromaDB returns distances (lower is more similar)
                    # Convert to similarity score
                    distance = results['distances'][0][i]
                    similarity = 1.0 / (1.0 + distance)  # Simple conversion
                    
                    if similarity >= threshold:
                        similar_scenarios.append({
                            'id': scenario_id,
                            'similarity': similarity,
                            'text': results['documents'][0][i] if results['documents'] else ""
                        })
            
            return similar_scenarios
        except Exception as e:
            print(f"Error finding similar scenarios: {e}")
            return []

    def validate_scenario(self, scenario_data: Dict) -> ValidationResult:
        """Run complete validation pipeline."""
        critical_failures = []
        warnings = []
        checks_passed = 0
        checks_total = 7
        
        details = {}
        
        # 1. Required fields
        fields_valid, missing = self.validate_required_fields(scenario_data)
        details['required_fields'] = {'valid': fields_valid, 'missing': missing}
        if fields_valid:
            checks_passed += 1
        else:
            critical_failures.append(f"Missing required fields: {', '.join(missing)}")
        
        # 2. Profanity check
        complaint = scenario_data.get('complaint_description', '')
        profanity_clean, found_profanity = self.check_profanity(complaint)
        details['profanity'] = {'clean': profanity_clean, 'found': found_profanity}
        if profanity_clean:
            checks_passed += 1
        else:
            critical_failures.append(f"Inappropriate language detected: {', '.join(found_profanity)}")
        
        # 3. Complaint structure
        structure_valid, structure_msg = self.check_complaint_structure(complaint)
        details['complaint_structure'] = {'valid': structure_valid, 'message': structure_msg}
        if structure_valid:
            checks_passed += 1
        else:
            warnings.append(structure_msg)
        
        # 4. PII check
        pii_clean, pii_found = self.check_pii(complaint)
        details['pii'] = {'clean': pii_clean, 'found': pii_found}
        if pii_clean:
            checks_passed += 1
        else:
            critical_failures.append(f"Personal identifying information found: {', '.join(pii_found)}")
        
        # 5. Location format (simple check)
        location = scenario_data.get('location', '')
        location_valid = len(location.strip()) > 5
        details['location'] = {'valid': location_valid}
        if location_valid:
            checks_passed += 1
        else:
            warnings.append("Location seems too short")
        
        # 6. Phone format (already checked in required fields)
        phone = scenario_data.get('caller_phone', '')
        phone_digits = re.sub(r'\D', '', phone)
        phone_valid = len(phone_digits) == 10
        details['phone'] = {'valid': phone_valid}
        if phone_valid:
            checks_passed += 1
        
        # 7. Event type present
        event_type = scenario_data.get('event_type', '')
        event_valid = bool(event_type and event_type.strip())
        details['event_type'] = {'valid': event_valid}
        if event_valid:
            checks_passed += 1
        
        # Overall pass/fail
        passed = len(critical_failures) == 0
        
        return ValidationResult(
            passed=passed,
            critical_failures=critical_failures,
            warnings=warnings,
            checks_passed=checks_passed,
            checks_total=checks_total,
            details=details
        )
