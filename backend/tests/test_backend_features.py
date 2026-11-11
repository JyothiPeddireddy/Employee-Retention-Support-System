"""Comprehensive functional tests for all backend services and API modules on PostgreSQL."""
import pytest
from datetime import date, datetime
from fastapi import HTTPException
from backend.app.models import (
    Employee, Team, Role, CompensationBand, TeamMembershipHistory,
    EngagementSurvey, WorkloadSnapshot, PromotionHistory, Intervention,
    InterventionEvent, AppUser, UserRole
)
from backend.app.schemas.employee import EmployeeCreate, EmployeeUpdate
from backend.app.schemas.team_role import TeamCreate, TeamTransferRequest, RoleCreate
from backend.app.schemas.engagement import SurveyCreate, SurveyUpdate
from backend.app.schemas.workload import WorkloadCreate
from backend.app.schemas.compensation import BandCreate, PromotionCreate
from backend.app.schemas.assessment import AssessmentGenerateRequest
from backend.app.schemas.intervention import (
    InterventionCreate, InterventionStatusUpdate, InterventionOutcomeUpdate, InterventionEventCreate
)
from backend.app.schemas.admin import UserRoleUpdateRequest
from backend.app.services.employee_service import EmployeeService
from backend.app.services.team_service import TeamService, RoleService
from backend.app.services.engagement_service import EngagementService
from backend.app.services.workload_service import WorkloadService
from backend.app.services.compensation_service import CompensationService
from backend.app.services.assessment_service import AssessmentService
from backend.app.services.intervention_service import InterventionService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.data_quality_service import DataQualityService


def test_employee_crud_and_search(db_session, seeded_db):
    """Test creating, listing, searching, filtering, and updating employee records."""
    # 1. Create employee
    create_req = EmployeeCreate(
        employee_id="EMP-TEST-9999",
        first_name="Jordan",
        last_name="Rivers",
        email="jordan.rivers@company.internal",
        role_id="ROLE-IC1-SWE",
        team_id="TEAM-ENG-01",
        hire_date=date(2025, 1, 1),
        current_salary=80000.0,
        status="ACTIVE"
    )
    emp = EmployeeService.create_employee(db=db_session, req=create_req, performed_by="USR-000001")
    assert emp.employee_id == "EMP-TEST-9999"
    assert emp.full_name == "Jordan Rivers"

    # Initial team membership created automatically
    membership = db_session.query(TeamMembershipHistory).filter(
        TeamMembershipHistory.employee_id == "EMP-TEST-9999"
    ).first()
    assert membership is not None
    assert membership.is_current is True

    # 2. Search employee
    items, total = EmployeeService.list_employees(db=db_session, search="Rivers")
    assert total >= 1
    assert any(e.employee_id == "EMP-TEST-9999" for e in items)

    # 3. Update employee
    update_req = EmployeeUpdate(current_salary=88000.0)
    updated = EmployeeService.update_employee(
        db=db_session,
        employee_id="EMP-TEST-9999",
        req=update_req,
        performed_by="USR-000001"
    )
    assert float(updated.current_salary) == 88000.0


def test_team_effective_dated_transfer_preserves_history(db_session, seeded_db):
    """Test transferring an employee between teams while preserving historical membership records."""
    emp_id = "EMP-000001"
    emp = db_session.query(Employee).filter(Employee.employee_id == emp_id).first()
    initial_team_id = emp.current_team_id

    # Transfer to a different team
    target_team = "TEAM-ENG-02" if initial_team_id != "TEAM-ENG-02" else "TEAM-ENG-03"
    transfer_req = TeamTransferRequest(
        employee_id=emp_id,
        target_team_id=target_team,
        effective_date=date(2026, 4, 1),
        transfer_reason="Strategic project reassignment"
    )
    new_mem = TeamService.transfer_employee_team(
        db=db_session,
        req=transfer_req,
        performed_by="USR-000001"
    )

    assert new_mem.is_current is True
    assert new_mem.team_id == target_team
    assert new_mem.effective_end_date is None

    # Verify previous membership is closed and preserved
    history = db_session.query(TeamMembershipHistory).filter(
        TeamMembershipHistory.employee_id == emp_id
    ).all()
    assert len(history) >= 2
    closed_mem = [m for m in history if not m.is_current]
    assert len(closed_mem) >= 1
    assert closed_mem[-1].effective_end_date == date(2026, 4, 1)


