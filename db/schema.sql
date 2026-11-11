-- ============================================================================
-- Supportive Retention Signal Engine - Database Schema (DDL)
-- Complies with Hackathon Problem Statement & ID Nomenclature Conventions
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. Master Tables
-- ----------------------------------------------------------------------------

-- Teams / Organizational Units
CREATE TABLE IF NOT EXISTS teams (
    team_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compensation Bands
CREATE TABLE IF NOT EXISTS compensation_bands (
    band_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    min_salary NUMERIC(12, 2) NOT NULL,
    mid_salary NUMERIC(12, 2) NOT NULL,
    max_salary NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    CONSTRAINT chk_salary_order CHECK (min_salary <= mid_salary AND mid_salary <= max_salary)
);

-- Job Roles & Levels
CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,           -- e.g., IC1..IC6, M1..M3
    band_id VARCHAR(32) NOT NULL,
    FOREIGN KEY (band_id) REFERENCES compensation_bands(band_id) ON DELETE RESTRICT
);

-- Employees Master
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(32) PRIMARY KEY,  -- EMP-000001
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    team_id VARCHAR(32) NOT NULL,
    role_id VARCHAR(32) NOT NULL,
    manager_id VARCHAR(32),               -- Self-referential nullable FK
    hire_date DATE NOT NULL,
    current_salary NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, LEAVE, ATTRITED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id),
    CONSTRAINT chk_emp_status CHECK (status IN ('ACTIVE', 'LEAVE', 'ATTRITED'))
);

-- ----------------------------------------------------------------------------
-- 2. Longitudinal Snapshot & Event Tables
-- ----------------------------------------------------------------------------

-- Quarterly Tenure Snapshots (e.g., SNAP-EMP-000001-2024Q1)
CREATE TABLE IF NOT EXISTS tenure_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    employee_id VARCHAR(32) NOT NULL,
    snapshot_quarter VARCHAR(10) NOT NULL, -- e.g., '2024Q1'
    snapshot_date DATE NOT NULL,
    tenure_months INT NOT NULL,
    role_id VARCHAR(32) NOT NULL,
    team_id VARCHAR(32) NOT NULL,
    months_in_current_role INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    CONSTRAINT uq_emp_snapshot_quarter UNIQUE (employee_id, snapshot_quarter)
);

-- Monthly/Quarterly Workload Snapshots
CREATE TABLE IF NOT EXISTS workload_snapshots (
    workload_id VARCHAR(64) PRIMARY KEY,   -- WORK-EMP-000001-2024Q1
    employee_id VARCHAR(32) NOT NULL,
    period_quarter VARCHAR(10) NOT NULL,
    period_date DATE NOT NULL,
    avg_weekly_hours NUMERIC(5, 2) NOT NULL,
    overtime_hours NUMERIC(5, 2) DEFAULT 0.0,
    consecutive_overtime_weeks INT DEFAULT 0,
    active_project_count INT DEFAULT 1,
    is_benign_surge BOOLEAN DEFAULT FALSE, -- e.g., product launch crunch
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    CONSTRAINT chk_weekly_hours CHECK (avg_weekly_hours >= 0 AND avg_weekly_hours <= 120),
    CONSTRAINT uq_emp_workload_period UNIQUE (employee_id, period_quarter)
);

-- Quarterly Engagement Surveys (Likert 1-5 with missingness support)
CREATE TABLE IF NOT EXISTS engagement_surveys (
    survey_id VARCHAR(64) PRIMARY KEY,     -- SURV-2024-000001
    employee_id VARCHAR(32) NOT NULL,
    survey_quarter VARCHAR(10) NOT NULL,
    survey_date DATE NOT NULL,
    is_missing BOOLEAN DEFAULT FALSE,
    satisfaction_score NUMERIC(3, 2),      -- Likert scale 1.00 to 5.00
    work_life_balance_score NUMERIC(3, 2), -- Likert scale 1.00 to 5.00
    career_growth_score NUMERIC(3, 2),     -- Likert scale 1.00 to 5.00
    manager_support_score NUMERIC(3, 2),   -- Likert scale 1.00 to 5.00
    composite_engagement NUMERIC(3, 2),    -- Mean of provided scores
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    CONSTRAINT chk_survey_scores CHECK (
        (is_missing = TRUE AND satisfaction_score IS NULL) OR
        (is_missing = FALSE AND satisfaction_score BETWEEN 1.00 AND 5.00)
    ),
    CONSTRAINT uq_emp_survey_quarter UNIQUE (employee_id, survey_quarter)
);

