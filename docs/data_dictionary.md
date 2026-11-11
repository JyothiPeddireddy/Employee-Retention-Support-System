# Data Dictionary: Supportive Retention Signal Engine

Comprehensive data dictionary specifying data types, constraints, allowed values, units, uniqueness, and validation rules for all 10 core entities plus the isolated anomaly ground truth table.

---

## 1. Master Tables

### `teams` (Organizational Units)
Represents departments, teams, or operational squads within the company.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `team_id` | VARCHAR(32) | Yes | Regex: `^TEAM-[A-Z]+-[0-9]{2}$` | ID | Primary Key | Must follow naming convention (e.g. `TEAM-ENG-01`). |
| `name` | VARCHAR(100) | Yes | String (3–100 chars) | Name | No | Non-empty alphanumeric string. |
| `department` | VARCHAR(100) | Yes | Enum: `Engineering`, `Product`, `Design`, `Operations`, `Sales`, `Human Resources` | Category | No | Must be one of the recognized company departments. |
| `created_at` | TIMESTAMP | Yes | Valid ISO datetime | UTC | No | Defaults to current timestamp. |

---

### `compensation_bands` (Salary Benchmarking)
Governs salary ranges and market benchmarks for job levels.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `band_id` | VARCHAR(32) | Yes | Regex: `^BAND-[A-Z0-9]+$` | ID | Primary Key | Must follow band convention (e.g. `BAND-IC3`). |
| `name` | VARCHAR(100) | Yes | String | Name | No | Non-empty descriptive band tier name. |
| `min_salary` | NUMERIC(12,2)| Yes | `40000.00` to `500000.00` | USD | No | Must be strictly > 0. |
| `mid_salary` | NUMERIC(12,2)| Yes | `50000.00` to `600000.00` | USD | No | Must satisfy: `min_salary <= mid_salary`. |
| `max_salary` | NUMERIC(12,2)| Yes | `60000.00` to `800000.00` | USD | No | Must satisfy: `mid_salary <= max_salary`. |
| `currency` | VARCHAR(3) | Yes | `USD`, `EUR`, `GBP` | ISO 4217 | No | Defaults to `USD`. |

---

