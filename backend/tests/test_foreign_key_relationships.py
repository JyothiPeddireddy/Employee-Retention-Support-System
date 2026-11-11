"""Tests for Foreign Key Relationships and Cascade rules."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import Employee, Role, Team, TenureSnapshot, CompensationBand


def test_invalid_role_foreign_key_rejected(db_session):
    # Setup team
    team = Team(team_id="TEAM-VALID", name="Platform", department="Engineering")
    db_session.add(team)
    db_session.commit()

    # Attempt to insert employee referencing non-existent role_id
    emp = Employee(
        employee_id="EMP-INVALID-ROLE",
        first_name="Ghost",
        last_name="Role",
        email="ghost.role@example.com",
        hire_date=date(2023, 1, 1),
        current_role_id="ROLE-DOES-NOT-EXIST",  # Invalid FK
        current_team_id="TEAM-VALID",
        current_salary=90000.00,
        status="ACTIVE"
    )
    db_session.add(emp)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_invalid_band_foreign_key_rejected(db_session):
    # Attempt to insert role referencing non-existent band_id
    role = Role(
        role_id="ROLE-BAD-BAND",
        title="Unknown Specialist",
        level="IC3",
        band_id="BAND-NON-EXISTENT"  # Invalid FK
    )
    db_session.add(role)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_employee_relationship_navigation(seeded_db):
    emp = seeded_db.query(Employee).filter(Employee.current_role_id.isnot(None)).first()
    assert emp.role is not None
    assert emp.team is not None
    assert emp.role.compensation_band is not None
    assert len(emp.tenure_snapshots) > 0
    assert len(emp.workload_snapshots) > 0
    assert len(emp.engagement_surveys) > 0
