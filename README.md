# Supportive Retention Signal Engine

> **A decision support platform analyzing synthetic longitudinal workforce signals (engagement, workload, role, tenure) to prioritize supportive, human-in-the-loop retention conversations.**

---

## 1. Executive Summary & Problem Context

Organizations struggle with retaining top talent because traditional indicators are either **lagging** (exit interviews occur after the resignation is committed) or **misinterpreted** (an employee skipping an optional pulse survey is unfairly penalized as "disengaged"; temporary release crunch overtime is mistaken for chronic burnout).

### Ethical Guardrails & Objective
1. **Supportive, Not Punitive**: The system produces opportunities for empathy, mentorship, and workload rebalancing—**never** automatic employment decisions or unilateral termination flags.
2. **Explainability First**: Every prioritized employee surfaces plain-English factor attributions and recommended 1-on-1 topics, rejecting black-box scores.
3. **Strict Pre-Outcome Temporal Barrier**: Only features generated before the observation cutoff date are used for scoring. Zero future information leakage.
4. **Deterministic Reproducibility**: 10,000 synthetic employee histories generated deterministically over 24 months with fixed seed `20261022`.
5. **Isolated Anomaly Ground Truth**: Deliberately injected negative scenarios are recorded in an isolated ground truth file (`data/ground_truth.json`), never silently corrupting model features.

---

## 2. System Architecture: Modular Separation

The workspace is cleanly partitioned into three independent tiers:

```
Hackathon/
├── frontend/               # Interactive Web Dashboard (Tailwind CSS, Lucide, Chart.js)
│   └── index.html          # Workbench, 360 Timeline, Intervention Hub & Audit Console
├── backend/                # Core Business Logic & Services
│   ├── generator/          # Synthetic Data Generator CLI & domain logic
│   ├── rules/              # Explainable Scoring & Prioritization Engine
│   ├── validator/          # Integrity, Temporal & Edge Case Validation Engine
│   ├── routers/            # FastAPI REST endpoints
│   ├── schemas/            # Pydantic data contracts
│   ├── services/           # Data store coordinator & algorithms
│   ├── models.py           # SQLAlchemy ORM definitions for all 10 core entities
│   ├── database.py         # Session & DB engine setup (SQLite / PostgreSQL)
│   └── main.py             # FastAPI application entrypoint & static frontend mount
├── db/
│   └── schema.sql          # Relational DDL schema with constraints & indexes
├── docs/
│   └── data_dictionary.md  # Data Dictionary covering all entities and fields
├── data/                   # Generated CSVs, manifest.json, and ground_truth.json
└── tests/                  # Automated pytest test suites (14 tests)
```

---

## 3. Core Entities & Relationships

| Entity Name | Primary Key | Key Foreign Keys | Purpose |
| :--- | :--- | :--- | :--- |
| `teams` | `team_id` | — | Organizational units / departments |
| `compensation_bands` | `band_id` | — | Salary benchmarking (min, mid, max) |
| `roles` | `role_id` | `band_id` | Job titles and levels (IC1–IC6, M1–M3) |
| `employees` | `employee_id` | `team_id`, `role_id`, `manager_id` | Core master profile (`EMP-000001`) |
| `tenure_snapshots` | `snapshot_id` | `employee_id`, `role_id`, `team_id` | Quarterly tenure & time-in-role |
| `workload_snapshots` | `workload_id` | `employee_id` | Weekly hours, overtime streaks, project counts |
| `engagement_surveys`| `survey_id` | `employee_id` | Quarterly pulse scores (1.00–5.00) & missingness |
| `promotion_histories`| `promotion_id` | `employee_id`, `from_role_id`, `to_role_id` | Internal promotions and lateral transfers |
| `attrition_outcomes` | `outcome_id` | `employee_id` | Future voluntary attrition (5–15% rate) |
| `interventions` | `intervention_id` | `employee_id`, `conducted_by_id` | Supportive 1-on-1 retention touchpoint notes |
| `ground_truth_anomalies` | `anomaly_id` | `record_id` | Isolated repository of injected edge cases |

