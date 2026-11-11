"""Tests for Historical Snapshot Preservation and Survey Neutrality."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import EngagementSurvey, WorkloadSnapshot, Employee


def test_missing_survey_neutrality_constraint(seeded_db):
    emp = seeded_db.query(Employee).first()

    # Valid missing survey: is_missing=True AND satisfaction_score=None
    valid_missing = EngagementSurvey(
        survey_id=f"SURV-VALID-MISSING-{emp.employee_id}",
        employee_id=emp.employee_id,
        survey_quarter="2026Q1",
        survey_date=date(2026, 3, 31),
        is_missing=True,
        satisfaction_score=None,
        composite_engagement=None
    )
    seeded_db.add(valid_missing)
    seeded_db.commit()

    # Invalid biased survey: is_missing=True but satisfaction_score=1.00 (penalizing missingness!)
    biased_survey = EngagementSurvey(
        survey_id=f"SURV-BIASED-{emp.employee_id}",
        employee_id=emp.employee_id,
        survey_quarter="2026Q2",
        survey_date=date(2026, 6, 30),
        is_missing=True,
        satisfaction_score=1.00,  # Violates chk_survey_neutrality!
        composite_engagement=1.00
    )
    seeded_db.add(biased_survey)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_workload_hours_valid_range_constraint(seeded_db):
    emp = seeded_db.query(Employee).first()

    # Attempt to insert workload snapshot with impossible weekly hours (> 120 hrs/wk)
    invalid_workload = WorkloadSnapshot(
        workload_id=f"WORK-IMPOSSIBLE-{emp.employee_id}",
        employee_id=emp.employee_id,
        period_quarter="2026Q1",
        period_date=date(2026, 3, 31),
        avg_weekly_hours=150.0,  # Violates chk_weekly_hours!
        overtime_hours=110.0,
        consecutive_overtime_weeks=12,
        active_project_count=5,
        is_benign_surge=False
    )
    seeded_db.add(invalid_workload)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_longitudinal_snapshots_8_quarters_coverage(seeded_db):
    emp = seeded_db.query(Employee).first()
    assert len(emp.workload_snapshots) == 8, "Expected 8 quarterly workload snapshots across 24 months"
    assert len(emp.tenure_snapshots) == 8, "Expected 8 quarterly tenure snapshots across 24 months"
    assert len(emp.engagement_surveys) == 8, "Expected 8 quarterly engagement surveys across 24 months"
