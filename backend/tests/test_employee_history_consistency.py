"""Tests for Employee History Consistency and Historical Record Preservation."""
import pytest
from decimal import Decimal
from datetime import date
from backend.app.models import Employee, TeamMembershipHistory, TenureSnapshot


def test_effective_dated_team_transfer_preserves_history(seeded_db):
    emp = seeded_db.query(Employee).first()

    # Get active membership
    active_mem = seeded_db.query(TeamMembershipHistory).filter(
        TeamMembershipHistory.employee_id == emp.employee_id,
        TeamMembershipHistory.is_current.is_(True)
    ).first()

    assert active_mem is not None
    orig_team_id = active_mem.team_id

    # Simulate internal transfer on 2025-01-01 to another team
    new_team_id = "TEAM-PROD-01" if orig_team_id != "TEAM-PROD-01" else "TEAM-ENG-02"

    # Close old membership
    active_mem.effective_end_date = date(2024, 12, 31)
    active_mem.is_current = False

    # Create new membership
    new_mem = TeamMembershipHistory(
        membership_id=f"MEM-{emp.employee_id}-0099",
        employee_id=emp.employee_id,
        team_id=new_team_id,
        role_id=emp.current_role_id,
        effective_start_date=date(2025, 1, 1),
        effective_end_date=None,
        is_current=True,
        transfer_reason="INTERNAL_TRANSFER"
    )
    seeded_db.add(new_mem)
    seeded_db.commit()

    # Query all memberships for employee
    all_memberships = seeded_db.query(TeamMembershipHistory).filter(
        TeamMembershipHistory.employee_id == emp.employee_id
    ).order_by(TeamMembershipHistory.effective_start_date).all()

    # Verify both history and current assignment are preserved
    assert len(all_memberships) == 2
    assert all_memberships[0].team_id == orig_team_id
    assert all_memberships[0].is_current is False
    assert all_memberships[1].team_id == new_team_id
    assert all_memberships[1].is_current is True


def test_updating_employee_salary_does_not_mutate_snapshots(seeded_db):
    emp = seeded_db.query(Employee).first()
    orig_salary = emp.current_salary
    snaps_count_before = len(emp.tenure_snapshots)

    # Update current salary using Decimal
    emp.current_salary = Decimal(str(orig_salary)) + Decimal("15000.00")
    seeded_db.commit()

    # Verify snapshots remain intact
    seeded_db.refresh(emp)
    assert len(emp.tenure_snapshots) == snaps_count_before