def test_engagement_survey_neutrality_and_composite(db_session, seeded_db):
    """Test survey creation enforcing strict neutrality, and composite score computation."""
    emp_id = "EMP-000001"

    # 1. Valid active survey with sentiment dimensions
    active_req = SurveyCreate(
        survey_id="SURV-TEST-0001",
        employee_id=emp_id,
        survey_quarter="2026Q2",
        survey_date=date(2026, 6, 30),
        is_missing=False,
        satisfaction_score=4.0,
        work_life_balance_score=3.5,
        career_growth_score=4.5,
        manager_support_score=4.0
    )
    survey = EngagementService.create_survey(db=db_session, req=active_req, performed_by="USR-000001")
    assert float(survey.composite_engagement) == 4.0

    # 2. Missing survey: neutrality enforced (scores must be None)
    missing_req = SurveyCreate(
        survey_id="SURV-TEST-0002",
        employee_id=emp_id,
        survey_quarter="2026Q3",
        survey_date=date(2026, 9, 30),
        is_missing=True
    )
    m_survey = EngagementService.create_survey(db=db_session, req=missing_req, performed_by="USR-000001")
    assert m_survey.is_missing is True
    assert m_survey.satisfaction_score is None
    assert m_survey.composite_engagement is None


def test_workload_recording_and_overtime(db_session, seeded_db):
    """Test workload snapshot recording and overtime tracking."""
    emp_id = "EMP-000001"
    workload_req = WorkloadCreate(
        workload_id=f"WKL-{emp_id}-2026Q2",
        employee_id=emp_id,
        period_quarter="2026Q2",
        period_date=date(2026, 6, 30),
        avg_weekly_hours=48.5,
        overtime_hours=8.5,
        consecutive_overtime_weeks=5,
        active_project_count=3,
        is_benign_surge=False
    )
    wkl = WorkloadService.create_snapshot(db=db_session, req=workload_req, performed_by="USR-000001")
    assert float(wkl.avg_weekly_hours) == 48.5
    assert float(wkl.overtime_hours) == 8.5
    assert wkl.is_benign_surge is False


def test_compensation_band_and_promotion_recording(db_session, seeded_db):
    """Test compensation band creation and promotion history recording."""
    band_req = BandCreate(
        band_id="BAND-TEST-M3",
        name="Senior Director",
        min_salary=200000.0,
        mid_salary=240000.0,
        max_salary=290000.0
    )
    band = CompensationService.create_band(db=db_session, req=band_req, performed_by="USR-000001")
    assert band.band_id == "BAND-TEST-M3"

    # Promotion recording
    emp_id = "EMP-000001"
    prom_req = PromotionCreate(
        promotion_id="PROM-TEST-0001",
        employee_id=emp_id,
        effective_date=date(2026, 5, 1),
        from_role_id="ROLE-IC1-SWE",
        to_role_id="ROLE-IC2-SWE",
        from_salary=80000.0,
        to_salary=95000.0,
        movement_type="PROMOTION"
    )
    prom = CompensationService.record_promotion(db=db_session, req=prom_req, performed_by="USR-000001")
    assert prom.promotion_id == "PROM-TEST-0001"

    # Verify employee's salary and role updated
    emp = db_session.query(Employee).filter(Employee.employee_id == emp_id).first()
    assert float(emp.current_salary) == 95000.0
    assert emp.current_role_id == "ROLE-IC2-SWE"


