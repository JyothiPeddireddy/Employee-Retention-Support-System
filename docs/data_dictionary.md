# Data Dictionary: Employee Retention Support System

Comprehensive technical data dictionary covering all **18 database entities** (14 Core Domain Entities + 4 Supporting Entities).

---

## 1. Master & Organizational Data

### `compensation_bands`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `band_id` | VARCHAR(32) | Yes | Regex: `^BAND-[A-Z0-9]+$` | Code | Primary Key | Immutable ID (e.g. `BAND-IC3`). |
| `name` | VARCHAR(100) | Yes | Non-empty string | Name | No | Descriptive title. |
| `min_salary` | NUMERIC(12,2)| Yes | `40000.00` to `500000.00` | USD | No | Min salary > 0. |
| `mid_salary` | NUMERIC(12,2)| Yes | `50000.00` to `600000.00` | USD | No | Invariant: `min_salary <= mid_salary`. |
| `max_salary` | NUMERIC(12,2)| Yes | `60000.00` to `800000.00` | USD | No | Invariant: `mid_salary <= max_salary`. |
| `currency` | VARCHAR(3) | Yes | `USD`, `EUR`, `GBP` | ISO 4217 | No | Defaults to `USD`. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `roles`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `role_id` | VARCHAR(32) | Yes | Regex: `^ROLE-[A-Z0-9\-]+$` | Code | Primary Key | Format: `ROLE-IC3-SWE`. |
| `title` | VARCHAR(100) | Yes | String | Title | No | Non-empty role title. |
| `level` | VARCHAR(20) | Yes | Enum: `IC1`..`IC6`, `M1`..`M3` | Code | No | Standard job ladder level. |
| `band_id` | VARCHAR(32) | Yes | Foreign Key | Code | No | References valid `compensation_bands.band_id`. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `teams`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `team_id` | VARCHAR(32) | Yes | Regex: `^TEAM-[A-Z]+-[0-9]{2}$` | Code | Primary Key | Format: `TEAM-ENG-01`. |
| `name` | VARCHAR(100) | Yes | String | Name | No | Department / team name. |
| `department` | VARCHAR(100) | Yes | Enum: `Engineering`, `Product`, `Design`, `Operations`, `Sales`, `Human Resources` | Dept | No | Recognized department. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

---

## 2. Core Workforce & Longitudinal Snapshots

### `employees`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `employee_id` | VARCHAR(32) | Yes | Regex: `^EMP-[0-9]{6}$` | ID | Primary Key | Immutable zero-padded ID (`EMP-000001`). |
| `first_name` | VARCHAR(60) | Yes | Alphanumeric | Name | No | Synthetic first name. |
| `last_name` | VARCHAR(60) | Yes | Alphanumeric | Name | No | Synthetic last name. |
| `email` | VARCHAR(160) | Yes | Email format | Email | Unique | Format: `{first}.{last}.{id}@example.com`. |
| `hire_date` | DATE | Yes | Historical date | Date | No | Must precede all snapshot and event dates. |
| `current_role_id`| VARCHAR(32)| Yes | Foreign Key | ID | No | References valid `roles.role_id`. |
| `current_team_id`| VARCHAR(32)| Yes | Foreign Key | ID | No | References valid `teams.team_id`. |
| `current_salary` | NUMERIC(12,2)| Yes | Salary within band | USD | No | Fall within assigned band. |
| `manager_id` | VARCHAR(32) | Optional | Foreign Key (Self) | ID | No | References valid `employees.employee_id`. |
| `status` | VARCHAR(20) | Yes | Enum: `ACTIVE`, `LEAVE`, `ATTRITED` | Status | No | Invariant: `status IN ('ACTIVE', 'LEAVE', 'ATTRITED')`. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Creation timestamp. |
| `updated_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Updated timestamp. |

### `team_membership_history`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `membership_id`| VARCHAR(64) | Yes | Regex: `^MEM-EMP-[0-9]{6}-[0-9]{4}$` | ID | Primary Key | Format: `MEM-<emp_id>-<seq>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `team_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `teams.team_id`. |
| `role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `effective_start_date`| DATE | Yes | Date | Date | No | Start of team assignment. |
| `effective_end_date` | DATE | Optional | Date | Date | No | Invariant: `effective_end_date IS NULL OR effective_end_date >= effective_start_date`. |
| `is_current` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | `TRUE` if currently active assignment. |
| `transfer_reason`| VARCHAR(50)| Yes | Enum: `HIRE`, `INTERNAL_TRANSFER`, `PROMOTION`, `REORGANIZATION` | Reason | No | Audit classification of mobility event. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Timestamp. |

