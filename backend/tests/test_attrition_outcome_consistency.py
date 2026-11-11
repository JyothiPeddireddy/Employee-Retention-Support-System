"""Tests for Attrition Outcome Consistency and Prediction Isolation."""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from backend.app.models import Employee, AttritionOutcome


def test_attrition_cardinality_strictly_one_to_one(seeded_db):
    emp = seeded_db.query(Employee).first()
    existing_outcome = seeded_db.query(AttritionOutcome).filter(
        AttritionOutcome.employee_id == emp.employee_id
    ).first()

    assert existing_outcome is not None

    # Attempt to insert a second outcome for the same employee
    dup_outcome = AttritionOutcome(
        outcome_id=f"OUT-{emp.employee_id}-CONFLICT",
        employee_id=emp.employee_id,  # Violates 1:1 unique constraint
        attrition_date=date(2026, 3, 1),
        voluntary=True,
        primary_reason="BURNOUT",
        horizon_period="2026-H1"
    )
    seeded_db.add(dup_outcome)
    with pytest.raises(IntegrityError):
        seeded_db.commit()
    seeded_db.rollback()


def test_attrition_target_rate_bounds(seeded_db):
    total = seeded_db.query(AttritionOutcome).count()
    resigned = seeded_db.query(AttritionOutcome).filter(AttritionOutcome.attrition_date.isnot(None)).count()
    attrition_rate = resigned / total
    assert 0.05 <= attrition_rate <= 0.15, f"Attrition rate {attrition_rate*100:.1f}% outside 5-15% target"


def test_ground_truth_isolation_from_snapshots(seeded_db):
    # Verify that tenure and workload snapshots contain ZERO references to post-horizon attrition
    outcomes = {o.employee_id: o.attrition_date for o in seeded_db.query(AttritionOutcome).all()}

    for emp in seeded_db.query(Employee).all():
        attr_date = outcomes.get(emp.employee_id)
        if attr_date:
            # All snapshots must strictly precede the future exit date
            for snap in emp.tenure_snapshots:
                assert snap.snapshot_date < attr_date, "Snapshot date leaks into future post-attrition timeline!"
