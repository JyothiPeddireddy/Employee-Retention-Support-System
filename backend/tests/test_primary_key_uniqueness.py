"""Tests for Primary Key Uniqueness across all entities."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import Team, CompensationBand, Role, Employee


def test_team_primary_key_uniqueness(db_session):
    team1 = Team(team_id="TEAM-TEST-01", name="Alpha Team", department="Engineering")
    db_session.add(team1)
    db_session.commit()

    # Attempt to insert identical primary key
    team2 = Team(team_id="TEAM-TEST-01", name="Beta Team", department="Product")
    db_session.add(team2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_employee_primary_key_uniqueness(seeded_db):
    # Attempt to insert an employee with an existing employee_id
    existing_emp = seeded_db.query(Employee).first()
    dup_emp = Employee(
        employee_id=existing_emp.employee_id,  # Duplicate PK
        first_name="Duplicate",
        last_name="Person",
        email="dup.unique@example.com",
        hire_date=date(2023, 1, 1),
        current_role_id=existing_emp.current_role_id,
        current_team_id=existing_emp.current_team_id,
        current_salary=100000.00,
        status="ACTIVE"
    )
    seeded_db.add(dup_emp)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_all_seeded_primary_keys_are_unique(seeded_db):
    employees = seeded_db.query(Employee.employee_id).all()
    emp_ids = [e[0] for e in employees]
    assert len(emp_ids) == len(set(emp_ids)), "Employee primary keys must be strictly unique"
