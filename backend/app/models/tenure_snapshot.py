"""TenureSnapshot model for longitudinal career velocity and tenure tracking."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Date, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class TenureSnapshot(Base):
    __tablename__ = "tenure_snapshots"

    # Deterministic format: SNAP-<employee_id>-<quarter>, e.g. SNAP-EMP-000001-2024Q1
    snapshot_id = Column(String(64), primary_key=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    snapshot_quarter = Column(String(10), nullable=False)  # e.g., 2024Q1
    snapshot_date = Column(Date, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    team_id = Column(String(32), ForeignKey("teams.team_id"), nullable=False)
    months_in_current_role = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="tenure_snapshots")
    role = relationship("Role")
    team = relationship("Team")

    __table_args__ = (
        UniqueConstraint("employee_id", "snapshot_quarter", name="uq_emp_tenure_quarter"),
        Index("idx_tenure_emp_quarter", "employee_id", "snapshot_quarter"),
        Index("idx_tenure_date", "snapshot_date"),
    )
