"""SQLAlchemy ORM models representing all 10 core entities plus anomaly ground truth."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime,
    ForeignKey, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(String(32), primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="team", foreign_keys="Employee.team_id")


class CompensationBand(Base):
    __tablename__ = "compensation_bands"

    band_id = Column(String(32), primary_key=True)
    name = Column(String(100), nullable=False)
    min_salary = Column(Float, nullable=False)
    mid_salary = Column(Float, nullable=False)
    max_salary = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    roles = relationship("Role", back_populates="compensation_band")

    __table_args__ = (
        CheckConstraint("min_salary <= mid_salary AND mid_salary <= max_salary", name="chk_salary_order"),
    )


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String(32), primary_key=True)
    title = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)  # IC1..IC6, M1..M3
    band_id = Column(String(32), ForeignKey("compensation_bands.band_id"), nullable=False)

    compensation_band = relationship("CompensationBand", back_populates="roles")
    employees = relationship("Employee", back_populates="role", foreign_keys="Employee.role_id")


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(32), primary_key=True)  # EMP-000001
    full_name = Column(String(120), nullable=False)
    email = Column(String(160), nullable=False, unique=True)
    team_id = Column(String(32), ForeignKey("teams.team_id"), nullable=False)
    role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    manager_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=True)
    hire_date = Column(Date, nullable=False)
    current_salary = Column(Float, nullable=False)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, LEAVE, ATTRITED
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="employees", foreign_keys=[team_id])
    role = relationship("Role", back_populates="employees", foreign_keys=[role_id])
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")

    tenure_snapshots = relationship("TenureSnapshot", back_populates="employee", cascade="all, delete-orphan")
    workload_snapshots = relationship("WorkloadSnapshot", back_populates="employee", cascade="all, delete-orphan")
    engagement_surveys = relationship("EngagementSurvey", back_populates="employee", cascade="all, delete-orphan")
    promotion_histories = relationship("PromotionHistory", back_populates="employee", foreign_keys="PromotionHistory.employee_id", cascade="all, delete-orphan")
    attrition_outcome = relationship("AttritionOutcome", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="employee", foreign_keys="Intervention.employee_id", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'LEAVE', 'ATTRITED')", name="chk_emp_status"),
    )


class TenureSnapshot(Base):
    __tablename__ = "tenure_snapshots"

    snapshot_id = Column(String(64), primary_key=True)  # SNAP-EMP-000001-2024Q1
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    snapshot_quarter = Column(String(10), nullable=False)  # 2024Q1
    snapshot_date = Column(Date, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    team_id = Column(String(32), ForeignKey("teams.team_id"), nullable=False)
    months_in_current_role = Column(Integer, nullable=False)

    employee = relationship("Employee", back_populates="tenure_snapshots")
    role = relationship("Role")
    team = relationship("Team")

    __table_args__ = (
        UniqueConstraint("employee_id", "snapshot_quarter", name="uq_emp_snapshot_quarter"),
    )


class WorkloadSnapshot(Base):
    __tablename__ = "workload_snapshots"

    workload_id = Column(String(64), primary_key=True)  # WORK-EMP-000001-2024Q1
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    period_quarter = Column(String(10), nullable=False)
    period_date = Column(Date, nullable=False)
    avg_weekly_hours = Column(Float, nullable=False)
    overtime_hours = Column(Float, default=0.0)
    consecutive_overtime_weeks = Column(Integer, default=0)
    active_project_count = Column(Integer, default=1)
    is_benign_surge = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="workload_snapshots")

    __table_args__ = (
        CheckConstraint("avg_weekly_hours >= 0 AND avg_weekly_hours <= 120", name="chk_weekly_hours"),
        UniqueConstraint("employee_id", "period_quarter", name="uq_emp_workload_period"),
    )


class EngagementSurvey(Base):
    __tablename__ = "engagement_surveys"

    survey_id = Column(String(64), primary_key=True)  # SURV-2024-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    survey_quarter = Column(String(10), nullable=False)
    survey_date = Column(Date, nullable=False)
    is_missing = Column(Boolean, default=False)
    satisfaction_score = Column(Float, nullable=True)       # 1.00 to 5.00
    work_life_balance_score = Column(Float, nullable=True)  # 1.00 to 5.00
    career_growth_score = Column(Float, nullable=True)      # 1.00 to 5.00
    manager_support_score = Column(Float, nullable=True)    # 1.00 to 5.00
    composite_engagement = Column(Float, nullable=True)

    employee = relationship("Employee", back_populates="engagement_surveys")

    __table_args__ = (
        UniqueConstraint("employee_id", "survey_quarter", name="uq_emp_survey_quarter"),
    )


class PromotionHistory(Base):
    __tablename__ = "promotion_histories"

    promotion_id = Column(String(64), primary_key=True)  # PROM-EMP-000001-2024
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    effective_date = Column(Date, nullable=False)
    from_role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    to_role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    from_salary = Column(Float, nullable=False)
    to_salary = Column(Float, nullable=False)
    movement_type = Column(String(20), nullable=False)  # PROMOTION, LATERAL_TRANSFER

    employee = relationship("Employee", back_populates="promotion_histories", foreign_keys=[employee_id])
    from_role = relationship("Role", foreign_keys=[from_role_id])
    to_role = relationship("Role", foreign_keys=[to_role_id])

    __table_args__ = (
        CheckConstraint("movement_type IN ('PROMOTION', 'LATERAL_TRANSFER')", name="chk_movement_type"),
    )


class AttritionOutcome(Base):
    __tablename__ = "attrition_outcomes"

    outcome_id = Column(String(64), primary_key=True)  # OUT-EMP-000001-2026
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, unique=True)
    attrition_date = Column(Date, nullable=True)
    voluntary = Column(Boolean, default=True)
    primary_reason = Column(String(100), nullable=True)  # CAREER_GROWTH, BURNOUT, COMP, UNKNOWN
    horizon_period = Column(String(20), nullable=False)  # 2026-H1

    employee = relationship("Employee", back_populates="attrition_outcome")


class Intervention(Base):
    __tablename__ = "interventions"

    intervention_id = Column(String(64), primary_key=True)  # INT-2026-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    conducted_by_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    intervention_date = Column(Date, nullable=False)
    intervention_type = Column(String(50), nullable=False)  # 1_ON_1_CAREER_CHECKIN, WORKLOAD_REBALANCING, etc.
    discussion_summary = Column(Text, nullable=False)
    agreed_actions = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    status = Column(String(20), default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    simulated_outcome = Column(String(50), nullable=True)  # RETENTION_REINFORCED, STILL_AT_RISK
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="interventions", foreign_keys=[employee_id])
    conducted_by = relationship("Employee", foreign_keys=[conducted_by_id])


class GroundTruthAnomaly(Base):
    __tablename__ = "ground_truth_anomalies"

    anomaly_id = Column(String(64), primary_key=True)  # ANOM-000001
    record_id = Column(String(64), nullable=False)
    table_name = Column(String(64), nullable=False)
    issue_type = Column(String(80), nullable=False)  # FUTURE_INFO_LEAK, MISSING_SURVEY_PUNITIVE, OUTCOME_DATE_MISMATCH, UNEXPLAINED_SCORE
    description = Column(Text, nullable=False)
    expected_validation_error = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
