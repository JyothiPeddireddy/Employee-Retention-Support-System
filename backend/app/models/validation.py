"""ValidationRun and ValidationIssue models for auditing data quality & edge cases."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    run_id = Column(String(64), primary_key=True)  # VRUN-2026-000001
    run_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    dataset_version = Column(String(50), default="v1.0-synthetic", nullable=False)
    seed_used = Column(Integer, nullable=False)
    total_checks = Column(Integer, nullable=False)
    passed_checks = Column(Integer, nullable=False)
    failed_checks = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False)  # PASSED, ANOMALIES_DETECTED

    # Relationships
    issues = relationship("ValidationIssue", back_populates="run", cascade="all, delete-orphan")


class ValidationIssue(Base):
    __tablename__ = "validation_issues"

    issue_id = Column(String(64), primary_key=True)  # VISS-2026-000001
    run_id = Column(String(64), ForeignKey("validation_runs.run_id", ondelete="CASCADE"), nullable=False)
    table_name = Column(String(64), nullable=False)
    record_id = Column(String(64), nullable=False)
    issue_type = Column(String(80), nullable=False)  # FUTURE_INFO_LEAK, MISSING_SURVEY_PUNITIVE, OUTCOME_DATE_MISMATCH, UNEXPLAINED_SCORE
    severity = Column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    run = relationship("ValidationRun", back_populates="issues")

    __table_args__ = (
        CheckConstraint(
            "issue_type IN ('FUTURE_INFO_LEAK', 'MISSING_SURVEY_PUNITIVE', 'OUTCOME_DATE_MISMATCH', 'UNEXPLAINED_SCORE', 'SCHEMA_ERROR')",
            name="chk_issue_type"
        ),
        Index("idx_vissue_run", "run_id"),
        Index("idx_vissue_record", "table_name", "record_id"),
    )


class GroundTruthAnomaly(Base):
    __tablename__ = "ground_truth_anomalies"

    anomaly_id = Column(String(64), primary_key=True)  # ANOM-000001
    record_id = Column(String(64), nullable=False)
    table_name = Column(String(64), nullable=False)
    issue_type = Column(String(80), nullable=False)  # FUTURE_INFO_LEAK, MISSING_SURVEY_PUNITIVE, OUTCOME_DATE_MISMATCH, UNEXPLAINED_SCORE
    description = Column(Text, nullable=False)
    expected_validation_error = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

