# Employee Retention Support System

> **An Enterprise Explainable AI & Longitudinal Workforce Signal Engine**  
> Analyzes synthetic engagement, tenure, role, and workload signals to prioritize supportive, human-in-the-loop retention conversations — with strict data integrity, survey neutrality, and zero pre-outcome leakage.

---

## 1. Business Problem & Solution Overview

### The Problem
Traditional employee attrition systems focus on predictive "flight risk" probabilities that penalize employees, create toxic surveillance perceptions, and lack actionable context. Furthermore, data quality issues — such as treating missing surveys as disengagement or misinterpreting planned sprint crunches as burnout — lead to biased interventions.

### Our Solution
The **Employee Retention Support System** is designed around supportive, non-punitive decision support:
1. **Explainable Priority Signals, Not Resignation Scores**: Prioritizes managerial 1-on-1 conversations with clear factor attribution chips rather than publishing a punitive probability score.
2. **Strict Pre-Outcome Temporal Barrier**: Historical snapshots (tenure, workload, engagement surveys) strictly precede post-observation exit outcomes (`attrition_outcomes`).
3. **Mandatory Survey Neutrality**: Voluntary survey skips (`is_missing = TRUE`) store `NULL` sentiment scores without score penalties or negative imputation.
4. **Benign Surge Differentiation**: Distinguishes temporary project crunches without sentiment decline (`is_benign_surge = TRUE`) from chronic, multi-week overtime strain.
5. **Effective-Dated Team Membership**: Preserves historical team and role transfers without overwriting previous organizational records.
6. **Human-in-the-Loop Traceability**: Every intervention records agreed supportive actions, follow-up milestones, and an immutable lifecycle event trail.

---

## 2. What Was Done — Step-by-Step Implementation Record

Here is the exact chronological breakdown of the end-to-end implementation:

### Step 1: Database Architecture & Migration Layer
- Built 18 SQLAlchemy domain and supporting models in `backend/app/models/`:
  - **Core Entities**: `Employee`, `Role`, `Team`, `TeamMembershipHistory`, `TenureSnapshot`, `WorkloadSnapshot`, `EngagementSurvey`, `CompensationBand`, `PromotionHistory`, `AttritionOutcome`, `Intervention`, `InterventionEvent`.
  - **Governance & RBAC**: `AppUser`, `AuditLog`.
  - **Audit & Analytics**: `ValidationRun`, `ValidationIssue`, `AnalysisRun`, `SupportAssessment`, `GroundTruthAnomaly`.
- Configured PostgreSQL 18 connection with the modern `psycopg` (v3) driver and connection pooling.
- Configured Alembic migrations in `backend/alembic/`:
  - `001_initial_schema.py`: Initial creation of all 18 tables, compound unique constraints, foreign keys, and indexes.
  - `002_expand_user_roles.py`: Expansion of RBAC user roles (`EMPLOYEE`, `MANAGER`, `HR_PARTNER`, `IT_OPS_PARTNER`, `ADMIN`, `SYSTEM_ADMIN`, `AUDITOR`).
- Enforced deterministic identifier formats across all entities:
  - Employee: `EMP-000001`
  - Tenure Snapshot: `SNAP-EMP-000001-2024Q1`
  - Workload Snapshot: `WORK-EMP-000001-2024Q1`
  - Engagement Survey: `SURV-2024-000001`
  - Intervention: `INT-2026-000001`
  - Attrition Outcome: `OUT-EMP-000001-2026`

### Step 2: Synthetic Data Generator & Deterministic Seeding
- Implemented `SyntheticDataGenerator` in `backend/app/services/generator.py`:
  - Deterministic generation with fixed seed (`20261022`).
  - Longitudinal simulation of 10,000 employees over 24 months across 8 quarters (`2024Q1` through `2025Q4`).
  - Enforced strict pre-outcome temporal barriers where all feature snapshots end at `2025-12-31` while voluntary attrition outcomes occur in `2026`.
  - Injected realistic survey non-response rates (~12%) handled with survey neutrality.
  - Simulated intentional isolated test anomalies in `ground_truth_anomalies` to demonstrate test isolation from model features.
