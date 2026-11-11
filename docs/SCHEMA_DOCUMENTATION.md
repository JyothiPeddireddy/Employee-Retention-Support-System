# Database Schema Documentation
## Employee Retention Support System (Phase 1 Database Architecture)

This document provides complete technical specifications for the relational database schema implemented in SQLAlchemy and Alembic, targeting PostgreSQL 18.

---

## 1. Architectural Highlights

1. **Temporal & Longitudinal Integrity**:
   - Employee records, team memberships, and tenure are effective-dated and snapshot-driven.
   - Historical snapshots are immutable event records; updating current salary or role never overwrites historical quarters.
2. **Strict Pre-Outcome Temporal Barrier**:
   - `attrition_outcomes` is isolated from feature extraction queries.
   - Every snapshot date occurs strictly on or before the observation cutoff date.
3. **Survey Neutrality**:
   - `engagement_surveys` enforces via database constraint (`chk_survey_neutrality`) that voluntary non-responses (`is_missing = TRUE`) strictly store `NULL` for sentiment scores. A missing survey is never punitively imputed as negative.
4. **Duplicate Prevention**:
   - Compound unique constraints (`uq_emp_tenure_quarter`, `uq_emp_workload_quarter`, `uq_emp_survey_quarter`) prevent duplicate quarterly entries per employee.
5. **Effective-Dated Team Membership**:
   - `team_membership_history` supports transitions across teams and roles with `effective_start_date` and `effective_end_date` (`NULL` indicates current assignment).

---

## 2. Table Specifications

### A. Master Reference Tables

#### `compensation_bands`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `band_id` | VARCHAR(32) | No | PRIMARY KEY | Unique band code (e.g., `BAND-IC3`) |
| `name` | VARCHAR(100) | No | — | Descriptive band name (e.g., Senior) |
| `min_salary` | NUMERIC(12,2) | No | — | Lower bound of salary range |
| `mid_salary` | NUMERIC(12,2) | No | — | Market midpoint |
| `max_salary` | NUMERIC(12,2) | No | — | Upper bound of salary range |
| `currency` | VARCHAR(3) | No | DEFAULT 'USD' | ISO currency code |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_salary_order`: `CHECK (min_salary <= mid_salary AND mid_salary <= max_salary)`

#### `roles`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `role_id` | VARCHAR(32) | No | PRIMARY KEY | Unique role ID (e.g., `ROLE-IC3-SWE`) |
| `title` | VARCHAR(100) | No | — | Full title (e.g., Senior Software Engineer) |
| `level` | VARCHAR(20) | No | — | Level code (IC1–IC6, M1–M3) |
| `band_id` | VARCHAR(32) | No | FK -> `compensation_bands.band_id` | Associated compensation band |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Indexes**: `idx_roles_band (band_id)`, `idx_roles_level (level)`

#### `teams`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `team_id` | VARCHAR(32) | No | PRIMARY KEY | Unique team ID (e.g., `TEAM-ENG-01`) |
| `name` | VARCHAR(100) | No | — | Team display name |
| `department` | VARCHAR(100) | No | — | Department (Engineering, Product, etc.) |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Indexes**: `idx_teams_dept (department)`

---

### B. Core Workforce & History Tables

#### `employees`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `employee_id` | VARCHAR(32) | No | PRIMARY KEY | Deterministic ID (`EMP-000001`) |
| `first_name` | VARCHAR(60) | No | — | Synthetic first name |
| `last_name` | VARCHAR(60) | No | — | Synthetic last name |
| `email` | VARCHAR(160) | No | UNIQUE | Synthetic corporate email |
| `hire_date` | DATE | No | — | Start date with organization |
| `current_role_id`| VARCHAR(32) | No | FK -> `roles.role_id` | Current job role |
| `current_team_id`| VARCHAR(32) | No | FK -> `teams.team_id` | Current team assignment |
| `current_salary` | NUMERIC(12,2) | No | — | Current base annual compensation |
| `manager_id` | VARCHAR(32) | Yes | FK -> `employees.employee_id` | Reporting line manager |
| `status` | VARCHAR(20) | No | DEFAULT 'ACTIVE' | Employment status |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit creation |
| `updated_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit update |
* **Table Constraints**:
  - `chk_employee_status`: `CHECK (status IN ('ACTIVE', 'LEAVE', 'ATTRITED'))`
* **Indexes**: `idx_employees_team`, `idx_employees_role`, `idx_employees_manager`, `idx_employees_status`

