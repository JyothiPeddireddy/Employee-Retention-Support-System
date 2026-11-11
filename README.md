# Employee Retention Support System
## Phase 1 Database Implementation & Architecture

> **A PostgreSQL & SQLAlchemy database engine analyzing synthetic longitudinal engagement, tenure, role, and workload signals to prioritize supportive, human-in-the-loop retention conversations.**

---

## 1. Project Overview & Architecture

The database architecture is designed with strict enterprise data governance standards:
- **14 Core Domain Entities + 4 Supporting Entities**: Fully modeled in SQLAlchemy with relationships, primary keys, foreign keys, check constraints, indexes, and timestamps.
- **Strict Pre-Outcome Temporal Barrier**: Historical snapshots (tenure, workload, engagement surveys) strictly precede post-observation exit outcomes (`attrition_outcomes`).
- **Survey Neutrality**: Voluntary skips (`is_missing = TRUE`) strictly store `NULL` sentiment scores, preventing punitive bias against missing survey data.
- **Effective-Dated Team Membership**: `team_membership_history` preserves past team and role transfers without overwriting historical records.
- **Deterministic Nomenclature**:
  - Employee: `EMP-000001`
  - Tenure Snapshot: `SNAP-EMP-000001-2024Q1`
  - Workload Snapshot: `WORK-EMP-000001-2024Q1`
  - Engagement Survey: `SURV-2024-000001`
  - Intervention: `INT-2026-000001`
  - Attrition Outcome: `OUT-EMP-000001-2026`

---

## 2. Folder Structure

```
Hackathon/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py               # Application settings & environment variables
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── session.py              # PostgreSQL engine & session factory
│   │   └── models/
│   │       ├── __init__.py             # Exports all 18 models for Alembic & ORM
│   │       ├── base.py                 # Declarative Base
│   │       ├── employee.py             # Employee (EMP-000001)
│   │       ├── role.py                 # Role (ROLE-IC3-SWE)
│   │       ├── team.py                 # Team (TEAM-ENG-01)
│   │       ├── team_membership.py      # Effective-dated TeamMembershipHistory
│   │       ├── tenure_snapshot.py      # Quarterly TenureSnapshot (SNAP-...)
│   │       ├── workload_snapshot.py    # Quarterly WorkloadSnapshot (WORK-...)
│   │       ├── engagement_survey.py    # Quarterly EngagementSurvey (SURV-...)
│   │       ├── compensation_band.py    # CompensationBand (BAND-IC3)
│   │       ├── promotion_history.py    # PromotionHistory (PROM-...)
│   │       ├── attrition_outcome.py    # AttritionOutcome (OUT-...) [Ground Truth]
│   │       ├── intervention.py         # Intervention (INT-...) [Human Touchpoints]
│   │       ├── intervention_event.py   # InterventionEvent (INTEV-...) [Audit Trail]
│   │       ├── app_user.py             # AppUser (USR-000001) [RBAC]
│   │       ├── audit_log.py            # AuditLog (AUD-...) [Traceability]
│   │       ├── validation.py           # ValidationRun & ValidationIssue
│   │       └── analysis.py             # AnalysisRun & SupportAssessment
│   ├── alembic/
│   │   ├── env.py                      # Alembic migration environment
│   │   ├── script.py.mako              # Revision script template
│   │   └── versions/
│   │       └── 001_initial_schema.py   # Complete initial schema migration (18 tables)
│   ├── scripts/
│   │   ├── check_db.py                 # Diagnostic script checking PostgreSQL connection
│   │   └── seed_synthetic_data.py      # Seeder for 10,000 employees (Seed: 20261022)
│   ├── tests/
│   │   ├── conftest.py                 # Pytest test fixtures
│   │   ├── test_primary_key_uniqueness.py
│   │   ├── test_foreign_key_relationships.py
│   │   ├── test_duplicate_records.py
│   │   ├── test_date_validation.py
│   │   ├── test_enum_validation.py
│   │   ├── test_employee_history_consistency.py
│   │   ├── test_attrition_outcome_consistency.py
│   │   └── test_historical_snapshot_preservation.py
│   ├── alembic.ini                     # Alembic configuration
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Environment variables template
├── docs/
│   ├── ER_DIAGRAM.md                   # Full Mermaid ER diagram of all 18 entities
│   ├── SCHEMA_DOCUMENTATION.md         # In-depth table & column specifications
│   └── data_dictionary.md              # Granular Data Dictionary
├── alembic.ini
├── pytest.ini
└── README.md
```

---

## 3. Local PostgreSQL Setup (Windows)

