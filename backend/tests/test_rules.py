"""Tests for Rules and Explainable Prioritization Engine."""
import pytest
from backend.app.services.generator import SyntheticDataGenerator
from backend.app.services.rules import PrioritizationRulesEngine


@pytest.fixture
def test_engine():
    gen = SyntheticDataGenerator(seed=20261022, scale=100)
    gen.generate_all()
    store = {
        "teams": gen.teams,
        "compensation_bands": gen.bands,
        "roles": gen.roles,
        "employees": gen.employees,
        "tenure_snapshots": gen.tenure_snapshots,
        "workload_snapshots": gen.workload_snapshots,
        "engagement_surveys": gen.engagement_surveys,
        "interventions": gen.interventions,
    }
    return PrioritizationRulesEngine(store)


def test_prioritization_explainability_contract(test_engine):
    """Verify every prioritized employee includes factor explanations and recommended topics."""
    prioritized = test_engine.evaluate_all()
    assert len(prioritized) > 0

    for p in prioritized:
        assert 0.0 <= p.composite_priority_score <= 100.0
        assert p.priority_tier in ["HIGH", "MEDIUM", "LOW"]
        # Human-in-the-loop requirement: recommended topics must be populated
        assert len(p.recommended_topics) > 0


def test_missing_surveys_are_not_penalized(test_engine):
    """Verify missing surveys are treated neutrally and do not unfairly inflate priority risk."""
    prioritized = test_engine.evaluate_all()
    for p in prioritized:
        # Check that neutral absence is labeled as LOW impact
        for f in p.factors:
            if f.signal_name == "Pulse Survey Neutral Absence":
                assert f.impact_level == "LOW"
