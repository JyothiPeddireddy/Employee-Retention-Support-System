"""Unit and functional tests for API endpoints and routers."""
import pytest
from backend.main import health_check
from backend.routers.employees import get_prioritized_retention_list, get_prioritization_summary, get_employee_longitudinal_timeline
from backend.routers.audit import run_and_get_validation_report, get_ground_truth_anomalies, get_metrics_overview
from backend.routers.interventions import list_interventions, log_supportive_intervention
from backend.schemas.intervention import InterventionCreate
from backend.database import SessionLocal
from backend.services.store import store_coordinator
from fastapi import HTTPException


@pytest.fixture(scope="session", autouse=True)
def init_store():
    store_coordinator.initialize(scale=100)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_health_check_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert "Supportive Retention Signal Engine" in res["service"]


def test_prioritized_retention_list_endpoint():
    res = get_prioritized_retention_list(page=1, page_size=10)
    assert res.success is True
    assert len(res.data.items) <= 10
    assert res.data.total > 0
    # Verify explainability on first candidate
    first = res.data.items[0]
    assert first.priority_tier in ["HIGH", "MEDIUM", "LOW"]
    assert len(first.factors) > 0
    assert len(first.recommended_topics) > 0


def test_prioritization_summary_endpoint():
    res = get_prioritization_summary()
    assert res.success is True
    assert res.data.total_evaluated > 0
    assert (res.data.high_priority_count + res.data.medium_priority_count + res.data.low_priority_count) == res.data.total_evaluated


def test_employee_timeline_endpoint(db_session):
    # Fetch first employee
    first_emp = store_coordinator.raw_data["employees"][0]
    eid = first_emp["employee_id"]
    res = get_employee_longitudinal_timeline(eid, db_session)
    assert res.success is True
    assert res.data.employee.employee_id == eid
    assert len(res.data.tenure_history) > 0
    assert len(res.data.workload_history) > 0
    assert len(res.data.survey_history) > 0


def test_audit_validation_report_endpoint():
    res = run_and_get_validation_report()
    assert res.success is True
    assert res.data.total_checks == 8
    assert res.data.ground_truth_reconciliation["recall_score"] == 1.0


def test_ground_truth_anomalies_endpoint(db_session):
    res = get_ground_truth_anomalies(db_session)
    assert res.success is True
    assert len(res.data) > 0


def test_metrics_overview_endpoint(db_session):
    res = get_metrics_overview(db_session)
    assert res.success is True
    assert res.data.total_employees > 0
    assert res.data.data_integrity_score > 0.0


def test_log_intervention_human_explainability_enforcement(db_session):
    # 1. Negative test: automated trigger without human explanation should raise 400
    bad_payload = InterventionCreate(
        employee_id="EMP-000001",
        conducted_by_id="EMP-000002",
        intervention_date="2026-03-01",
        intervention_type="1_ON_1_CAREER_CHECKIN",
        discussion_summary="AUTOMATED_TRIGGER_NO_REVIEW"
    )
    with pytest.raises(HTTPException) as exc_info:
        log_supportive_intervention(bad_payload, db_session)
    assert exc_info.value.status_code == 400
    assert "Compliance violation" in exc_info.value.detail

    # 2. Positive test: legitimate supportive check-in with discussion summary
    valid_payload = InterventionCreate(
        employee_id="EMP-000001",
        conducted_by_id="EMP-000002",
        intervention_date="2026-03-01",
        intervention_type="1_ON_1_CAREER_CHECKIN",
        discussion_summary="Held supportive 1-on-1 discussing recent project deadlines and career milestones. Rebalanced sprint commitments.",
        agreed_actions="Offload secondary on-call rotation for next two sprints.",
        follow_up_date="2026-04-01"
    )
    res = log_supportive_intervention(valid_payload, db_session)
    assert res.success is True
    assert res.data.employee_id == "EMP-000001"
    assert res.data.status == "SCHEDULED"