-- Career Progression & Promotion Histories
CREATE TABLE IF NOT EXISTS promotion_histories (
    promotion_id VARCHAR(64) PRIMARY KEY,  -- PROM-EMP-000001-2024
    employee_id VARCHAR(32) NOT NULL,
    effective_date DATE NOT NULL,
    from_role_id VARCHAR(32) NOT NULL,
    to_role_id VARCHAR(32) NOT NULL,
    from_salary NUMERIC(12, 2) NOT NULL,
    to_salary NUMERIC(12, 2) NOT NULL,
    movement_type VARCHAR(20) NOT NULL,   -- PROMOTION, LATERAL_TRANSFER
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (from_role_id) REFERENCES roles(role_id),
    FOREIGN KEY (to_role_id) REFERENCES roles(role_id),
    CONSTRAINT chk_movement_type CHECK (movement_type IN ('PROMOTION', 'LATERAL_TRANSFER'))
);

-- ----------------------------------------------------------------------------
-- 3. Future Outcome & Supportive Intervention Tables
-- ----------------------------------------------------------------------------

-- Future Voluntary Attrition Outcome (Horizon 2026)
-- STRICT RULE: Only pre-outcome features are used for modeling!
CREATE TABLE IF NOT EXISTS attrition_outcomes (
    outcome_id VARCHAR(64) PRIMARY KEY,    -- OUT-EMP-000001-2026
    employee_id VARCHAR(32) NOT NULL UNIQUE,
    attrition_date DATE,
    voluntary BOOLEAN DEFAULT TRUE,
    primary_reason VARCHAR(100),           -- CAREER_GROWTH, BURNOUT, COMP, UNKNOWN
    horizon_period VARCHAR(20) NOT NULL,   -- e.g., '2026-H1'
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Supportive Retention Interventions (Human-in-the-Loop)
CREATE TABLE IF NOT EXISTS interventions (
    intervention_id VARCHAR(64) PRIMARY KEY, -- INT-2026-000001
    employee_id VARCHAR(32) NOT NULL,
    conducted_by_id VARCHAR(32) NOT NULL,    -- Manager or HR Partner
    intervention_date DATE NOT NULL,
    intervention_type VARCHAR(50) NOT NULL,  -- 1_ON_1_CAREER_CHECKIN, WORKLOAD_REBALANCING, COMP_REVIEW
    discussion_summary TEXT NOT NULL,
    agreed_actions TEXT,
    follow_up_date DATE,
    status VARCHAR(20) DEFAULT 'SCHEDULED',  -- SCHEDULED, COMPLETED, CANCELLED
    simulated_outcome VARCHAR(50),           -- RETENTION_REINFORCED, STILL_AT_RISK
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (conducted_by_id) REFERENCES employees(employee_id)
);

-- ----------------------------------------------------------------------------
-- 4. Isolated Anomaly & Ground Truth Table (Never Leaked to Model Features)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ground_truth_anomalies (
    anomaly_id VARCHAR(64) PRIMARY KEY,     -- ANOM-000001
    record_id VARCHAR(64) NOT NULL,         -- ID of corrupted/affected entity
    table_name VARCHAR(64) NOT NULL,
    issue_type VARCHAR(80) NOT NULL,        -- FUTURE_INFO_LEAK, MISSING_SURVEY_PUNITIVE, OUTCOME_DATE_MISMATCH, UNEXPLAINED_SCORE
    description TEXT NOT NULL,
    expected_validation_error TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Indexes for High Performance Queries
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_emp_team ON employees(team_id);
CREATE INDEX IF NOT EXISTS idx_emp_role ON employees(role_id);
CREATE INDEX IF NOT EXISTS idx_snap_emp ON tenure_snapshots(employee_id, snapshot_quarter);
CREATE INDEX IF NOT EXISTS idx_work_emp ON workload_snapshots(employee_id, period_quarter);
CREATE INDEX IF NOT EXISTS idx_surv_emp ON engagement_surveys(employee_id, survey_quarter);
CREATE INDEX IF NOT EXISTS idx_promo_emp ON promotion_histories(employee_id);
CREATE INDEX IF NOT EXISTS idx_interv_emp ON interventions(employee_id);
