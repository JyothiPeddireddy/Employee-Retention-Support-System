"""Tests for Enum Validation and Allowed Check Constraints."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import Employee, PromotionHistory, Intervention, AppUser


def test_invalid_employee_status_rejected(seeded_db):
    emp = seeded_db.query(Employee).first()

    # Attempt to set invalid status not in ('ACTIVE', 'LEAVE', 'ATTRITED')
    invalid_emp = Employee(
        employee_id="EMP-BAD-STATUS",
        first_name="Bad",
        last_name="Status",
        email="bad.status@example.com",
        hire_date=date(2023, 1, 1),
        current_role_id=emp.current_role_id,
        current_team_id=emp.current_team_id,
        current_salary=95000.00,
        status="FIRED_UNILATERALLY"  # Invalid status!
    )
    seeded_db.add(invalid_emp)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_invalid_promotion_movement_type_rejected(seeded_db):
    emp = seeded_db.query(Employee).first()

    invalid_promo = PromotionHistory(
        promotion_id="PROM-BAD-TYPE",
        employee_id=emp.employee_id,
        effective_date=date(2024, 6, 1),
        from_role_id=emp.current_role_id,
        to_role_id=emp.current_role_id,
        from_salary=80000.00,
        to_salary=90000.00,
        movement_type="DEMOTION_PUNITIVE"  # Invalid movement type!
    )
    seeded_db.add(invalid_promo)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_invalid_user_role_rejected(db_session):
    invalid_user = AppUser(
        user_id="USR-BAD-ROLE",
        username="hacker_user",
        email="hacker@example.com",
        hashed_password="mock_password_hash",
        role="SUPERUSER_ALL_POWERFUL"  # Invalid role!
    )
    db_session.add(invalid_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