- Created `seed_synthetic_data.py` CLI script and automatic in-memory seeder for rapid testing.

### Step 3: Heuristics & Explainable Rules Engine
- Developed the explainable rules engine in `backend/app/services/rules.py`:
  - Evaluates pre-outcome longitudinal features to produce a composite priority score (0–100) and priority tiers (`HIGH`, `MEDIUM`, `LOW`).
  - Generates transparent **Factor Attribution Chips** across 4 categories:
    - `WORKLOAD`: Sustained overtime (>5 hrs/wk for 4+ consecutive weeks), filtering out benign release surges.
    - `CAREER_GROWTH`: Extended role stagnation (>24 months without promotion or lateral move).
    - `ENGAGEMENT`: Quarterly sentiment drops, ignoring missing surveys.
    - `COMPENSATION`: Salary lagging below band midpoint target.
  - Generates recommended supportive 1-on-1 conversation topics (e.g. sprint offloading, roadmap review).

### Step 4: FastAPI REST API Implementation
- Created 14 modular routers in `backend/app/routers/` mounted under `/api/v1`:
  1. `auth.py`: JWT login, registration, current profile (`/me`), password changes, logout.
  2. `employees.py`: Employee directory CRUD, prioritized retention list, summary, 24-month longitudinal timeline.
  3. `teams.py`: Teams directory, membership rosters, effective-dated employee transfers.
  4. `roles.py`: Standard job classification roles and levels.
  5. `engagement.py`: Quarterly engagement pulse surveys with neutrality handling.
  6. `workload.py`: Workload and capacity strain snapshots with benign surge indicators.
  7. `compensation.py`: Standard pay bands and employee promotion records.
  8. `assessments.py`: Rules engine trigger, historical analysis runs, assessment details.
  9. `interventions.py`: Human-in-the-loop check-ins, lifecycle status updates, outcomes, and event trail.
  10. `analytics.py`: Executive overview metrics, departmental retention breakdowns, longitudinal trends.
  11. `data_quality.py`: Automated validation suite triggers, run history, isolated ground-truth anomalies.
  12. `admin.py`: User management, RBAC role updates, system database health statistics, audit logs.
  13. `audit.py`: Reconciliation reports and metrics overview.
  14. `generator.py`: Reproducible synthetic data generation and verification.
- Implemented comprehensive Pydantic v2 schemas for all requests and responses in `backend/app/schemas/`.
- Configured CORS middleware for frontend communication (`http://localhost:5173`).

### Step 5: Data Quality & Integrity Validation Suite
- Built `DataQualityService` in `backend/app/services/data_quality_service.py`:
  - Automated validation checking 12 critical relational, temporal, and neutrality constraints.
  - Verifies zero data leakage from post-observation outcomes into feature snapshots.
  - Verifies survey neutrality (no default 0 or negative scores for skipped surveys).
  - Isolates ground-truth anomalies in a dedicated table so test validation never leaks into predictive feature sets.

### Step 6: Pytest Automated Test Suite
- Implemented 48 tests across 15 test files in `backend/tests/`:
  - `test_primary_key_uniqueness.py`: Primary key integrity and collision rejection.
  - `test_foreign_key_relationships.py`: Foreign key constraints and cascade rules.
  - `test_duplicate_records.py`: Compound unique quarterly constraints.
  - `test_date_validation.py`: Chronological invariants (effective dates, hire dates).
  - `test_enum_validation.py`: Enum validation for roles, statuses, and movements.
  - `test_employee_history_consistency.py`: Preservation of historical snapshots during profile updates.
  - `test_attrition_outcome_consistency.py`: Strict pre-outcome separation and ground-truth isolation.
  - `test_historical_snapshot_preservation.py`: 8-quarter snapshot preservation.
  - `test_auth_rbac.py`: JWT token lifecycle, role-based endpoint authorization.
  - `test_backend_features.py`: Team transfers, promotions, and intervention events.
  - `test_rules.py`: Heuristic prioritization, factor attribution, and benign surge classification.
  - `test_validator.py`: Data quality suite execution and issue detection.
  - `test_generator.py`: Deterministic seed reproducibility.
  - `test_api.py`: FastAPI endpoint integration contracts.