def test_support_assessment_generation_and_explainability(db_session, seeded_db):
    """Test explainable supportive assessment rules adhering to pre-outcome observation cutoff."""
    req = AssessmentGenerateRequest(
        cutoff_date=date(2025, 12, 31)
    )
    run = AssessmentService.generate_assessments(db=db_session, req=req, performed_by="USR-000001")
    assert run.analysis_id.startswith("ARUN-")
    assert run.cohort_size > 0
    assert run.status == "COMPLETED"

    # Fetch assessment details
    assessments = AssessmentService.list_assessments(db=db_session, analysis_id=run.analysis_id)
    assert len(assessments) > 0

    first = assessments[0]
    assert first.priority_tier in ["HIGH", "MEDIUM", "LOW"]
    assert 0.0 <= first.composite_priority_score <= 100.0
    assert len(first.recommended_topics) > 0
    assert first.data_completeness_percentage > 0


def test_intervention_lifecycle_and_event_trail(db_session, seeded_db):
    """Test supportive intervention creation, human review validation, status transition, and event tracking."""
    # 1. Rejection of unreviewed or automated trigger
    bad_req = InterventionCreate(
        employee_id="EMP-000001",
        conducted_by_id="EMP-000002",
        intervention_date=date(2026, 3, 1),
        intervention_type="1_ON_1_CAREER_CHECKIN",
        discussion_summary="AUTOMATED_TRIGGER_NO_REVIEW"
    )
    with pytest.raises(HTTPException) as exc_info:
        InterventionService.create_intervention(db=db_session, req=bad_req, performed_by="USR-000001")
    assert exc_info.value.status_code == 400

    # 2. Legitimate human check-in
    valid_req = InterventionCreate(
        employee_id="EMP-000001",
        conducted_by_id="EMP-000002",
        intervention_date=date(2026, 3, 1),
        intervention_type="1_ON_1_CAREER_CHECKIN",
        discussion_summary="Held supportive career 1-on-1 discussing upcoming technical leadership opportunities and workload distribution.",
        agreed_actions="Transition to tech lead for upcoming platform migration.",
        follow_up_date=date(2026, 4, 15)
    )
    intervention = InterventionService.create_intervention(db=db_session, req=valid_req, performed_by="USR-000001")
    int_id = intervention.intervention_id
    assert int_id.startswith("INT-")
    assert intervention.status == "SCHEDULED"

    # 3. Status transition with event logging
    status_req = InterventionStatusUpdate(status="COMPLETED", notes="Follow-up discussion concluded successfully.")
    updated = InterventionService.update_status(
        db=db_session,
        intervention_id=int_id,
        req=status_req,
        actor_id="EMP-000002",
        performed_by="USR-000001"
    )
    assert updated.status == "COMPLETED"

    # 4. Outcome update
    outcome_req = InterventionOutcomeUpdate(simulated_outcome="RETENTION_REINFORCED")
    updated_out = InterventionService.update_outcome(
        db=db_session,
        intervention_id=int_id,
        req=outcome_req,
        actor_id="EMP-000002",
        performed_by="USR-000001"
    )
    assert updated_out.simulated_outcome == "RETENTION_REINFORCED"

    # 5. Verify full event trail
    detail = InterventionService.get_intervention_detail(db=db_session, intervention_id=int_id)
    assert len(detail.events) >= 3


def test_analytics_and_data_quality_services(db_session, seeded_db):
    """Test analytics overview, department aggregations, and automated validation suite."""
    # 1. Overview metrics
    metrics = AnalyticsService.get_overview_metrics(db=db_session)
    assert metrics.total_headcount > 0
    assert metrics.active_headcount > 0
    assert metrics.avg_weekly_workload > 0

    # 2. Department summary
    dept_summaries = AnalyticsService.get_team_summaries(db=db_session)
    assert len(dept_summaries) > 0
    assert any(d.department == "Engineering" for d in dept_summaries)

    # 3. Data quality validation run
    val_run = DataQualityService.run_full_validation(db=db_session, seed=20261022, performed_by="USR-000001")
    assert val_run.run_id.startswith("VRUN-")
    assert val_run.total_checks > 0
    assert val_run.passed_checks > 0
