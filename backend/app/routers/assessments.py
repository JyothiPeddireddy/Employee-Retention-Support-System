"""Retention Support Assessments API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import get_current_user, require_roles, check_employee_access
from backend.app.schemas.assessment import (
    AssessmentGenerateRequest, SupportAssessmentDetailResponse, AnalysisRunResponse
)
from backend.app.schemas.common import APIResponse
from backend.app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["Retention Support Assessments"])


@router.post("/generate", response_model=APIResponse[AnalysisRunResponse], status_code=status.HTTP_201_CREATED)
def generate_assessments(
    payload: AssessmentGenerateRequest,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Execute explainable supportive assessment rules using PostgreSQL records up to strict observation cutoff."""
    run = AssessmentService.generate_assessments(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Analysis run '{run.analysis_id}' executed successfully with {run.high_priority_count} high-priority signals.",
        data=AnalysisRunResponse.model_validate(run)
    )


@router.get("/runs", response_model=APIResponse[List[AnalysisRunResponse]])
def list_analysis_runs(
    limit: int = Query(20, ge=1, le=100),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List historical analysis runs."""
    runs = AssessmentService.list_runs(db=db, limit=limit)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(runs)} past analysis runs.",
        data=runs
    )


@router.get("", response_model=APIResponse[List[SupportAssessmentDetailResponse]])
def list_assessments(
    analysis_id: Optional[str] = Query(None, description="Filter by analysis run ID"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    tier: Optional[str] = Query(None, description="Filter by priority tier (HIGH, MEDIUM, LOW)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List support assessments with explainability factors and data completeness."""
    assessments = AssessmentService.list_assessments(
        db=db,
        analysis_id=analysis_id,
        employee_id=employee_id,
        tier=tier,
        limit=limit,
        offset=offset
    )
    return APIResponse(
        success=True,
        message=f"Retrieved {len(assessments)} support assessments.",
        data=assessments
    )


@router.get("/{assessment_id}", response_model=APIResponse[SupportAssessmentDetailResponse])
def get_assessment_detail(
    assessment_id: str,
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve full factor breakdown and actionable topics for a single assessment."""
    detail = AssessmentService.get_assessment(db=db, assessment_id=assessment_id)
    return APIResponse(
        success=True,
        message=f"Assessment '{assessment_id}' retrieved.",
        data=detail
    )


@router.get("/employee/{employee_id}", response_model=APIResponse[List[SupportAssessmentDetailResponse]])
def get_employee_assessments(
    employee_id: str,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve assessments for an individual employee with access verification."""
    check_employee_access(current_user=current_user, target_employee_id=employee_id, db=db)
    assessments = AssessmentService.list_assessments(db=db, employee_id=employee_id)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(assessments)} assessments for employee '{employee_id}'.",
        data=assessments
    )