- **Test Results**: All 48 tests pass cleanly on PostgreSQL (`retention_test`).

### Step 7: React 18 + Vite + Tailwind CSS Enterprise Frontend
- Built the modern frontend inside `frontend/`:
  - **Enterprise Design**: Deep forest green sidebar (`#064e3b`) with emerald accents, clean white cards, and `Inter` typography.
  - **Centralized Axios Client** (`src/api/client.js`): Injects JWT bearer tokens, unwraps responses, and handles automatic 401 token expiration redirects.
  - **Authentication Context** (`src/context/AuthContext.jsx`): Manages user state, token persistence in `localStorage`, and role-checking helpers.
  - **Role-Based Protected Routes** (`src/components/ProtectedRoute.jsx`): Guards sensitive views with graceful "Access Restricted" fallback screens.
  - **Interactive Visualizations (Recharts)**:
    - 8-quarter workload hours and overtime rate dual-axis trend line chart.
    - Departmental retention signals vs interventions bar chart.
    - Priority tier distribution donut chart.
  - **12 Major Operational Screens**:
    1. `LoginPage.jsx`: Sign in with 4 one-click demo credential fillers (`sys_admin`, `hr_partner_1`, `manager_apollo`, `it_ops_lead`).
    2. `RegisterPage.jsx`: Account creation with platform role assignment.
    3. `ProfilePage.jsx`: Current user details and change password form.
    4. `DashboardPage.jsx`: Executive KPI cards, workload trends, and quick actions.
    5. `RetentionWorkbenchPage.jsx`: The centerpiece workbench for prioritized supportive check-ins, factor chips, and rule re-evaluation.
    6. `EmployeeDirectoryPage.jsx`: Searchable employee directory, department filters, and "Add Employee" modal.
    7. `EmployeeProfilePage.jsx`: 360 profile with 4 tabbed longitudinal views (24-month timeline, workload, surveys, promotions).
    8. `TeamsPage.jsx`: Team roster cards, member modal, and effective-dated transfer modal.
    9. `RolesPage.jsx`: Standard job classification levels and pay band mapping.
    10. `EngagementSurveysPage.jsx`: Pulse surveys with neutrality badges and survey logger.
    11. `WorkloadPage.jsx`: Capacity strain snapshots with benign surge indicators.
    12. `CompensationPage.jsx`: Compensation bands and career promotion history.
    13. `InterventionsPage.jsx`: Human-in-the-loop check-ins with full event audit timeline.
    14. `AnalyticsPage.jsx`: Departmental comparisons and longitudinal trend reports.
    15. `DataQualityPage.jsx`: Automated validation test runner and isolated anomaly viewer.
    16. `AdminPage.jsx`: System database health stats, user role management, and audit logs.

### Step 8: Build Verification & Clean State
- Compiled the production bundle with Vite (`npm run build`), verifying zero errors and clean asset emission.
- Configured FastAPI static files to serve the compiled frontend automatically.
- Committed all files cleanly to git (`2fbecc5`).

---

## 3. Architecture & Entities