PostgreSQL 18 is installed locally at `C:\Program Files\PostgreSQL\18\`.

### Step 1: Start the PostgreSQL Windows Service
Open Windows **Command Prompt as Administrator** and execute:
```cmd
net start postgresql-x64-18
```
*(Alternatively: Press `Win + R`, type `services.msc`, find **postgresql-x64-18**, right-click and select **Start**).*

### Step 2: Create the Database
Open **Command Prompt** (or `psql` in pgAdmin) and create the database `retention_db`:
```cmd
"C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres retention_db
```
*(You will be prompted to enter your PostgreSQL password).*

### Step 3: Configure Environment Variables
Inside `backend/`, copy `.env.example` to `.env` and fill in your password:
```ini
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/retention_db
JWT_SECRET=dev-secret-key-change-in-production
GENERATOR_SEED=20261022
```

### Step 4: Verify Connection
Run the diagnostic script:
```cmd
python backend/scripts/check_db.py
```
If connected, it will print:
```
[SUCCESS] Successfully connected to the database!
Database Server Version: PostgreSQL 18.x...
```

---

## 4. Running Alembic Migrations

To apply the database schema to your local PostgreSQL database:

```cmd
python -m alembic upgrade head
```
This executes [`001_initial_schema.py`](file:///c:/CandidateWorkspace/Hackathon/backend/alembic/versions/001_initial_schema.py) and creates all 18 tables, indexes, and constraints.

To rollback the migration:
```cmd
python -m alembic downgrade base
```

---

## 5. Seeding Synthetic Data (10,000 Employees, 24 Months)

To generate and seed the full synthetic baseline dataset:
```cmd
python backend/scripts/seed_synthetic_data.py --scale 10000 --seed 20261022
```
*Seeding Features:*
- 10,000 Synthetic Employees (`EMP-000001`)
- 24 Months of history across 8 quarters (`2024Q1` through `2025Q4`)
- 80,000 Tenure Snapshots (`SNAP-...`)
- 80,000 Workload Snapshots (`WORK-...`) with benign release crunches and chronic strain
- 80,000 Engagement Surveys (`SURV-...`) with voluntary skips (~12% missingness handled neutrally)
- Effective-dated Team Membership transfers (`MEM-...`)
- 1,600 Promotion Histories (`PROM-...`)
- 10,000 Attrition Outcomes (`OUT-...`) with 9.5% voluntary attrition (ground truth isolated)
- Supportive 1-on-1 Interventions (`INT-...`) and chronological Event Logs (`INTEV-...`)
- 4 Role-Based App Users (`USR-...`) for RBAC testing

---

## 6. Running Database Tests

Run the full pytest suite (22 comprehensive database test cases):
```cmd
python -m pytest backend/tests/ -v
```

### Test Coverage Breakdown:
1. `test_primary_key_uniqueness.py`: Verifies primary key integrity across tables and ensures duplicates raise `IntegrityError`.
2. `test_foreign_key_relationships.py`: Validates foreign key constraints, cascading deletions, and ORM relationship navigation.
3. `test_duplicate_records.py`: Tests compound unique constraints (`uq_emp_tenure_quarter`, `uq_emp_workload_quarter`, `uq_emp_survey_quarter`).
4. `test_date_validation.py`: Tests chronological invariants (`effective_end_date >= effective_start_date`, snapshot dates after hire dates).
5. `test_enum_validation.py`: Verifies strict enum constraints (`status`, `movement_type`, `role`).
6. `test_employee_history_consistency.py`: Confirms salary/role updates do not mutate or overwrite historical snapshots.
7. `test_attrition_outcome_consistency.py`: Enforces 1:1 ground-truth cardinality and verifies zero leakage into snapshot queries.
8. `test_historical_snapshot_preservation.py`: Verifies 8-quarter coverage, workload hour bounds, and survey neutrality.

---

## 7. How to Verify the Database in pgAdmin 4

1. **Open pgAdmin 4**: Search for "pgAdmin 4" in the Windows Start menu and launch it.
2. **Connect to Server**:
   - In the left sidebar, double-click **Servers** > **PostgreSQL 18**.
   - Enter your master password when prompted.
3. **Inspect the Database**:
   - Expand **Databases** > **retention_db** > **Schemas** > **public** > **Tables**.
   - You will see all 18 tables:
     - `compensation_bands`
     - `roles`
     - `teams`
     - `employees`
     - `team_membership_history`
     - `tenure_snapshots`
     - `workload_snapshots`
     - `engagement_surveys`
     - `promotion_histories`
     - `attrition_outcomes`
     - `interventions`
     - `intervention_events`
     - `app_users`
     - `audit_logs`
     - `validation_runs`
     - `validation_issues`
     - `analysis_runs`
     - `support_assessments`
4. **Run Verification Queries**:
   - Right-click `retention_db` and select **Query Tool**.
   - Check table row counts:
     ```sql
     SELECT 
         'employees' AS table_name, COUNT(*) AS total_rows FROM employees
     UNION ALL
     SELECT 'tenure_snapshots', COUNT(*) FROM tenure_snapshots
     UNION ALL
     SELECT 'workload_snapshots', COUNT(*) FROM workload_snapshots
     UNION ALL
     SELECT 'engagement_surveys', COUNT(*) FROM engagement_surveys
     UNION ALL
     SELECT 'attrition_outcomes', COUNT(*) FROM attrition_outcomes;
     ```
   - Verify survey neutrality (no negative imputation for skipped surveys):
     ```sql
     SELECT survey_id, employee_id, is_missing, satisfaction_score 
     FROM engagement_surveys 
     WHERE is_missing = TRUE 
     LIMIT 5;
     ```
   - Verify effective-dated team membership history:
     ```sql
     SELECT membership_id, employee_id, team_id, effective_start_date, effective_end_date, is_current
     FROM team_membership_history
     ORDER BY employee_id, effective_start_date;
     ```
