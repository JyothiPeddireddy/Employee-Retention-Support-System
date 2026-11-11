"""AttritionOutcome model - Post-horizon ground truth strictly isolated from predictions."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class AttritionOutcome(Base):
    __tablename__ = "attrition_outcomes"

    # Deterministic format: OUT-<employee-id>-2026
    outcome_id = Column(String(64), primary_key=True)
    employee_id = Column(
        String(32),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # Strictly 1:1 cardinality
    )
    attrition_date = Column(Date, nullable=True)  # NULL for retained workforce
    voluntary = Column(Boolean, default=True, nullable=False)
    primary_reason = Column(String(100), nullable=True)  # BURNOUT, CAREER_GROWTH, COMPENSATION, BETTER_OPPORTUNITY
    horizon_period = Column(String(20), nullable=False)  # e.g., '2026-H1'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="attrition_outcome")

    __table_args__ = (
        CheckConstraint(
            "primary_reason IS NULL OR primary_reason IN ('BURNOUT', 'CAREER_GROWTH', 'COMPENSATION', 'BETTER_OPPORTUNITY', 'RELOCATION', 'OTHER')",
            name="chk_attrition_reason"
        ),
        Index("idx_outcome_emp", "employee_id"),
        Index("idx_outcome_date", "attrition_date"),
    )