### `tenure_snapshots`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `snapshot_id` | VARCHAR(64) | Yes | Regex: `^SNAP-EMP-[0-9]{6}-[0-9]{4}Q[1-4]$` | ID | Primary Key | Format: `SNAP-<emp_id>-<quarter>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `snapshot_quarter`| VARCHAR(10)| Yes | Enum: `2024Q1`..`2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `snapshot_date` | DATE | Yes | Quarter-end date | Date | No | Must be `>= employee.hire_date`. |
| `tenure_months` | INTEGER | Yes | `>= 1` | Months | No | Derived total tenure with company. |
| `role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `team_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `teams.team_id`. |
| `months_in_current_role`| INTEGER| Yes | `>= 0` | Months | No | Resets to 0 upon role/team promotion. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `workload_snapshots`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `workload_id` | VARCHAR(64) | Yes | Regex: `^WORK-EMP-[0-9]{6}-[0-9]{4}Q[1-4]$` | ID | Primary Key | Format: `WORK-<emp_id>-<quarter>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `period_quarter` | VARCHAR(10)| Yes | Enum: `2024Q1`..`2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `period_date` | DATE | Yes | Quarter-end date | Date | No | Strict pre-outcome date. |
| `avg_weekly_hours`| NUMERIC(5,2)| Yes | `0.00` to `120.00` | Hours/wk | No | Invariant: `avg_weekly_hours BETWEEN 0.0 AND 120.0`. |
| `overtime_hours` | NUMERIC(5,2)| Yes | `>= 0.0` | Hours/wk | No | Derived: `max(0.0, avg_weekly_hours - 40.0)`. |
| `consecutive_overtime_weeks`| INT | Yes | `0` to `12` | Weeks | No | Sustained consecutive overtime. |
| `active_project_count`| INT | Yes | `1` to `8` | Count | No | Measures context switching. |
| `is_benign_surge`| BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Indicates planned launch crunch. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `engagement_surveys`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `survey_id` | VARCHAR(64) | Yes | Regex: `^SURV-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `SURV-2024-000001`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Compound UQ | References `employees.employee_id`. |
| `survey_quarter`| VARCHAR(10)| Yes | Enum: `2024Q1`..`2025Q4` | Quarter | Compound UQ | Unique per (employee, quarter). |
| `survey_date` | DATE | Yes | Quarter-end date | Date | No | Survey submission date. |
| `is_missing` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Indicates voluntary skip. |
| `satisfaction_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | Invariant: If `is_missing=TRUE`, MUST BE `NULL`. |
| `work_life_balance_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `career_growth_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `manager_support_score`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Likert | No | If `is_missing=TRUE`, MUST BE `NULL`. |
| `composite_engagement`| NUMERIC(3,2)| Optional | `1.00` to `5.00` | Mean | No | Arithmetic mean of Likert scores. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `promotion_histories`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `promotion_id` | VARCHAR(64) | Yes | Regex: `^PROM-EMP-[0-9]{6}-[0-9]{4}$` | ID | Primary Key | Format: `PROM-<emp_id>-<seq>`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `effective_date`| DATE | Yes | Date | Date | No | Movement date. |
| `from_role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `to_role_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `roles.role_id`. |
| `from_salary` | NUMERIC(12,2)| Yes | Base salary | USD | No | Pre-movement salary. |
| `to_salary` | NUMERIC(12,2)| Yes | Base salary | USD | No | Invariant: `to_salary >= from_salary`. |
| `movement_type` | VARCHAR(20) | Yes | Enum: `PROMOTION`, `LATERAL_TRANSFER` | Type | No | Valid movement classification. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

---

## 3. Horizon Ground Truth & Supportive Interventions

### `attrition_outcomes`
*Note: Post-horizon ground truth table. Inaccessible to predictive feature generation.*
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `outcome_id` | VARCHAR(64) | Yes | Regex: `^OUT-EMP-[0-9]{6}-[0-9]{4}$` | ID | Primary Key | Format: `OUT-<emp_id>-2026`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | Unique (1:1) | Strictly one outcome per employee. |
| `attrition_date`| DATE | Optional | Date in 2026 | Date | No | `NULL` for retained active employees. |
| `voluntary` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Voluntary attrition tracking. |
| `primary_reason`| VARCHAR(100)| Optional | Enum: `BURNOUT`, `CAREER_GROWTH`, `COMPENSATION`, `BETTER_OPPORTUNITY` | Reason | No | Reason code. |
| `horizon_period`| VARCHAR(20) | Yes | `2026-H1` | Period | No | Evaluation window. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `interventions`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `intervention_id`| VARCHAR(64)| Yes | Regex: `^INT-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `INT-2026-000001`. |
| `employee_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `conducted_by_id`| VARCHAR(32)| Yes | Foreign Key | ID | No | References manager or HR partner. |
| `intervention_date`| DATE | Yes | Date | Date | No | Touchpoint date. |
| `intervention_type`| VARCHAR(50)| Yes | Enum: `1_ON_1_CAREER_CHECKIN`, `WORKLOAD_REBALANCING`, `COMPENSATION_REVIEW`, `MENTORSHIP_ALIGNMENT` | Type | No | Standardized action category. |
| `discussion_summary`| TEXT | Yes | Text (min 10 chars) | Text | No | Required human discussion notes. Rejects automated triggers without explanation. |
| `agreed_actions`| TEXT | Optional | Action plan text | Text | No | Follow-up action items. |
| `follow_up_date`| DATE | Optional | Date | Date | No | Scheduled check-in date. |
| `status` | VARCHAR(20) | Yes | Enum: `SCHEDULED`, `COMPLETED`, `CANCELLED` | Status | No | Defaults to `SCHEDULED`. |
| `simulated_outcome`| VARCHAR(50)| Optional | Enum: `RETENTION_REINFORCED`, `STILL_AT_RISK` | Outcome | No | Outcome tracking. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Defaults to current timestamp. |

