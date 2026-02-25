import streamlit as st
import random
import chromadb
from chromadb.config import Settings
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
from typing import Dict, List, Any
from validation_logic import DispatcherValidator

class AI911Caller:
    """AI that simulates a 911 caller reporting emergency - ENHANCED."""

    def __init__(self, llm_model: str = "llama3.1:8b"):
        self.llm_model = llm_model
        self.use_ollama = OLLAMA_AVAILABLE
        self.current_scenario = None
        self.information_revealed = set()

    def initialize_scenario(self, scenario_text: str):
        """Initialize with a scenario."""
        self.current_scenario = scenario_text
        self.information_revealed = set()
        self.scenario_details = self._parse_scenario(scenario_text)

    def _parse_scenario(self, scenario: str) -> Dict:
        """Parse scenario to extract key details."""
        return {
            "full_text": scenario,
            "has_injuries": "injury" in scenario.lower() or "hurt" in scenario.lower(),
            "is_blocking": "blocking" in scenario.lower(),
            "has_fire": "fire" in scenario.lower() or "smoke" in scenario.lower()
        }

    def generate_initial_call(self) -> str:
        """Generate initial 911 call (caller's first statement) - FASTER."""
        prompt = f"""Emergency caller reporting: {self.current_scenario[:150]}

Generate ONLY the caller's first urgent statement (1 sentence, 5-10 words):"""

        if self.use_ollama:
            try:
                response = ollama.generate(
                    model=self.llm_model,
                    prompt=prompt,
                    options={
                        'temperature': 0.7,
                        'num_predict': 30,
                        'num_ctx': 512
                    }
                )
                return response['response'].strip()
            except:
                return self._generate_fallback_initial_call()

        return self._generate_fallback_initial_call()

    def _generate_fallback_initial_call(self) -> str:
        """Generate quick fallback initial call based on scenario keywords."""
        scenario_lower = self.current_scenario.lower()

        if "vehicle" in scenario_lower or "car" in scenario_lower or "accident" in scenario_lower:
            return "Help! There's been a car accident! Please send help!"
        elif "fire" in scenario_lower:
            return "There's a fire! We need help immediately!"
        elif "injury" in scenario_lower or "hurt" in scenario_lower:
            return "Someone's hurt! I need an ambulance!"
        else:
            return "911! I need help right away!"

    def respond_to_dispatcher(self, dispatcher_question: str, conversation_history: List[Dict]) -> str:
        """Generate caller's response to dispatcher's question."""
        context = "\n".join([
            f"{'Dispatcher' if msg['role'] == 'trainee' else 'Caller'}: {msg['content']}"
            for msg in conversation_history[-5:]
        ])

        # Determine emotional intensity based on scenario
        emotional_level = "moderate"
        scenario_lower = self.current_scenario.lower()
        if any(word in scenario_lower for word in ["fire", "flames", "smoke", "burning"]):
            emotional_level = "very high"
        elif any(word in scenario_lower for word in ["injury", "hurt", "bleeding", "unconscious", "not breathing"]):
            emotional_level = "high"
        elif any(word in scenario_lower for word in ["accident", "crash", "collision"]):
            emotional_level = "moderate"
        
        prompt = f"""You are a REAL 911 caller reporting this emergency:

SCENARIO: {self.current_scenario}

EMOTIONAL STATE: {emotional_level} stress/panic

CONVERSATION SO FAR:
{context}

DISPATCHER'S QUESTION: {dispatcher_question}

INSTRUCTIONS - Behave like a REAL 911 caller:
1. Answer the specific question asked - be direct but SHOW EMOTION
2. Use realistic speech patterns: urgency, stress, maybe incomplete sentences
3. Express appropriate emotions based on scenario severity:
   - High stress: Use words like "Oh my God!", "Please hurry!", voice concern
   - Moderate: Show worry but more controlled
   - Include natural reactions: "I don't know!", "I'm scared!", "It's bad!"
4. Keep responses SHORT (1-2 sentences) but emotionally authentic
5. Show you're stressed/panicked through your words and tone
6. If you don't know, express it with emotion: "I don't know! I can't tell!"
7. Don't volunteer extra info, but DO show realistic emotional reactions
8. Sound like a real person in crisis, not a robot

EXAMPLES:
- "Two cars! God, it looks bad!" (not just "Two cars.")
- "I think so! There's blood!" (not just "Yes.")
- "I-I don't know! Maybe 30s or 40s?" (not just "I'm not sure.")

CALLER'S RESPONSE:"""

        if self.use_ollama:
            response = ollama.generate(
                model=self.llm_model,
                prompt=prompt,
                options={
                    'temperature': 0.7,  # Higher for more emotional/natural variety
                    'num_predict': 80,   # Increased from 60 to allow emotional expressions
                    'top_p': 0.9
                }
            )
            return response['response'].strip()

        return "I'm not sure, I just saw it happen!"

class InteractiveTrainingSystem:
    """Complete interactive training system with multi-scenario support."""

    def __init__(self, db_path: str = "./chroma_db", llm_model: str = "llama3.1:8b",
                 collection_name: str = "emergency_scenarios"):
        self.db_path = db_path
        self.llm_model = llm_model
        self.collection_name = collection_name
        self._initialize_components()

    @st.cache_resource
    def _initialize_components(_self):
        """Initialize with caching."""
        components = {}

        with st.spinner("Loading emergency scenarios..."):
            client = chromadb.PersistentClient(
                path=_self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            # Collection already has 384-dim embeddings from loaded data
            try:
                components['collection'] = client.get_or_create_collection(
                    name=_self.collection_name
                )
            except Exception as e:
                st.error(f"Failed to initialize scenario collection: {e}")
                raise

        components['ai_caller'] = AI911Caller(llm_model=_self.llm_model)
        components['validator'] = DispatcherValidator()

        return components

    def __getattr__(self, name):
        """Delegate to cached components."""
        components = self._initialize_components()
        if name in components:
            return components[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def get_all_scenarios(self) -> List[Dict]:
        """Get ALL scenarios from database."""
        components = self._initialize_components()
        results = components['collection'].get(include=["documents", "metadatas"])

        scenarios = []
        if results["ids"] and results["documents"]:
            for i in range(len(results["ids"])):
                scenarios.append({
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    "preview": results["documents"][i][:100] + "..." if len(results["documents"][i]) > 100 else results["documents"][i]
                })

        return scenarios

    def get_scenario_by_id(self, scenario_id: str) -> Dict:
        """Get specific scenario by ID."""
        components = self._initialize_components()
        results = components['collection'].get(
            ids=[scenario_id],
            include=["documents", "metadatas"]
        )

        if results["ids"] and results["documents"]:
            return {
                "id": results["ids"][0],
                "text": results["documents"][0],
                "metadata": results["metadatas"][0] if results["metadatas"] else {}
            }
        return None

    def get_random_scenario(self) -> Dict:
        """Get a random scenario from database."""
        all_scenarios = self.get_all_scenarios()
        if all_scenarios:
            return random.choice(all_scenarios)
        return None