#### `team_membership_history`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `membership_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `MEM-<emp>-<seq>` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Assigned employee |
| `team_id` | VARCHAR(32) | No | FK -> `teams.team_id` | Assigned team |
| `role_id` | VARCHAR(32) | No | FK -> `roles.role_id` | Role held during assignment |
| `effective_start_date` | DATE | No | — | Assignment start date |
| `effective_end_date` | DATE | Yes | — | Assignment end date (`NULL` = active) |
| `is_current` | BOOLEAN | No | DEFAULT TRUE | Active assignment flag |
| `transfer_reason` | VARCHAR(50) | No | DEFAULT 'HIRE' | HIRE, INTERNAL_TRANSFER, PROMOTION |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_membership_dates`: `CHECK (effective_end_date IS NULL OR effective_end_date >= effective_start_date)`
* **Indexes**: `idx_membership_emp`, `idx_membership_team`, `idx_membership_active`

#### `tenure_snapshots`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `snapshot_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `SNAP-<emp>-<quarter>` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Snapshot employee |
| `snapshot_quarter` | VARCHAR(10) | No | — | Quarter label (`2024Q1`..`2025Q4`) |
| `snapshot_date` | DATE | No | — | Quarter end boundary date |
| `tenure_months` | INTEGER | No | — | Total tenure with company |
| `role_id` | VARCHAR(32) | No | FK -> `roles.role_id` | Role at snapshot date |
| `team_id` | VARCHAR(32) | No | FK -> `teams.team_id` | Team at snapshot date |
| `months_in_current_role`| INTEGER | No | — | Months in role (resets on movement) |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `uq_emp_tenure_quarter`: `UNIQUE (employee_id, snapshot_quarter)`
* **Indexes**: `idx_tenure_emp_quarter`, `idx_tenure_date`

#### `workload_snapshots`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `workload_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `WORK-<emp>-<quarter>` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Snapshot employee |
| `period_quarter` | VARCHAR(10) | No | — | Quarter label |
| `period_date` | DATE | No | — | Quarter end boundary date |
| `avg_weekly_hours` | NUMERIC(5,2)| No | — | Average weekly working hours |
| `overtime_hours` | NUMERIC(5,2)| No | DEFAULT 0.0 | Hours worked above 40.0 |
| `consecutive_overtime_weeks`| INT | No | DEFAULT 0 | Overtime streak length |
| `active_project_count` | INT | No | DEFAULT 1 | Concurrent project assignments |
| `is_benign_surge`| BOOLEAN | No | DEFAULT FALSE | Known release crunch period |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_weekly_hours`: `CHECK (avg_weekly_hours >= 0.0 AND avg_weekly_hours <= 120.0)`
  - `uq_emp_workload_quarter`: `UNIQUE (employee_id, period_quarter)`
* **Indexes**: `idx_workload_emp_quarter`, `idx_workload_date`

#### `engagement_surveys`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `survey_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `SURV-2024-000001` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Surveyed employee |
| `survey_quarter` | VARCHAR(10) | No | — | Pulse survey quarter |
| `survey_date` | DATE | No | — | Submission date |
| `is_missing` | BOOLEAN | No | DEFAULT FALSE | Voluntary survey skip |
| `satisfaction_score` | NUMERIC(3,2)| Yes | — | Likert score 1.00 to 5.00 |
| `work_life_balance_score`| NUMERIC(3,2)| Yes | — | Likert score 1.00 to 5.00 |
| `career_growth_score` | NUMERIC(3,2)| Yes | — | Likert score 1.00 to 5.00 |
| `manager_support_score` | NUMERIC(3,2)| Yes | — | Likert score 1.00 to 5.00 |
| `composite_engagement` | NUMERIC(3,2)| Yes | — | Arithmetic mean of Likert scores |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_survey_neutrality`: `CHECK ((is_missing = TRUE AND satisfaction_score IS NULL) OR (is_missing = FALSE AND satisfaction_score BETWEEN 1.00 AND 5.00))`
  - `uq_emp_survey_quarter`: `UNIQUE (employee_id, survey_quarter)`
* **Indexes**: `idx_survey_emp_quarter`, `idx_survey_date`

#### `promotion_histories`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `promotion_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `PROM-<emp>-<seq>` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Employee promoted/moved |
| `effective_date` | DATE | No | — | Promotion effective date |
| `from_role_id` | VARCHAR(32) | No | FK -> `roles.role_id` | Role before movement |
| `to_role_id` | VARCHAR(32) | No | FK -> `roles.role_id` | Role after movement |
| `from_salary` | NUMERIC(12,2)| No | — | Salary before movement |
| `to_salary` | NUMERIC(12,2)| No | — | Salary after movement |
| `movement_type` | VARCHAR(20) | No | — | PROMOTION, LATERAL_TRANSFER |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_movement_type`: `CHECK (movement_type IN ('PROMOTION', 'LATERAL_TRANSFER'))`
* **Indexes**: `idx_promo_emp`, `idx_promo_date`

---

### C. Ground Truth & Supportive Interventions

#### `attrition_outcomes`
*Note: Post-horizon ground truth table. Inaccessible to predictive feature generation.*
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `outcome_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `OUT-<emp>-2026` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (1:1 UNIQUE) | Unique employee |
| `attrition_date` | DATE | Yes | — | Termination date (`NULL` if retained) |
| `voluntary` | BOOLEAN | No | DEFAULT TRUE | Voluntary vs involuntary |
| `primary_reason` | VARCHAR(100) | Yes | — | BURNOUT, CAREER_GROWTH, etc. |
| `horizon_period` | VARCHAR(20) | No | — | Evaluation horizon (`2026-H1`) |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit timestamp |
* **Table Constraints**:
  - `chk_attrition_reason`: `CHECK (primary_reason IS NULL OR primary_reason IN ('BURNOUT', 'CAREER_GROWTH', 'COMPENSATION', 'BETTER_OPPORTUNITY', 'RELOCATION', 'OTHER'))`
