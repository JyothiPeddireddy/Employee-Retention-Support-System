"""Tests for Unique Constraints preventing duplicate records."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import TenureSnapshot, WorkloadSnapshot, EngagementSurvey, Employee


def test_duplicate_tenure_snapshot_prevented(seeded_db):
    # Attempt to insert a second tenure snapshot for the same employee in the same quarter
    existing_snap = seeded_db.query(TenureSnapshot).first()

    dup_snap = TenureSnapshot(
        snapshot_id=f"{existing_snap.snapshot_id}-DUP",
        employee_id=existing_snap.employee_id,
        snapshot_quarter=existing_snap.snapshot_quarter,  # Duplicate compound key
        snapshot_date=existing_snap.snapshot_date,
        tenure_months=existing_snap.tenure_months + 1,
        role_id=existing_snap.role_id,
        team_id=existing_snap.team_id,
        months_in_current_role=existing_snap.months_in_current_role
    )
    seeded_db.add(dup_snap)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_duplicate_workload_snapshot_prevented(seeded_db):
    existing_work = seeded_db.query(WorkloadSnapshot).first()

    dup_work = WorkloadSnapshot(
        workload_id=f"{existing_work.workload_id}-DUP",
        employee_id=existing_work.employee_id,
        period_quarter=existing_work.period_quarter,  # Duplicate compound key
        period_date=existing_work.period_date,
        avg_weekly_hours=55.0,
        overtime_hours=15.0,
        consecutive_overtime_weeks=4,
        active_project_count=3,
        is_benign_surge=False
    )
    seeded_db.add(dup_work)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_duplicate_email_prevented(seeded_db):
    existing_emp = seeded_db.query(Employee).first()
    new_emp = Employee(
        employee_id="EMP-999999",
        first_name="New",
        last_name="Person",
        email=existing_emp.email,  # Duplicate email
        hire_date=date(2023, 1, 1),
        current_role_id=existing_emp.current_role_id,
        current_team_id=existing_emp.current_team_id,
        current_salary=110000.00,
        status="ACTIVE"
    )
    seeded_db.add(new_emp)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()