### `roles` (Job Titles & Hierarchy)
Defines employee roles and levels across engineering, product, and leadership tracks.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `role_id` | VARCHAR(32) | Yes | Regex: `^ROLE-[A-Z0-9\-]+$` | ID | Primary Key | Must follow naming convention (e.g. `ROLE-IC3-SWE`). |
| `title` | VARCHAR(100) | Yes | String | Title | No | Non-empty role title. |
| `level` | VARCHAR(20) | Yes | Enum: `IC1`..`IC6`, `M1`..`M3` | Level | No | Must be a recognized job level code. |
| `band_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | Must reference a valid `compensation_bands.band_id`. |

---

### `employees` (Master Profile)
Core profile for active and historical employees. Excludes protected sensitive attributes and proxies.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `employee_id` | VARCHAR(32) | Yes | Regex: `^EMP-[0-9]{6}$` | ID | Primary Key | Immutable, zero-padded 6-digit identifier (e.g. `EMP-000001`). |
| `full_name` | VARCHAR(120) | Yes | Synthetic Name string | Name | No | Synthetic name (no real PII). |
| `email` | VARCHAR(160) | Yes | Valid email format | Email | Unique | Must follow `{first}.{last}.{id}@example.com`. |
| `team_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References valid `teams.team_id`. |
| `role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References valid `roles.role_id`. |
| `manager_id` | VARCHAR(32) | Optional | Foreign Key (Self) | ID | No | References valid `employees.employee_id`. Top directors have `NULL`. |
| `hire_date` | DATE | Yes | Between `2018-01-01` and `2024-01-01` | Date | No | Must precede all snapshot and event dates. |
| `current_salary`| NUMERIC(12,2)| Yes | Within role's compensation band | USD | No | Must fall within assigned `compensation_bands` range. |
| `status` | VARCHAR(20) | Yes | Enum: `ACTIVE`, `LEAVE`, `ATTRITED` | Status | No | Invariant: `ATTRITED` requires matching outcome record. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Audit creation timestamp. |

---

## 2. Longitudinal Snapshot & Event Tables

### `tenure_snapshots` (Quarterly Career Checkpoints)
Longitudinal tracking of employee tenure and time-in-role over the 24-month horizon.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `snapshot_id` | VARCHAR(64) | Yes | Regex: `^SNAP-EMP-[0-9]{6}-[0-9]{4}Q[1-4]$` | ID | Primary Key | Deterministic format: `SNAP-<emp_id>-<quarter>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `snapshot_quarter`| VARCHAR(10)| Yes | Enum: `2024Q1` through `2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `snapshot_date` | DATE | Yes | Quarter-end dates | Date | No | Must be `>= employee.hire_date`. |
| `tenure_months` | INT | Yes | `1` to `120` | Months | No | Derived: `floor((snapshot_date - hire_date) / 30.44)`. |
| `role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `team_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `teams.team_id`. |
| `months_in_current_role`| INT | Yes | `0` to `120` | Months | No | Resets to 0 upon internal promotion or transfer. |

---

### `workload_snapshots` (Quarterly Workload & Overtime Signals)
Measures weekly hours, overtime streaks, and project concurrency.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `workload_id` | VARCHAR(64) | Yes | Regex: `^WORK-EMP-[0-9]{6}-[0-9]{4}Q[1-4]$` | ID | Primary Key | Deterministic ID format. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `period_quarter` | VARCHAR(10)| Yes | `2024Q1` through `2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `period_date` | DATE | Yes | Quarter-end dates | Date | No | Pre-outcome cutoff enforced. |
| `avg_weekly_hours`| NUMERIC(5,2)| Yes | `0.00` to `120.00` | Hours/wk | No | Values >= 95.0 flagged as potential data leakage proxy. |
| `overtime_hours` | NUMERIC(5,2)| Yes | `>= 0.00` | Hours/wk | No | Derived: `max(0.00, avg_weekly_hours - 40.00)`. |
| `consecutive_overtime_weeks`| INT | Yes | `0` to `12` | Weeks | No | Sustained streak over 6 weeks flags high strain. |
| `active_project_count`| INT | Yes | `1` to `8` | Count | No | Measures project context switching overhead. |
| `is_benign_surge`| BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Indicates planned launch surge; prevents false positive. |

---

### `engagement_surveys` (Quarterly Voluntary Pulse Surveys)
Captures voluntary employee sentiment on a 1.00 to 5.00 Likert scale.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `survey_id` | VARCHAR(64) | Yes | Regex: `^SURV-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `SURV-2024-000001`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `survey_quarter`| VARCHAR(10)| Yes | `2024Q1` through `2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `survey_date` | DATE | Yes | Quarter-end dates | Date | No | Survey submission timestamp. |
| `is_missing` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Indicates voluntary skip (~12% baseline). |
| `satisfaction_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | Invariant: If `is_missing=TRUE`, MUST BE `NULL`. |
| `work_life_balance_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `career_growth_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `manager_support_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `composite_engagement`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Mean | No | Derived arithmetic mean of the 4 dimension scores. |

---

