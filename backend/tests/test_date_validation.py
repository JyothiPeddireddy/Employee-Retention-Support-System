"""Tests for Date Validation and chronological invariants."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import TeamMembershipHistory, Employee, TenureSnapshot


def test_membership_effective_end_date_order(seeded_db):
    emp = seeded_db.query(Employee).first()

    # Attempt to insert membership where end_date < start_date
    invalid_mem = TeamMembershipHistory(
        membership_id="MEM-BAD-DATES",
        employee_id=emp.employee_id,
        team_id=emp.current_team_id,
        role_id=emp.current_role_id,
        effective_start_date=date(2024, 6, 1),
        effective_end_date=date(2024, 1, 1),  # Precedes start date!
        is_current=False,
        transfer_reason="INTERNAL_TRANSFER"
    )
    seeded_db.add(invalid_mem)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_tenure_snapshot_dates_after_hire_date(seeded_db):
    snaps = seeded_db.query(TenureSnapshot).all()
    emp_lookup = {e.employee_id: e.hire_date for e in seeded_db.query(Employee).all()}

    for s in snaps:
        hire_d = emp_lookup.get(s.employee_id)
        assert s.snapshot_date >= hire_d, f"Snapshot {s.snapshot_id} date precedes employee hire date"
