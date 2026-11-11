"""Initial database schema with 14 core entities and 4 supporting entities.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-11 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Compensation Bands
    op.create_table(
        "compensation_bands",
        sa.Column("band_id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("min_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("mid_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("max_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("min_salary <= mid_salary AND mid_salary <= max_salary", name="chk_salary_order")
    )

    # 2. Roles
    op.create_table(
        "roles",
        sa.Column("role_id", sa.String(32), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("band_id", sa.String(32), sa.ForeignKey("compensation_bands.band_id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.create_index("idx_roles_band", "roles", ["band_id"])
    op.create_index("idx_roles_level", "roles", ["level"])

    # 3. Teams
    op.create_table(
        "teams",
        sa.Column("team_id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    )
    op.create_index("idx_teams_dept", "teams", ["department"])

    # 4. Employees
    op.create_table(
        "employees",
        sa.Column("employee_id", sa.String(32), primary_key=True),
        sa.Column("first_name", sa.String(60), nullable=False),
        sa.Column("last_name", sa.String(60), nullable=False),
        sa.Column("email", sa.String(160), unique=True, nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column("current_role_id", sa.String(32), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("current_team_id", sa.String(32), sa.ForeignKey("teams.team_id"), nullable=False),
        sa.Column("current_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("manager_id", sa.String(32), sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('ACTIVE', 'LEAVE', 'ATTRITED')", name="chk_employee_status")
    )
    op.create_index("idx_employees_team", "employees", ["current_team_id"])
    op.create_index("idx_employees_role", "employees", ["current_role_id"])
    op.create_index("idx_employees_manager", "employees", ["manager_id"])
    op.create_index("idx_employees_status", "employees", ["status"])

    # 5. Team Membership History (Effective-dated)
    op.create_table(
        "team_membership_history",
        sa.Column("membership_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_id", sa.String(32), sa.ForeignKey("teams.team_id"), nullable=False),
        sa.Column("role_id", sa.String(32), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("effective_start_date", sa.Date(), nullable=False),
        sa.Column("effective_end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default="TRUE", nullable=False),
        sa.Column("transfer_reason", sa.String(50), server_default="HIRE", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("effective_end_date IS NULL OR effective_end_date >= effective_start_date", name="chk_membership_dates")
    )
    op.create_index("idx_membership_emp", "team_membership_history", ["employee_id"])
    op.create_index("idx_membership_team", "team_membership_history", ["team_id"])
    op.create_index("idx_membership_active", "team_membership_history", ["employee_id", "is_current"])

    # 6. Tenure Snapshots
    op.create_table(
        "tenure_snapshots",
        sa.Column("snapshot_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_quarter", sa.String(10), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("tenure_months", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.String(32), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("team_id", sa.String(32), sa.ForeignKey("teams.team_id"), nullable=False),
        sa.Column("months_in_current_role", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("employee_id", "snapshot_quarter", name="uq_emp_tenure_quarter")
    )
    op.create_index("idx_tenure_emp_quarter", "tenure_snapshots", ["employee_id", "snapshot_quarter"])
    op.create_index("idx_tenure_date", "tenure_snapshots", ["snapshot_date"])

    # 7. Workload Snapshots
    op.create_table(
        "workload_snapshots",
        sa.Column("workload_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_quarter", sa.String(10), nullable=False),
        sa.Column("period_date", sa.Date(), nullable=False),
        sa.Column("avg_weekly_hours", sa.Numeric(5, 2), nullable=False),
        sa.Column("overtime_hours", sa.Numeric(5, 2), server_default="0.0", nullable=False),
        sa.Column("consecutive_overtime_weeks", sa.Integer(), server_default="0", nullable=False),
        sa.Column("active_project_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("is_benign_surge", sa.Boolean(), server_default="FALSE", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("avg_weekly_hours >= 0.0 AND avg_weekly_hours <= 120.0", name="chk_weekly_hours"),
        sa.UniqueConstraint("employee_id", "period_quarter", name="uq_emp_workload_quarter")
    )
    op.create_index("idx_workload_emp_quarter", "workload_snapshots", ["employee_id", "period_quarter"])
    op.create_index("idx_workload_date", "workload_snapshots", ["period_date"])

    # 8. Engagement Surveys (Neutrality validation)
    op.create_table(
        "engagement_surveys",
        sa.Column("survey_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("survey_quarter", sa.String(10), nullable=False),
        sa.Column("survey_date", sa.Date(), nullable=False),
        sa.Column("is_missing", sa.Boolean(), server_default="FALSE", nullable=False),
        sa.Column("satisfaction_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("work_life_balance_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("career_growth_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("manager_support_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("composite_engagement", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "(is_missing = TRUE AND satisfaction_score IS NULL) OR "
            "(is_missing = FALSE AND satisfaction_score BETWEEN 1.00 AND 5.00)",
            name="chk_survey_neutrality"
        ),
        sa.UniqueConstraint("employee_id", "survey_quarter", name="uq_emp_survey_quarter")
    )
    op.create_index("idx_survey_emp_quarter", "engagement_surveys", ["employee_id", "survey_quarter"])
    op.create_index("idx_survey_date", "engagement_surveys", ["survey_date"])

    # 9. Promotion Histories
    op.create_table(
        "promotion_histories",
        sa.Column("promotion_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("from_role_id", sa.String(32), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("to_role_id", sa.String(32), sa.ForeignKey("roles.role_id"), nullable=False),
        sa.Column("from_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("to_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("movement_type IN ('PROMOTION', 'LATERAL_TRANSFER')", name="chk_movement_type")
    )
    op.create_index("idx_promo_emp", "promotion_histories", ["employee_id"])
    op.create_index("idx_promo_date", "promotion_histories", ["effective_date"])

    # 10. Attrition Outcomes (Ground Truth Horizon - Separate from prediction input)
    op.create_table(
        "attrition_outcomes",
        sa.Column("outcome_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("attrition_date", sa.Date(), nullable=True),
        sa.Column("voluntary", sa.Boolean(), server_default="TRUE", nullable=False),
        sa.Column("primary_reason", sa.String(100), nullable=True),
        sa.Column("horizon_period", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "primary_reason IS NULL OR primary_reason IN ('BURNOUT', 'CAREER_GROWTH', 'COMPENSATION', 'BETTER_OPPORTUNITY', 'RELOCATION', 'OTHER')",
            name="chk_attrition_reason"
        )
    )
    op.create_index("idx_outcome_emp", "attrition_outcomes", ["employee_id"])
    op.create_index("idx_outcome_date", "attrition_outcomes", ["attrition_date"])

    # 11. Interventions (Supportive retention check-in records)
    op.create_table(
        "interventions",
        sa.Column("intervention_id", sa.String(64), primary_key=True),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("conducted_by_id", sa.String(32), sa.ForeignKey("employees.employee_id"), nullable=False),
        sa.Column("intervention_date", sa.Date(), nullable=False),
        sa.Column("intervention_type", sa.String(50), nullable=False),
        sa.Column("discussion_summary", sa.Text(), nullable=False),
        sa.Column("agreed_actions", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), server_default="SCHEDULED", nullable=False),
        sa.Column("simulated_outcome", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')", name="chk_intervention_status")
    )
    op.create_index("idx_intervention_emp", "interventions", ["employee_id"])
    op.create_index("idx_intervention_conductor", "interventions", ["conducted_by_id"])
    op.create_index("idx_intervention_date", "interventions", ["intervention_date"])

    # 12. Intervention Events
    op.create_table(
        "intervention_events",
        sa.Column("event_id", sa.String(64), primary_key=True),
        sa.Column("intervention_id", sa.String(64), sa.ForeignKey("interventions.intervention_id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("actor_id", sa.String(32), sa.ForeignKey("employees.employee_id"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "event_type IN ('CREATED', 'NOTES_UPDATED', 'ACTION_COMPLETED', 'FOLLOW_UP_SCHEDULED', 'CANCELLED')",
            name="chk_event_type"
        )
    )
    op.create_index("idx_intev_intervention", "intervention_events", ["intervention_id"])
    op.create_index("idx_intev_timestamp", "intervention_events", ["event_timestamp"])

    # 13. App Users
    op.create_table(
        "app_users",
        sa.Column("user_id", sa.String(32), primary_key=True),
        sa.Column("username", sa.String(80), unique=True, nullable=False),
        sa.Column("email", sa.String(160), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), server_default="HR_PARTNER", nullable=False),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="TRUE", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("role IN ('HR_PARTNER', 'MANAGER', 'SYSTEM_ADMIN', 'AUDITOR')", name="chk_user_role")
    )
    op.create_index("idx_users_role", "app_users", ["role"])

    # 14. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("log_id", sa.String(64), primary_key=True),
        sa.Column("entity_name", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("performed_by", sa.String(64), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("changes_json", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True)
    )
    op.create_index("idx_audit_entity", "audit_logs", ["entity_name", "entity_id"])
    op.create_index("idx_audit_timestamp", "audit_logs", ["timestamp"])

    # 15. Validation Runs
    op.create_table(
        "validation_runs",
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column("run_timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("dataset_version", sa.String(50), server_default="v1.0-synthetic", nullable=False),
        sa.Column("seed_used", sa.Integer(), nullable=False),
        sa.Column("total_checks", sa.Integer(), nullable=False),
        sa.Column("passed_checks", sa.Integer(), nullable=False),
        sa.Column("failed_checks", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False)
    )

    # 16. Validation Issues
    op.create_table(
        "validation_issues",
        sa.Column("issue_id", sa.String(64), primary_key=True),
        sa.Column("run_id", sa.String(64), sa.ForeignKey("validation_runs.run_id", ondelete="CASCADE"), nullable=False),
        sa.Column("table_name", sa.String(64), nullable=False),
        sa.Column("record_id", sa.String(64), nullable=False),
        sa.Column("issue_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(20), server_default="HIGH", nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "issue_type IN ('FUTURE_INFO_LEAK', 'MISSING_SURVEY_PUNITIVE', 'OUTCOME_DATE_MISMATCH', 'UNEXPLAINED_SCORE', 'SCHEMA_ERROR')",
            name="chk_issue_type"
        )
    )
    op.create_index("idx_vissue_run", "validation_issues", ["run_id"])
    op.create_index("idx_vissue_record", "validation_issues", ["table_name", "record_id"])

    # 17. Analysis Runs
    op.create_table(
        "analysis_runs",
        sa.Column("analysis_id", sa.String(64), primary_key=True),
        sa.Column("execution_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("rule_version", sa.String(50), server_default="v1.0-explainable", nullable=False),
        sa.Column("cutoff_date", sa.Date(), nullable=False),
        sa.Column("cohort_size", sa.Integer(), nullable=False),
        sa.Column("high_priority_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("medium_priority_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(30), server_default="COMPLETED", nullable=False)
    )

    # 18. Support Assessments
    op.create_table(
        "support_assessments",
        sa.Column("assessment_id", sa.String(64), primary_key=True),
        sa.Column("analysis_id", sa.String(64), sa.ForeignKey("analysis_runs.analysis_id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.String(32), sa.ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False),
        sa.Column("composite_priority_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("priority_tier", sa.String(20), nullable=False),
        sa.Column("workload_strain_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("career_stagnation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("engagement_trajectory_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("factors_json", sa.Text(), nullable=False),
        sa.Column("recommended_topics_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("priority_tier IN ('HIGH', 'MEDIUM', 'LOW')", name="chk_priority_tier")
    )
    op.create_index("idx_assessment_run", "support_assessments", ["analysis_id"])
    op.create_index("idx_assessment_emp", "support_assessments", ["employee_id"])
    op.create_index("idx_assessment_tier", "support_assessments", ["priority_tier"])


def downgrade() -> None:
    op.drop_table("support_assessments")
    op.drop_table("analysis_runs")
    op.drop_table("validation_issues")
    op.drop_table("validation_runs")
    op.drop_table("audit_logs")
    op.drop_table("app_users")
    op.drop_table("intervention_events")
    op.drop_table("interventions")
    op.drop_table("attrition_outcomes")
    op.drop_table("promotion_histories")
    op.drop_table("engagement_surveys")
    op.drop_table("workload_snapshots")
    op.drop_table("tenure_snapshots")
    op.drop_table("team_membership_history")
    op.drop_table("employees")
    op.drop_table("teams")
    op.drop_table("roles")
    op.drop_table("compensation_bands")