### `promotion_histories` (Internal Mobility & Velocity)
Records lateral job transfers and promotions.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `promotion_id` | VARCHAR(64) | Yes | Regex: `^PROM-EMP-[0-9]{6}-[0-9]{4}$` | ID | Primary Key | Deterministic format: `PROM-<emp_id>-<count>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `effective_date`| DATE | Yes | Date | Date | No | Event effective date. |
| `from_role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `to_role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `from_salary` | NUMERIC(12,2)| Yes | Salary | USD | No | Base salary prior to change. |
| `to_salary` | NUMERIC(12,2)| Yes | Salary | USD | No | Base salary after change (`to_salary >= from_salary`). |
| `movement_type` | VARCHAR(20) | Yes | Enum: `PROMOTION`, `LATERAL_TRANSFER` | Type | No | Valid mobility classification. |

---

## 3. Horizon Outcomes & Interventions

### `attrition_outcomes` (Post-Observation Ground Truth)
Future horizon labels (5–15% voluntary attrition rate). Strictly guarded by pre-outcome cutoff.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `outcome_id` | VARCHAR(64) | Yes | Regex: `^OUT-EMP-[0-9]{6}-[0-9]{4}$` | ID | Primary Key | Format: `OUT-EMP-000001-2026`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Unique (1:1) | References `employees.employee_id`. |
| `attrition_date`| DATE | Optional | `2026-01-01` to `2026-06-30` | Date | No | `NULL` for retained active employees. |
| `voluntary` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Voluntary attrition tracking. |
| `primary_reason`| VARCHAR(100)| Optional | Enum: `BURNOUT`, `CAREER_GROWTH`, `COMPENSATION`, `BETTER_OPPORTUNITY` | Reason | No | Stated reason from simulated exit conversation. |
| `horizon_period`| VARCHAR(20) | Yes | `2026-H1` | Period | No | Target future evaluation window. |

---

### `interventions` (Human-in-the-Loop Supportive Actions)
Auditable record of manager 1-on-1 retention touchpoints and workload rebalancing.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `intervention_id`| VARCHAR(64) | Yes | Regex: `^INT-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `INT-2026-000001`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `conducted_by_id`| VARCHAR(32)| Yes | Foreign Key | ID | No | References manager or HR partner `employee_id`. |
| `intervention_date`| DATE | Yes | Valid date | Date | No | Date when 1-on-1 occurred. |
| `intervention_type`| VARCHAR(50)| Yes | Enum: `1_ON_1_CAREER_CHECKIN`, `WORKLOAD_REBALANCING`, `COMPENSATION_REVIEW`, `MENTORSHIP_ALIGNMENT` | Type | No | Standardized supportive action category. |
| `discussion_summary`| TEXT | Yes | Text (min 10 chars) | Notes | No | Must contain human review notes. Rejects automated triggers without explanation. |
| `agreed_actions`| TEXT | Optional | Action plan text | Text | No | Follow-up action items. |
| `follow_up_date`| DATE | Optional | Date | Date | No | Scheduled check-in date. |
| `status` | VARCHAR(20) | Yes | Enum: `SCHEDULED`, `COMPLETED`, `CANCELLED` | Status | No | Defaults to `SCHEDULED`. |
| `simulated_outcome`| VARCHAR(50)| Optional | Enum: `RETENTION_REINFORCED`, `STILL_AT_RISK` | Outcome | No | Outcome tracking. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Creation timestamp. |

---

## 4. Isolated Anomaly Ground Truth

### `ground_truth_anomalies` (Negative Scenario Ground Truth)
Kept strictly isolated from model training/scoring features to audit validation detectors.

| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `anomaly_id` | VARCHAR(64) | Yes | Regex: `^ANOM-[0-9]{6}$` | ID | Primary Key | Format: `ANOM-000001`. |
| `record_id` | VARCHAR(64) | Yes | Foreign record ID | ID | No | Identifier of the affected record. |
| `table_name` | VARCHAR(64) | Yes | Table name | Name | No | Name of affected table. |
| `issue_type` | VARCHAR(80) | Yes | Enum: `FUTURE_INFO_LEAK`, `MISSING_SURVEY_PUNITIVE`, `OUTCOME_DATE_MISMATCH`, `UNEXPLAINED_SCORE` | Anomaly | No | Classification of the edge case. |
| `description` | TEXT | Yes | Detailed description | Text | No | Explains what deliberate edge case was injected. |
| `expected_validation_error`| TEXT | Yes | Expected error message | Text | No | The exact validation check expected to catch this anomaly. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Injection timestamp. |