```
+----------------------------------------------------------------------------------------------------+
|                                    EMPLOYEE RETENTION ENGINE                                       |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   +-----------------------+       +------------------------+       +---------------------------+   |
|   |   CompensationBand    |       |          Role          |       |           Team            |   |
|   |-----------------------|       |------------------------|       |---------------------------|   |
|   | band_id (PK)          |<------| role_id (PK)           |   +-->| team_id (PK)              |   |
|   | name, min, mid, max   |       | title, level, band_id  |   |   | name, department, lead_id |   |
|   +-----------------------+       +------------------------+   |   +---------------------------+   |
|                                                |               |                 |                 |
|                                                v               |                 v                 |
|                                   +----------------------------+   +---------------------------+   |
|                                   |          Employee          |   |  TeamMembershipHistory    |   |
|                                   |----------------------------|   |---------------------------|   |
|                                   | employee_id (PK)           |   | membership_id (PK)        |   |
|                                   | name, email, hire_date,    |   | employee_id (FK)          |   |
|                                   | current_salary, status     |   | team_id, start_date,      |   |
|                                   +----------------------------+   | end_date, is_current      |   |
|                                                  |                 +---------------------------+   |
|         +-----------------------+----------------+-----------------------+                         |
|         |                       |                |                       |                         |
|         v                       v                v                       v                         |
| +-------------------+ +-------------------+ +-------------------+ +-------------------+            |
| |  TenureSnapshot   | | WorkloadSnapshot  | | EngagementSurvey  | | PromotionHistory  |            |
| |-------------------| |-------------------| |-------------------| |-------------------|            |
| | snapshot_id (PK)  | | workload_id (PK)  | | survey_id (PK)    | | promotion_id (PK) |            |
| | employee_id (FK)  | | employee_id (FK)  | | employee_id (FK)  | | employee_id (FK)  |            |
| | quarter, tenure   | | avg_weekly_hours, | | satisfaction,     | | from_role, to_role|            |
| | months_in_role    | | overtime_hours,   | | balance, growth,  | | from_sal, to_sal  |            |
| |                   | | is_benign_surge   | | is_missing        | | movement_type     |            |
| +-------------------+ +-------------------+ +-------------------+ +-------------------+            |
|                                                  |                                                 |
|         +----------------------------------------+---------------------------------------+         |
|         |                                                                                |         |
|         v                                                                                v         |
| +------------------------------------+                        +----------------------------------+ |
| |      AttritionOutcome [GROUND]     |                        |           Intervention           | |
| |------------------------------------|                        |----------------------------------| |
| | outcome_id (PK)                    |                        | intervention_id (PK)             | |
| | employee_id (FK)                   |                        | employee_id (FK), conducted_by   | |
| | attrition_date, voluntary, reason  |                        | date, type, summary, status      | |
| | (Strictly isolated pre-outcome)    |                        +----------------------------------+ |
| +------------------------------------+                                           |                 |
|                                                                                  v                 |
|                                                               +----------------------------------+ |
|                                                               |        InterventionEvent         | |
|                                                               |----------------------------------| |
|                                                               | event_id (PK), intervention_id   | |
|                                                               | event_type, timestamp, actor_id  | |
|                                                               +----------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

### Deterministic Identifier Formats

| Entity | Primary Key Pattern | Example |
| :--- | :--- | :--- |
| **Employee** | `EMP-{seq:06d}` | `EMP-000001` |
| **Role** | `ROLE-{level}-{code}` | `ROLE-IC3-SWE`, `ROLE-M1-MGR` |
| **Team** | `TEAM-{dept}-{seq}` | `TEAM-ENG-01`, `TEAM-SALES-01` |
| **Team Membership** | `MEM-{seq:06d}` | `MEM-000001` |
| **Tenure Snapshot** | `SNAP-{employee_id}-{quarter}` | `SNAP-EMP-000001-2024Q1` |
| **Workload Snapshot** | `WORK-{employee_id}-{quarter}` | `WORK-EMP-000001-2024Q1` |
| **Engagement Survey** | `SURV-{year}-{seq:06d}` | `SURV-2024-000001` |
| **Compensation Band** | `BAND-{level}` | `BAND-IC1`, `BAND-M2` |
| **Promotion History** | `PROM-{year}-{seq:06d}` | `PROM-2024-000001` |
| **Attrition Outcome** | `OUT-{employee_id}-{year}` | `OUT-EMP-000001-2026` |
| **Intervention** | `INT-{year}-{seq:06d}` | `INT-2026-000001` |
| **Intervention Event**| `INTEV-{year}-{seq:06d}` | `INTEV-2026-000001` |
| **App User** | `USR-{seq:06d}` | `USR-000001` |
| **Audit Log** | `AUD-{seq:06d}` | `AUD-000001` |

---

## 4. Complete Project Directory Layout

```
Hackathon/
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 001_initial_schema.py       # 18 tables, constraints, foreign keys
│   │       └── 002_expand_user_roles.py    # Expanded RBAC roles
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py                   # Pydantic Settings & environment variables
│   │   │   ├── dependencies.py             # RBAC role guards & user injection
│   │   │   └── security.py                 # Bcrypt password hashing & JWT tokens
│   │   ├── database/
│   │   │   └── session.py                  # PostgreSQL engine & session maker
│   │   ├── models/                         # 18 SQLAlchemy domain models
│   │   ├── routers/                        # 14 FastAPI REST routers
│   │   ├── schemas/                        # Pydantic request & response schemas
│   │   └── services/                       # Business logic services
│   │       ├── analytics_service.py        # Longitudinal metric rollups
│   │       ├── assessment_service.py       # Assessment generation & execution
│   │       ├── audit_service.py            # Audit logging service
│   │       ├── auth_service.py             # User lifecycle & bcrypt auth
│   │       ├── compensation_service.py     # Pay bands & promotions
│   │       ├── data_quality_service.py     # Schema validation runner
│   │       ├── employee_service.py         # Directory & timeline builder
│   │       ├── engagement_service.py       # Pulse surveys with neutrality
│   │       ├── generator.py                # Synthetic data generator
│   │       ├── intervention_service.py     # Touchpoints & event logging
│   │       ├── rules.py                    # Explainable heuristics engine
│   │       ├── store.py                    # Store coordinator & memory cache
│   │       ├── team_service.py             # Effective-dated transfers
│   │       ├── validator.py                # Validation rules
│   │       └── workload_service.py         # Hours & benign surge logic
│   ├── data/exports/                       # Deterministic CSV/JSON exports
│   ├── scripts/
│   │   ├── check_db.py                     # Connection diagnostic
│   │   ├── run_generator.py                # Generator CLI
│   │   ├── run_rules.py                    # Rules engine CLI
│   │   ├── run_validator.py                # Validator CLI
│   │   ├── seed_synthetic_data.py          # 10,000-employee seeder
│   │   └── setup_test_db.py                # Test DB provisioning
│   ├── tests/                              # 15 test suites (48 pytest tests)
│   ├── alembic.ini
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/                            # 12 centralized Axios API modules
│   │   ├── components/                     # 10 modular React components
│   │   ├── context/
│   │   │   └── AuthContext.jsx             # JWT auth & session management
│   │   ├── layouts/
│   │   │   └── AppLayout.jsx               # Dark-green sidebar enterprise layout
│   │   ├── pages/                          # 16 complete application views
│   │   ├── App.jsx                         # Router configuration
│   │   ├── index.css                       # Tailwind directives
│   │   └── main.jsx                        # React root entry
│   ├── .env                                # VITE_API_BASE_URL=http://localhost:8000/api/v1
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

