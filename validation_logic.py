from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ValidationResult:
    """Result of ontology validation."""
    valid: bool
    confidence: float = 0.0
    issues: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "PASS"

class DispatcherValidator:
    """Validates trainee responses - ENHANCED."""

    def __init__(self):
        self.mandatory_questions = {
            "location": ["location", "where", "address", "street", "route", "highway"],
            "injuries": ["injury", "hurt", "injured", "pain", "medical"],
            "vehicles": ["vehicle", "car", "truck", "how many", "color", "make", "model"],
            "caller_info": ["name", "phone", "callback", "contact"],
            "hazards": ["danger", "fire", "blocking", "hazard", "traffic", "leak"],
            "emergency_status": ["conscious", "breathing", "trapped", "serious", "critical"]
        }

        # Question indicators - ENHANCED
        self.question_indicators = [
            "what", "where", "when", "who", "how", "which", "why",
            "can you", "could you", "tell me", "do you", "are you",
            "is there", "are there", "have you", "did you"
        ]

        self.inappropriate_responses = [
            "move the vehicle", "provide first aid", "drive to hospital",
            "leave the scene", "admit fault"
        ]

    def validate_trainee_question(self, question: str) -> Dict:
        """Validate if trainee asked appropriate dispatcher question - ENHANCED."""
        question_lower = question.lower()

        # Check for question indicators (improved detection)
        has_question_mark = "?" in question
        has_question_word = any(word in question_lower for word in self.question_indicators)
        is_question = has_question_mark or has_question_word

        categories_covered = []
        for category, keywords in self.mandatory_questions.items():
            if any(keyword in question_lower for keyword in keywords):
                categories_covered.append(category)

        inappropriate = []
        for bad_phrase in self.inappropriate_responses:
            if bad_phrase in question_lower:
                inappropriate.append(bad_phrase)

        is_appropriate = len(inappropriate) == 0

        return {
            "is_appropriate": is_appropriate,
            "categories_covered": categories_covered,
            "inappropriate_content": inappropriate,
            "is_question": is_question,
            "has_question_mark": has_question_mark,
            "has_question_word": has_question_word
        }

    def evaluate_conversation(self, conversation: List[Dict]) -> ValidationResult:
        """Evaluate entire conversation for protocol compliance - ENHANCED."""
        # Filter out the initial dispatcher greeting
        trainee_messages = [msg for msg in conversation if msg["role"] == "trainee"]

        # Skip the first message if it's the greeting
        first_msg = trainee_messages[0]["content"].lower() if trainee_messages else ""
        is_greeting = any(phrase in first_msg for phrase in ["911", "9-1-1", "emergency", "what's your emergency"])

        if is_greeting and len(trainee_messages) > 0:
            trainee_questions = trainee_messages[1:]  # Skip greeting
        else:
            trainee_questions = trainee_messages

        all_categories_covered = set()
        all_inappropriate = []
        question_count = 0

        for msg in trainee_questions:
            validation = self.validate_trainee_question(msg["content"])
            all_categories_covered.update(validation["categories_covered"])
            all_inappropriate.extend(validation["inappropriate_content"])
            if validation["is_question"]:
                question_count += 1

        total_categories = len(self.mandatory_questions)
        coverage_score = len(all_categories_covered) / total_categories
        missing_categories = set(self.mandatory_questions.keys()) - all_categories_covered

        if all_inappropriate:
            confidence = 0.0
            status = "FAIL"
        elif coverage_score >= 0.83:
            confidence = 1.0
            status = "PASS"
        elif coverage_score >= 0.67:
            confidence = 0.7
            status = "REVIEW"
        else:
            confidence = 0.5
            status = "FAIL"

        result = ValidationResult(
            valid=(status == "PASS"),
            confidence=confidence,
            status=status,
            details={
                "categories_covered": list(all_categories_covered),
                "missing_categories": list(missing_categories),
                "coverage_score": coverage_score,
                "question_count": question_count,
                "total_messages": len(trainee_questions),
                "inappropriate_content": all_inappropriate
            }
        )

        if missing_categories:
            result.issues.append(f"Missing protocol categories: {', '.join(missing_categories)}")
        if all_inappropriate:
            result.issues.append(f"Inappropriate dispatcher responses: {', '.join(all_inappropriate)}")
        if question_count < 6:
            result.issues.append(f"Asked only {question_count} questions, should ask at least 6")

        return result