---

## 4. Handling the 4 Mandatory Edge Cases

The solution injects, isolates, and verifies the 4 required negative scenarios:

| Anomaly Type | Injected Scenario | Detection & Validation Check |
| :--- | :--- | :--- |
| `FUTURE_INFO_LEAK` | A workload record in 2024Q2 references post-observation outcome data before the cutoff date. | `temporal_boundary_future_leakage` validates observation timestamps against the horizon cutoff. |
| `MISSING_SURVEY_PUNITIVE` | An employee skips an optional pulse survey; a biased system imputed 1.00 instead of `NULL`. | `missing_survey_neutrality` enforces that `is_missing=TRUE` must strictly have `NULL` satisfaction score. |
| `OUTCOME_DATE_MISMATCH` | An employee has `status = 'ACTIVE'`, but an attrition record exists with a past termination date. | `outcome_lifecycle_consistency` reconciles employment lifecycle state with historical exit dates. |
| `UNEXPLAINED_SCORE` | An automated retention trigger executes without human-in-the-loop discussion notes or explanations. | `intervention_human_explainability` blocks automated decisions lacking human discussion summaries. |

---

## 5. Quickstart Guide

### Prerequisites
- Python 3.10+ (Standard library, SQLite, FastAPI, SQLAlchemy, Uvicorn, Pytest)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings pytest httpx
```

### 2. Generate Synthetic Longitudinal Dataset (10,000 Employees)
Generates 10,000 synthetic employee histories over 24 months (8 quarters) with fixed seed `20261022` and exports artifacts to `data/`:
```bash
python -m backend.generator.main --scale 10000 --seed 20261022 --output-dir data
```

### 3. Run Validation & Anomaly Audit Suite
Validates primary key uniqueness, foreign key integrity, temporal cutoff boundaries, survey neutrality, and reconciles ground truth:
```bash
python -m backend.validator.main --data-dir data
```

### 4. Run Explainable Prioritization Rules CLI
Evaluates supportive retention signals and displays top prioritized employees with factor explanations:
```bash
python -m backend.rules.main --data-dir data --top 10
```

### 5. Launch the Web Server & Interactive Dashboard
Start the FastAPI server:
```bash
uvicorn backend.main:app --port 8000
```
Open your browser to:
- **Interactive Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 6. Automated Testing & Verification

Run the complete test suite (14 test cases covering reproducibility, data integrity, edge case detection, explainability, and REST API contracts):
```bash
python -m pytest tests/ -v
```

### Demonstrating Dual Seed Reproducibility
To demonstrate identical row counts and checksums across repeated runs with seed `20261022`:
```bash
python -c "from backend.routers.generator import verify_reproducibility; print(verify_reproducibility(seed=20261022, scale=200).data)"
```
Output:
```json
{
  "seed": 20261022,
  "scale": 200,
  "reproducibility_verified": true,
  "sample_verification_passed": true
}
```

---

## 7. REST API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/api/v1/employees/prioritized` | Paginated queue of employees prioritized for supportive retention check-ins with explainability chips |
| `GET` | `/api/v1/employees/summary` | Organizational counts of High, Medium, and Low priority retention candidates |
| `GET` | `/api/v1/employees/{id}/timeline` | Full 24-month longitudinal timeline (workload hours, survey trend, promotions) |
| `GET` | `/api/v1/interventions` | List of logged human-in-the-loop retention check-ins |
| `POST`| `/api/v1/interventions` | Commit a supportive retention check-in (validates human review requirement) |
| `GET` | `/api/v1/audit/validation-report` | Full validation report with pass/fail breakdown across all 8 checks |
| `GET` | `/api/v1/audit/ground-truth` | Isolated repository of the 4 injected negative scenarios |
| `GET` | `/api/v1/audit/metrics` | High-level organizational overview and data integrity recall metrics |
| `POST`| `/api/v1/generator/regenerate` | Deterministically re-seed the dataset with custom scale and seed |
| `GET` | `/api/v1/generator/verify-reproducibility` | Dual regeneration test proving exact checksum & row count matching |