---

## 5. How to Run the System Step-by-Step

### Prerequisites
- **Operating System:** Windows
- **Database:** PostgreSQL 18 (installed locally at `localhost:5432`)
- **Python:** 3.10+
- **Node.js:** 18+ (tested on Node v22.16.0 / npm 10.9.2)

---

### Step 1: Ensure PostgreSQL is Running
Open Command Prompt as Administrator and ensure the PostgreSQL service is active:
```powershell
net start postgresql-x64-18
```

Verify that the databases `retention` and `retention_test` exist:
```powershell
"C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -p 5432 retention
"C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -p 5432 retention_test
```

---

### Step 2: Configure Environment Variables
Inside `backend/.env`:
```ini
DATABASE_URL=postgresql+psycopg://postgres:Hack2026@localhost:5432/retention
JWT_SECRET=th5WgL_GDY1FOBe-n_Akfq2byZInd1IE0qg7NuCEYhUyfIVKZsJrEhIJpesc_Dwc
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GENERATOR_SEED=20261022
CORS_ORIGINS=http://localhost:5173
```

Inside `frontend/.env`:
```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

### Step 3: Run Database Migrations
Apply Alembic migrations to bring the PostgreSQL schema to the latest version:
```powershell
cd C:\CandidateWorkspace\Hackathon\backend
python -m alembic upgrade head
```

---

### Step 4: Run the Backend Test Suite
Verify database constraints, RBAC, business logic, and API endpoints:
```powershell
cd C:\CandidateWorkspace\Hackathon\backend
python -m pytest tests/ -v
```
*(All 48 tests pass cleanly in ~27 seconds against `retention_test`).*

---

### Step 5: Start the FastAPI Backend
Launch the FastAPI server:
```powershell
cd C:\CandidateWorkspace\Hackathon\backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000/api/v1`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Redoc Documentation: `http://localhost:8000/redoc`

