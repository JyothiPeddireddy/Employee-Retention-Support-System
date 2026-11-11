"""Intervention model for tracking supportive retention touchpoints."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Date, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class Intervention(Base):
    __tablename__ = "interventions"

    # Deterministic format: INT-2026-000001
    intervention_id = Column(String(64), primary_key=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    conducted_by_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    intervention_date = Column(Date, nullable=False)
    intervention_type = Column(String(50), nullable=False)  # 1_ON_1_CAREER_CHECKIN, WORKLOAD_REBALANCING, etc.
    discussion_summary = Column(Text, nullable=False)       # Human review summary
    agreed_actions = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    status = Column(String(20), default="SCHEDULED", nullable=False)  # SCHEDULED, COMPLETED, CANCELLED
    simulated_outcome = Column(String(50), nullable=True)             # RETENTION_REINFORCED, STILL_AT_RISK
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="interventions", foreign_keys=[employee_id])
    conducted_by = relationship("Employee", foreign_keys=[conducted_by_id])
    events = relationship("InterventionEvent", back_populates="intervention", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')",
            name="chk_intervention_status"
        ),
        Index("idx_intervention_emp", "employee_id"),
        Index("idx_intervention_conductor", "conducted_by_id"),
        Index("idx_intervention_date", "intervention_date"),
    )
