"""WorkloadSnapshot model for overtime streaks and capacity strain tracking."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class WorkloadSnapshot(Base):
    __tablename__ = "workload_snapshots"

    # Deterministic format: WORK-<employee_id>-<quarter>, e.g. WORK-EMP-000001-2024Q1
    workload_id = Column(String(64), primary_key=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    period_quarter = Column(String(10), nullable=False)  # e.g., 2024Q1
    period_date = Column(Date, nullable=False)
    avg_weekly_hours = Column(Numeric(5, 2), nullable=False)
    overtime_hours = Column(Numeric(5, 2), default=0.0, nullable=False)
    consecutive_overtime_weeks = Column(Integer, default=0, nullable=False)
    active_project_count = Column(Integer, default=1, nullable=False)
    is_benign_surge = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="workload_snapshots")

    __table_args__ = (
        CheckConstraint(
            "avg_weekly_hours >= 0.0 AND avg_weekly_hours <= 120.0",
            name="chk_weekly_hours"
        ),
        UniqueConstraint("employee_id", "period_quarter", name="uq_emp_workload_quarter"),
        Index("idx_workload_emp_quarter", "employee_id", "period_quarter"),
        Index("idx_workload_date", "period_date"),
    )