* **Indexes**: `idx_outcome_emp`, `idx_outcome_date`

#### `interventions`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `intervention_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `INT-2026-000001` |
| `employee_id` | VARCHAR(32) | No | FK -> `employees.employee_id` (CASCADE) | Employee supported |
| `conducted_by_id` | VARCHAR(32) | No | FK -> `employees.employee_id` | Manager or HR partner |
| `intervention_date` | DATE | No | — | Date 1-on-1 held |
| `intervention_type` | VARCHAR(50) | No | — | 1_ON_1_CAREER_CHECKIN, etc. |
| `discussion_summary`| TEXT | No | — | Required human discussion notes |
| `agreed_actions` | TEXT | Yes | — | Action plan agreed upon |
| `follow_up_date` | DATE | Yes | — | Next check-in date |
| `status` | VARCHAR(20) | No | DEFAULT 'SCHEDULED' | SCHEDULED, COMPLETED, CANCELLED |
| `simulated_outcome` | VARCHAR(50) | Yes | — | RETENTION_REINFORCED, etc. |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Audit creation |
* **Table Constraints**:
  - `chk_intervention_status`: `CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED'))`
* **Indexes**: `idx_intervention_emp`, `idx_intervention_conductor`, `idx_intervention_date`

#### `intervention_events`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `INTEV-2026-000001` |
| `intervention_id` | VARCHAR(64) | No | FK -> `interventions.intervention_id` (CASCADE) | Parent touchpoint |
| `event_type` | VARCHAR(50) | No | — | CREATED, NOTES_UPDATED, etc. |
| `event_timestamp` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Event instant |
| `actor_id` | VARCHAR(32) | No | FK -> `employees.employee_id` | User triggering action |
| `notes` | TEXT | Yes | — | Context notes |
* **Table Constraints**:
  - `chk_event_type`: `CHECK (event_type IN ('CREATED', 'NOTES_UPDATED', 'ACTION_COMPLETED', 'FOLLOW_UP_SCHEDULED', 'CANCELLED'))`
* **Indexes**: `idx_intev_intervention`, `idx_intev_timestamp`

---

### D. Governance, Security & Audit Tables

#### `app_users`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | VARCHAR(32) | No | PRIMARY KEY | Format: `USR-000001` |
| `username` | VARCHAR(80) | No | UNIQUE | System login name |
| `email` | VARCHAR(160) | No | UNIQUE | System login email |
| `hashed_password` | VARCHAR(255) | No | — | Bcrypt / PBKDF2 hash |
| `role` | VARCHAR(30) | No | DEFAULT 'HR_PARTNER' | HR_PARTNER, MANAGER, SYSTEM_ADMIN, AUDITOR |
| `employee_id` | VARCHAR(32) | Yes | FK -> `employees.employee_id` | Optional linked workforce profile |
| `is_active` | BOOLEAN | No | DEFAULT TRUE | Active flag |
| `created_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Update timestamp |
* **Table Constraints**:
  - `chk_user_role`: `CHECK (role IN ('HR_PARTNER', 'MANAGER', 'SYSTEM_ADMIN', 'AUDITOR'))`
* **Indexes**: `idx_users_role`

#### `audit_logs`
| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `log_id` | VARCHAR(64) | No | PRIMARY KEY | Format: `AUD-2026-000001` |
| `entity_name` | VARCHAR(80) | No | — | Target entity (e.g., `employees`) |
| `entity_id` | VARCHAR(64) | No | — | Target record ID |
| `action` | VARCHAR(30) | No | — | INSERT, UPDATE, DELETE, REVIEW |
| `performed_by` | VARCHAR(64) | No | — | User or actor ID |
| `timestamp` | TIMESTAMP | No | DEFAULT CURRENT_TIMESTAMP | Event timestamp |
| `changes_json` | TEXT | Yes | — | JSON before/after state |
| `ip_address` | VARCHAR(45) | Yes | — | Client IPv4/IPv6 |
* **Indexes**: `idx_audit_entity (entity_name, entity_id)`, `idx_audit_timestamp`, `idx_audit_actor`

---

### E. Supporting Pipeline Tables

#### `validation_runs` & `validation_issues`
- Record automated database tests, data quality audits, and tracking of the 4 injected negative scenarios (`FUTURE_INFO_LEAK`, `MISSING_SURVEY_PUNITIVE`, `OUTCOME_DATE_MISMATCH`, `UNEXPLAINED_SCORE`).

#### `analysis_runs` & `support_assessments`
- Store longitudinal prioritization runs, computed dimension scores (Workload Strain, Career Stagnation, Engagement Trajectory), explainability chips (`factors_json`), and recommended 1-on-1 agenda items.