---

### Step 6: Start the React Frontend
In a separate terminal:
```powershell
cd C:\CandidateWorkspace\Hackathon\frontend
npm run dev
```
- Open your browser to: **`http://localhost:5173`**

*(Alternatively, to build the production bundle: `npm run build`. The FastAPI server will automatically serve the static bundle directly at `http://localhost:8000`)*.

---

## 6. Pre-Configured Demo Credentials

The login page at `http://localhost:5173/login` provides **One-Click Quick-Fill buttons** for instant evaluation across roles:

| Persona | Role | Username | Password | Permitted Views |
| :--- | :--- | :--- | :--- | :--- |
| **System Admin** | `ADMIN` | `sys_admin` | `AdminPass123!` | All views (System Stats, User Admin, Audit Logs, Workbench) |
| **HR Partner** | `HR_PARTNER` | `hr_partner_1` | `HrPass123!` | Workbench, Interventions, Data Quality, Surveys, Directory |
| **Team Manager** | `MANAGER` | `manager_apollo`| `ManagerPass123!` | Workbench, Team Roster, Interventions, Surveys, Analytics |
| **IT/Ops Partner** | `IT_OPS_PARTNER` | `it_ops_lead` | `ItOpsPass123!` | Workload Snapshots, Capacity Strain, Interventions |
| **Employee** | `EMPLOYEE` | `sarah_connor` | `EmployeePass123!` | Personal 360 Longitudinal Profile, Directory |

---

