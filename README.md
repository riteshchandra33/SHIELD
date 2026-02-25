# SHIELD — Simulation-Based Human Intelligence for Emergency Law Dispatch

SHIELD is an AI-powered training platform for 911 emergency dispatchers. It provides a complete end-to-end pipeline — from raw scenario ingestion and quality assurance through to an interactive AI-driven simulation engine that trains dispatchers under realistic call conditions.

---

## System Architecture

```
 Scenario Book (Gold Standard)
          |
          v
 [1] Load & Parse Scenarios
   load_scenarios.py | parse.py | structure.py
          |
          v
 [2] Abbreviation Expansion & Validation
   abbreviation.py
   Abbreviations_Event_type.xlsx | Abbreviations_short_forms.xlsx
          |
          v
 [3] Completeness Check
   completeness_check.py
          |
          v
 [4] Segmentation
   segmentation.py
          |
          v
 [5] Scenario Validation & Standardization
   validation.py | validation_logic.py
   scenario_validator.py | scenario_standardizer.py
          |
          v
 [6] Ontology Validation  (every scenario must pass)
   ontology_validator.py
   - Unsafe content detection
   - Protocol compliance check
   - Hallucination detection
   - Confidence scoring (PASS / REVIEW / FAIL)
          |
          v
 [7] Quality Evaluation  (>= 85% cosine similarity to pass)
   quality_eval.py | quality_eval_with_validation.py
   quality_metrics.py | report_generation.py
          |
          v
 [8] Vector Database Deployment
   chromadb_deployment.py | vector_Db.py
   Embedding model: all-mpnet-base-v2 (768-dim)
   Distance metric: cosine
          |
          v
 [9] Simulation Engine  (end-to-end)
   simulation_engine.py
   - AI 911 caller (powered by Ollama / llama3.1:8b)
   - Real-time dispatcher validation
   - Scenario retrieval from ChromaDB
   - Session management via database_manager.py
```

---

## Pipeline Stages

### Stage 1 — Load & Parse
Raw scenarios are loaded from the gold-standard scenario book and parsed into structured components.

**Files:** `load_scenarios.py`, `parse.py`, `structure.py`, `structure_Report.py`

---

### Stage 2 — Abbreviation Expansion
All abbreviations used in 911 call data are expanded and validated against the reference tables before scenarios are used in training.

**Files:** `abbreviation.py`, `Abbreviations_Event_type.xlsx`, `Abbreviations_short_forms.xlsx`

---

### Stage 3 — Completeness Check
Scenarios are checked to ensure all required fields are present (location, injury status, vehicle details, hazards, caller info).

**Files:** `completeness_check.py`

---

### Stage 4 — Segmentation
Scenario text is segmented into structured units for downstream processing.

**Files:** `segmentation.py`

---

### Stage 5 — Validation & Standardization
Scenarios are validated against protocol rules and standardized into a consistent format.

**Files:** `validation.py`, `validation_logic.py`, `scenario_validator.py`, `scenario_standardizer.py`

---

### Stage 6 — Ontology Validation
Every scenario must pass through the 911 Ontology Validator before it can enter the simulation. The validator checks:

- **Unsafe content** — flags instructions that violate 911 protocols (e.g., "move the vehicle", "provide first aid")
- **Protocol compliance** — verifies mandatory information categories are covered (location, injuries, vehicles, caller info, hazards, emergency status)
- **Hallucination detection** — cross-checks facts in the response against the scenario
- **Confidence scoring** — PASS (>= 0.70), REVIEW (>= 0.50), FAIL (< 0.50)

**Files:** `ontology_validator.py`

---

### Stage 7 — Quality Evaluation
Only scenarios achieving >= 85% cosine similarity score are approved for deployment into the simulation engine.

**Files:** `quality_eval.py`, `quality_eval_with_validation.py`, `quality_metrics.py`, `report_generation.py`

---

### Stage 8 — Vector Database
Approved scenarios are embedded using `all-mpnet-base-v2` (768-dimensional) and stored in ChromaDB with cosine distance for semantic retrieval.