### `intervention_events`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | VARCHAR(64) | Yes | Regex: `^INTEV-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `INTEV-2026-000001`. |
| `intervention_id`| VARCHAR(64)| Yes | Foreign Key | ID | No | References `interventions.intervention_id`. |
| `event_type` | VARCHAR(50) | Yes | Enum: `CREATED`, `NOTES_UPDATED`, `ACTION_COMPLETED`, `FOLLOW_UP_SCHEDULED`, `CANCELLED` | Event | No | Lifecycle event classification. |
| `event_timestamp`| TIMESTAMP | Yes | ISO datetime | UTC | No | Event instant. |
| `actor_id` | VARCHAR(32) | Yes | Foreign Key | ID | No | References `employees.employee_id`. |
| `notes` | TEXT | Optional | Free text | Text | No | Audit commentary. |

---

## 4. Governance, Security & Audit

### `app_users`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | VARCHAR(32) | Yes | Regex: `^USR-[0-9]{6}$` | ID | Primary Key | Format: `USR-000001`. |
| `username` | VARCHAR(80) | Yes | Alphanumeric | Login | Unique | Unique login identifier. |
| `email` | VARCHAR(160) | Yes | Email format | Email | Unique | Unique corporate email. |
| `hashed_password`| VARCHAR(255)| Yes | Bcrypt hash | Hash | No | Password hash string. |
| `role` | VARCHAR(30) | Yes | Enum: `HR_PARTNER`, `MANAGER`, `SYSTEM_ADMIN`, `AUDITOR` | Role | No | RBAC permission role. |
| `employee_id` | VARCHAR(32) | Optional | Foreign Key | ID | No | Optional linked `employees.employee_id`. |
| `is_active` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | No | Account status. |
| `created_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Creation timestamp. |
| `updated_at` | TIMESTAMP | Yes | ISO datetime | UTC | No | Update timestamp. |

### `audit_logs`
| Field Name | Type | Required | Allowed Values | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `log_id` | VARCHAR(64) | Yes | Regex: `^AUD-[0-9]{4}-[0-9]{6}$` | ID | Primary Key | Format: `AUD-2026-000001`. |
| `entity_name` | VARCHAR(80) | Yes | Table name | Name | No | Entity being audited. |
| `entity_id` | VARCHAR(64) | Yes | Row ID | ID | No | Target row identifier. |
| `action` | VARCHAR(30) | Yes | Enum: `INSERT`, `UPDATE`, `DELETE`, `REVIEW` | Action | No | DML or access action. |
| `performed_by` | VARCHAR(64) | Yes | User ID or actor name | ID | No | Actor identifier. |
| `timestamp` | TIMESTAMP | Yes | ISO datetime | UTC | No | Event timestamp. |
| `changes_json` | TEXT | Optional | JSON string | JSON | No | Before and after diff. |
| `ip_address` | VARCHAR(45) | Optional | IPv4/IPv6 format | IP | No | Client IP address. |

---

## 5. Supporting Entities

### `validation_runs` & `validation_issues`
- Audit tracking of database integrity test executions, seed verification, and isolation of the 4 required negative scenarios (`FUTURE_INFO_LEAK`, `MISSING_SURVEY_PUNITIVE`, `OUTCOME_DATE_MISMATCH`, `UNEXPLAINED_SCORE`).

### `analysis_runs` & `support_assessments`
- Stores pre-outcome retention assessments, composite scores (0.00–100.00), priority tiers (`HIGH`, `MEDIUM`, `LOW`), Workload Strain, Career Velocity Stagnation, Engagement Trajectory, and human-readable factor attributions.
