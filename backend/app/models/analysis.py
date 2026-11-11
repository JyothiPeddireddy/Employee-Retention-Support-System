"""AnalysisRun and SupportAssessment models for explainable prioritization runs."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Date, DateTime, Text,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    analysis_id = Column(String(64), primary_key=True)  # ARUN-2026-000001
    execution_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    rule_version = Column(String(50), default="v1.0-explainable", nullable=False)
    cutoff_date = Column(Date, nullable=False)  # Strict pre-outcome observation cutoff
    cohort_size = Column(Integer, nullable=False)
    high_priority_count = Column(Integer, default=0, nullable=False)
    medium_priority_count = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default="COMPLETED", nullable=False)

    # Relationships
    assessments = relationship("SupportAssessment", back_populates="analysis_run", cascade="all, delete-orphan")


class SupportAssessment(Base):
    __tablename__ = "support_assessments"

    assessment_id = Column(String(64), primary_key=True)  # ASMT-2026-000001
    analysis_id = Column(String(64), ForeignKey("analysis_runs.analysis_id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    composite_priority_score = Column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00
    priority_tier = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    workload_strain_score = Column(Numeric(5, 2), nullable=False)
    career_stagnation_score = Column(Numeric(5, 2), nullable=False)
    engagement_trajectory_score = Column(Numeric(5, 2), nullable=False)
    factors_json = Column(Text, nullable=False)  # Explainable factor attributions
    recommended_topics_json = Column(Text, nullable=False)  # Recommended 1-on-1 topics
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="assessments")
    employee = relationship("Employee", back_populates="support_assessments")

    __table_args__ = (
        CheckConstraint(
            "priority_tier IN ('HIGH', 'MEDIUM', 'LOW')",
            name="chk_priority_tier"
        ),
        Index("idx_assessment_run", "analysis_id"),
        Index("idx_assessment_emp", "employee_id"),
        Index("idx_assessment_tier", "priority_tier"),
    )