**Files:** `chromadb_deployment.py`, `vector_Db.py`

| Setting | Value |
|---------|-------|
| Embedding model | `all-mpnet-base-v2` |
| Embedding dimension | 768 |
| Distance metric | Cosine |
| Collection name | `emergency_scenarios` |

---

### Stage 9 — Simulation Engine
The core training interface. Provides an end-to-end interactive training session where an AI simulates a real 911 caller and evaluates the dispatcher trainee in real time.

**File:** `simulation_engine.py`

Key components:

| Class | Description |
|-------|-------------|
| `AI911Caller` | Simulates a caller with realistic emotional responses. Powered by Ollama (`llama3.1:8b`). Falls back to rule-based responses if Ollama is unavailable. |
| `InteractiveTrainingSystem` | Manages scenario retrieval from ChromaDB, session state, and trainee evaluation. |

**Supporting:** `database_manager.py` — manages user accounts, roles (instructor/trainee), and session records.

---

## Scenario Data Files

| File | Description |
|------|-------------|
| `final_scenarios.json` | Base scenario set |
| `final_scenarios_validated.json` | After ontology validation |
| `final_scenarios_with_completeness.json` | After completeness check |
| `final_scenarios_with_quality.json` | After quality evaluation (>= 85% cosine sim) |
| `embedding_ready_scenarios.json` | Final set with 768-dim embeddings, ready for ChromaDB |

---

## Requirements

```bash
pip install streamlit chromadb sentence-transformers ollama numpy
```

For LLM-powered caller simulation:
```bash
# Install Ollama: https://ollama.com
ollama pull llama3.1:8b
```

---

## Setup & Run

### 1. Deploy the Vector Database
```bash
python chromadb_deployment.py
```

### 2. Run the Simulation Engine
```bash
streamlit run simulation_engine.py
```

---

## Dispatcher Evaluation Criteria

The `DispatcherValidator` (`validation_logic.py`) scores trainee performance across 6 mandatory protocol categories:

| Category | Keywords |
|----------|----------|
| Location | where, address, street, route, highway |
| Injuries | injury, hurt, injured, pain, medical |
| Vehicles | vehicle, car, truck, how many |
| Caller info | name, phone, callback, contact |
| Hazards | danger, fire, blocking, hazard, traffic |
| Emergency status | conscious, breathing, trapped, serious |

**Scoring:**

| Score | Status |
|-------|--------|
| >= 83% categories covered | PASS |
| >= 67% categories covered | REVIEW |
| < 67% categories covered | FAIL |

---

## Repository Structure

```
SHIELD/
├── simulation_engine.py          # Core simulation engine
├── validation_logic.py           # Dispatcher evaluation
├── database_manager.py           # User & session DB
├── chromadb_deployment.py        # ChromaDB setup & deployment
├── vector_Db.py                  # Vector DB utilities
├── ontology_validator.py         # 911 protocol ontology validator
├── abbreviation.py               # Abbreviation expansion
├── Abbreviations_Event_type.xlsx # Event type abbreviation table
├── Abbreviations_short_forms.xlsx# Short-form abbreviation table
├── completeness_check.py         # Scenario completeness checker
├── segmentation.py               # Scenario segmentation
├── validation.py                 # Protocol validation
├── scenario_validator.py         # Scenario-level validator
├── scenario_standardizer.py      # Scenario standardizer
├── quality_eval.py               # Quality evaluation (85% threshold)
├── quality_eval_with_validation.py
├── quality_metrics.py            # Cosine similarity metrics
├── report_generation.py          # Quality report generator
├── load_scenarios.py             # Scenario loader
├── parse.py                      # Data parser
├── structure.py                  # Data structure utilities
├── structure_Report.py           # Structure report
├── final_scenarios.json          # Base scenarios
├── final_scenarios_validated.json
├── final_scenarios_with_completeness.json
├── final_scenarios_with_quality.json
└── embedding_ready_scenarios.json # ChromaDB-ready (768-dim)
```

---

## License

Private repository — all rights reserved.
