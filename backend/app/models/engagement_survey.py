"""EngagementSurvey model with strict survey neutrality and missingness validation."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Numeric, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class EngagementSurvey(Base):
    __tablename__ = "engagement_surveys"

    # Deterministic format: SURV-2024-000001
    survey_id = Column(String(64), primary_key=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    survey_quarter = Column(String(10), nullable=False)  # e.g., 2024Q1
    survey_date = Column(Date, nullable=False)
    is_missing = Column(Boolean, default=False, nullable=False)
    satisfaction_score = Column(Numeric(3, 2), nullable=True)       # Likert 1.00 to 5.00
    work_life_balance_score = Column(Numeric(3, 2), nullable=True)  # Likert 1.00 to 5.00
    career_growth_score = Column(Numeric(3, 2), nullable=True)      # Likert 1.00 to 5.00
    manager_support_score = Column(Numeric(3, 2), nullable=True)    # Likert 1.00 to 5.00
    composite_engagement = Column(Numeric(3, 2), nullable=True)     # Mean of non-null Likert scores
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="engagement_surveys")

    __table_args__ = (
        # Enforces survey neutrality: if survey was skipped (is_missing=True), scores must be NULL (never penalized)
        CheckConstraint(
            "(is_missing = TRUE AND satisfaction_score IS NULL) OR "
            "(is_missing = FALSE AND satisfaction_score BETWEEN 1.00 AND 5.00)",
            name="chk_survey_neutrality"
        ),
        UniqueConstraint("employee_id", "survey_quarter", name="uq_emp_survey_quarter"),
        Index("idx_survey_emp_quarter", "employee_id", "survey_quarter"),
        Index("idx_survey_date", "survey_date"),
    )
