"""Tests for Data Validator and Anomaly Auditing."""
import pytest
from backend.app.services.generator import SyntheticDataGenerator
from backend.app.services.validator import DataValidator


@pytest.fixture
def generated_data():
    gen = SyntheticDataGenerator(seed=20261022, scale=100)
    gen.generate_all()
    return {
        "teams": gen.teams,
        "compensation_bands": gen.bands,
        "roles": gen.roles,
        "employees": gen.employees,
        "tenure_snapshots": gen.tenure_snapshots,
        "workload_snapshots": gen.workload_snapshots,
        "engagement_surveys": gen.engagement_surveys,
        "promotion_histories": gen.promotion_histories,
        "attrition_outcomes": gen.attrition_outcomes,
        "interventions": gen.interventions,
        "ground_truth_anomalies": gen.ground_truth_anomalies,
    }


def test_validation_integrity_and_anomaly_detection(generated_data):
    validator = DataValidator(generated_data)
    report = validator.run_all_validations()

    # Core integrity must pass
    pk_check = next(c for c in report.check_results if c.check_name == "primary_key_uniqueness")
    assert pk_check.passed is True

    fk_check = next(c for c in report.check_results if c.check_name == "foreign_key_integrity")
    assert fk_check.passed is True

    # Injected anomalies must be detected
    leak_check = next(c for c in report.check_results if c.check_name == "temporal_boundary_future_leakage")
    assert leak_check.anomaly_type_detected == "FUTURE_INFO_LEAK"

    neutrality_check = next(c for c in report.check_results if c.check_name == "missing_survey_neutrality")
    assert neutrality_check.anomaly_type_detected == "MISSING_SURVEY_PUNITIVE"

    outcome_check = next(c for c in report.check_results if c.check_name == "outcome_lifecycle_consistency")
    assert outcome_check.anomaly_type_detected == "OUTCOME_DATE_MISMATCH"

    explain_check = next(c for c in report.check_results if c.check_name == "intervention_human_explainability")
    assert explain_check.anomaly_type_detected == "UNEXPLAINED_SCORE"

    # Perfect recall on ground truth
    assert report.ground_truth_reconciliation["recall_score"] == 1.0