## 7. API Endpoints Reference Table

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access token |
| | `POST` | `/api/v1/auth/register` | Register new user account with role |
| | `GET` | `/api/v1/auth/me` | Retrieve current authenticated user profile |
| | `POST` | `/api/v1/auth/change-password` | Update current user password with bcrypt |
| | `POST` | `/api/v1/auth/logout` | Revoke access token |
| **Employees** | `GET` | `/api/v1/employees` | Search, filter, and paginate employees |
| | `POST` | `/api/v1/employees` | Create employee and initialize membership |
| | `GET` | `/api/v1/employees/{id}` | Retrieve 360 employee profile |
| | `PUT` | `/api/v1/employees/{id}` | Update employee profile with audit logging |
| | `GET` | `/api/v1/employees/{id}/timeline` | Fetch full 24-month longitudinal snapshot history |
| | `GET` | `/api/v1/employees/prioritized` | Fetch prioritized candidates with factor chips |
| | `GET` | `/api/v1/employees/summary` | Summary counts of prioritized tiers |
| **Teams** | `GET` | `/api/v1/teams` | List organizational teams |
| | `POST` | `/api/v1/teams` | Create new team |
| | `GET` | `/api/v1/teams/{id}/members` | List current team members |
| | `POST` | `/api/v1/teams/{id}/transfer` | Effective-dated employee team transfer |
| **Roles** | `GET` | `/api/v1/roles` | List job classifications and levels |
| | `POST` | `/api/v1/roles` | Create new job role |
| **Engagement** | `GET` | `/api/v1/engagement/surveys` | List quarterly pulse surveys |
| | `POST` | `/api/v1/engagement/surveys` | Record survey enforcing survey neutrality |
| | `PUT` | `/api/v1/engagement/surveys/{id}` | Update permitted survey fields |
| **Workload** | `GET` | `/api/v1/workload/snapshots` | List quarterly capacity strain snapshots |
| | `POST` | `/api/v1/workload/snapshots` | Record workload snapshot with benign surge flag |
| **Compensation** | `GET` | `/api/v1/compensation/bands` | List approved compensation pay bands |
| | `POST` | `/api/v1/compensation/bands` | Create compensation band |
| | `GET` | `/api/v1/compensation/promotions` | List employee promotion records |
| | `POST` | `/api/v1/compensation/promotions` | Record promotion or lateral career move |
| **Assessments** | `POST` | `/api/v1/assessments/generate` | Run rules engine up to observation cutoff |
| | `GET` | `/api/v1/assessments/runs` | List past assessment analysis runs |
| | `GET` | `/api/v1/assessments` | List explainable support assessments |
| | `GET` | `/api/v1/assessments/{id}` | Get single assessment factor breakdown |
| **Interventions** | `GET` | `/api/v1/interventions` | List supportive 1-on-1 check-ins |
| | `POST` | `/api/v1/interventions` | Log new human-in-the-loop check-in |
| | `GET` | `/api/v1/interventions/{id}` | Get intervention detail and full event history |
| | `PUT` | `/api/v1/interventions/{id}/status` | Update lifecycle status (`SCHEDULED` -> `COMPLETED`) |
| | `PUT` | `/api/v1/interventions/{id}/outcome` | Record simulated retention outcome |
| | `POST` | `/api/v1/interventions/{id}/events` | Append touchpoint event to audit timeline |
| **Analytics** | `GET` | `/api/v1/analytics/overview` | High-level organizational KPIs |
| | `GET` | `/api/v1/analytics/team-summary` | Departmental metrics and signal breakdown |
| | `GET` | `/api/v1/analytics/trends` | 8-quarter longitudinal trends for Recharts |
| **Data Quality** | `POST` | `/api/v1/data-quality/validate` | Trigger full automated schema validation |
| | `GET` | `/api/v1/data-quality/runs` | List historical validation runs |
| | `GET` | `/api/v1/data-quality/runs/{id}/issues` | Get identified issues categorized by severity |
| | `GET` | `/api/v1/data-quality/ground-truth` | Fetch isolated ground-truth anomalies |
| **Admin** | `GET` | `/api/v1/admin/users` | List registered system users |
| | `POST` | `/api/v1/admin/users` | Provision new user account |
| | `PUT` | `/api/v1/admin/users/{id}/role` | Update user RBAC role assignment |
| | `GET` | `/api/v1/admin/system-stats` | Masked DB URL, engine, and table counts |
| | `GET` | `/api/v1/admin/audit-logs` | Query immutable audit log records |
| **Generator** | `POST` | `/api/v1/generator/regenerate` | Deterministic synthetic dataset regeneration |
| | `GET` | `/api/v1/generator/verify-reproducibility`| Verify identical outputs with same seed |

---

## 8. Ethical AI & Data Governance Guarantees

1. **Non-Punitive Explainable Signals**: Composite priority scores are designed strictly for supportive managerial 1-on-1 check-in prioritization. No flight-risk scores or resignation probabilities are ever shown to employees.
2. **Strict Pre-Outcome Temporal Barrier**: All feature snapshots (tenure, workload, engagement, promotions) strictly reflect pre-outcome observations ending at `2025-12-31`. Voluntary attrition outcomes (`2026`) are strictly separated into a distinct table to ensure zero label leakage.
3. **Survey Neutrality Mandate**: Voluntary survey skips (`is_missing = TRUE`) store `NULL` for sentiment dimensions. Heuristics treat missing surveys as neutral data incompleteness, guaranteeing employees are never penalized for exercising their right to privacy.
4. **Benign Surge Differentiation**: High workload alone does not flag high retention risk. Short-term release crunches without sentiment decline are classified as benign surges (`is_benign_surge = TRUE`), avoiding false alarms during planned project sprints.
5. **Effective-Dated History**: Employee role and team transitions are captured via effective-dated records (`team_membership_history`), ensuring full historical auditability without destructive overwrites.
6. **Immutable Audit Trail**: All state mutations (user role modifications, profile edits, intervention status updates) trigger structured audit log records in `audit_logs` capturing actor IDs, timestamps, and JSON state diffs.
