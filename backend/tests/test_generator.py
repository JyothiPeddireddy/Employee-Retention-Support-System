"""Tests for Synthetic Data Generator and Seed Reproducibility."""
import pytest
from backend.app.services.generator import SyntheticDataGenerator


def test_generator_deterministic_reproducibility():
    """Verify that running generator twice with the exact same seed produces identical outputs."""
    seed = 20261022
    scale = 100

    gen1 = SyntheticDataGenerator(seed=seed, scale=scale)
    gen1.generate_all()

    gen2 = SyntheticDataGenerator(seed=seed, scale=scale)
    gen2.generate_all()

    # Verify counts match
    assert len(gen1.employees) == len(gen2.employees) == 100
    assert len(gen1.tenure_snapshots) == len(gen2.tenure_snapshots)
    assert len(gen1.workload_snapshots) == len(gen2.workload_snapshots)
    assert len(gen1.engagement_surveys) == len(gen2.engagement_surveys)
    assert len(gen1.ground_truth_anomalies) == len(gen2.ground_truth_anomalies)

    # Verify deterministic fields
    for e1, e2 in zip(gen1.employees, gen2.employees):
        assert e1["employee_id"] == e2["employee_id"]
        assert e1["full_name"] == e2["full_name"]
        assert e1["current_salary"] == e2["current_salary"]
        assert e1["team_id"] == e2["team_id"]


def test_target_attrition_rate():
    """Verify attrition rate is within documented 5-15% range."""
    gen = SyntheticDataGenerator(seed=20261022, scale=200)
    gen.generate_all()

    attrited = [e for e in gen.employees if e["status"] == "ATTRITED"]
    attrition_rate = len(attrited) / len(gen.employees)
    assert 0.05 <= attrition_rate <= 0.15


def test_id_nomenclature_conventions():
    """Verify ID conventions: EMP-000001, SNAP-EMP-000001-2024Q1, etc."""
    gen = SyntheticDataGenerator(seed=20261022, scale=20)
    gen.generate_all()

    for emp in gen.employees:
        assert emp["employee_id"].startswith("EMP-")
        assert len(emp["employee_id"]) == 10

    for snap in gen.tenure_snapshots:
        assert snap["snapshot_id"].startswith("SNAP-EMP-")

    for w in gen.workload_snapshots:
        assert w["workload_id"].startswith("WORK-EMP-")

    for s in gen.engagement_surveys:
        assert s["survey_id"].startswith("SURV-")
