"""Employee & Prioritized Retention API Router."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import Employee, TenureSnapshot, WorkloadSnapshot, EngagementSurvey, PromotionHistory, AttritionOutcome
from backend.app.schemas.prioritization import PrioritizedEmployee, PrioritizationSummary
from backend.app.schemas.employee import EmployeeTimeline, EmployeeListItem, TenureSnapshotSchema, WorkloadSnapshotSchema, EngagementSurveySchema, PromotionHistorySchema, AttritionOutcomeSchema
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.store import store_coordinator

router = APIRouter(prefix="/employees", tags=["Employees & Retention Workbench"])


@router.get("/prioritized", response_model=APIResponse[PaginatedResponse[PrioritizedEmployee]])
def get_prioritized_retention_list(
    department: Optional[str] = Query(None, description="Filter by department (e.g. Engineering, Sales)"),
    min_tier: Optional[str] = Query(None, description="Minimum priority tier: HIGH, MEDIUM, LOW"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Fetch employees prioritized for supportive retention check-ins with explainability chips."""
    if not store_coordinator.rules_engine:
        store_coordinator.initialize(scale=500)

    dept_val = department if isinstance(department, str) else None
    tier_val = min_tier if isinstance(min_tier, str) else None

    evaluated = store_coordinator.rules_engine.evaluate_all(
        department_filter=dept_val,
        min_tier=tier_val
    )

    total = len(evaluated)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = evaluated[start_idx:end_idx]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message=f"Found {total} prioritized retention candidates.",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get("/summary", response_model=APIResponse[PrioritizationSummary])
def get_prioritization_summary():
    """Summary counts of supportive retention candidates by priority tier."""
    if not store_coordinator.rules_engine:
        store_coordinator.initialize(scale=500)

    all_evaluated = store_coordinator.rules_engine.evaluate_all()
    summary = store_coordinator.rules_engine.get_summary(all_evaluated)
    return APIResponse(success=True, data=summary)


@router.get("/{employee_id}/timeline", response_model=APIResponse[EmployeeTimeline])
def get_employee_longitudinal_timeline(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full 24-month longitudinal history (workload, survey scores, promotions) for 360 review."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

    tenures = db.query(TenureSnapshot).filter(TenureSnapshot.employee_id == employee_id).order_by(TenureSnapshot.snapshot_date).all()
    workloads = db.query(WorkloadSnapshot).filter(WorkloadSnapshot.employee_id == employee_id).order_by(WorkloadSnapshot.period_date).all()
    surveys = db.query(EngagementSurvey).filter(EngagementSurvey.employee_id == employee_id).order_by(EngagementSurvey.survey_date).all()
    promos = db.query(PromotionHistory).filter(PromotionHistory.employee_id == employee_id).order_by(PromotionHistory.effective_date).all()
    outcome = db.query(AttritionOutcome).filter(AttritionOutcome.employee_id == employee_id).first()

    emp_item = EmployeeListItem(
        employee_id=emp.employee_id,
        full_name=emp.full_name,
        email=emp.email,
        team_name=emp.team.name if emp.team else "N/A",
        department=emp.team.department if emp.team else "N/A",
        role_title=emp.role.title if emp.role else "N/A",
        role_level=emp.role.level if emp.role else "N/A",
        hire_date=emp.hire_date,
        current_salary=emp.current_salary,
        status=emp.status
    )

    timeline = EmployeeTimeline(
        employee=emp_item,
        tenure_history=[TenureSnapshotSchema.model_validate(t) for t in tenures],
        workload_history=[WorkloadSnapshotSchema.model_validate(w) for w in workloads],
        survey_history=[EngagementSurveySchema.model_validate(s) for s in surveys],
        promotions=[PromotionHistorySchema.model_validate(p) for p in promos],
        attrition_outcome=AttritionOutcomeSchema.model_validate(outcome) if outcome else None
    )

    return APIResponse(success=True, data=timeline)
