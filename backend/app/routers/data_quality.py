"""Data Quality, Validation & Ground Truth API Router."""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.models.validation import GroundTruthAnomaly
from backend.app.core.dependencies import require_roles
from backend.app.schemas.data_quality import (
    ValidationRunCreate, ValidationRunResponse, ValidationIssueResponse
)
from backend.app.schemas.audit import GroundTruthAnomalySchema
from backend.app.schemas.common import APIResponse
from backend.app.services.data_quality_service import DataQualityService

router = APIRouter(prefix="/data-quality", tags=["Data Quality & Integrity Suite"])


@router.post("/validate", response_model=APIResponse[ValidationRunResponse], status_code=status.HTTP_201_CREATED)
def trigger_validation_run(
    payload: ValidationRunCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Trigger automated validation run verifying temporal constraints, neutrality, and relational consistency."""
    run = DataQualityService.run_full_validation(
        db=db,
        seed=payload.seed or 20261022,
        performed_by=current_user.user_id
    )
    issues = DataQualityService.get_run_issues(db=db, run_id=run.run_id)

    return APIResponse(
        success=True,
        message=f"Validation run '{run.run_id}' completed with status: {run.status}.",
        data=ValidationRunResponse(
            run_id=run.run_id,
            run_timestamp=run.run_timestamp,
            dataset_version=run.dataset_version,
            seed_used=run.seed_used,
            total_checks=run.total_checks,
            passed_checks=run.passed_checks,
            failed_checks=run.failed_checks,
            status=run.status,
            issues=issues
        )
    )


@router.get("/runs", response_model=APIResponse[List[ValidationRunResponse]])
def list_validation_runs(
    limit: int = Query(20, ge=1, le=100),
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List historical data quality validation runs."""
    runs = DataQualityService.list_validation_runs(db=db, limit=limit)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(runs)} validation runs.",
        data=runs
    )


@router.get("/runs/{run_id}/issues", response_model=APIResponse[List[ValidationIssueResponse]])
def get_run_issues(
    run_id: str,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve issues identified during a specific validation run."""
    issues = DataQualityService.get_run_issues(db=db, run_id=run_id)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(issues)} issues for run '{run_id}'.",
        data=issues
    )


@router.get("/ground-truth", response_model=APIResponse[List[GroundTruthAnomalySchema]])
def get_ground_truth_anomalies(
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Fetch isolated ground-truth anomalies to demonstrate test isolation from model features."""
    anomalies = db.query(GroundTruthAnomaly).all()
    results = [GroundTruthAnomalySchema.model_validate(a) for a in anomalies]
    return APIResponse(
        success=True,
        message=f"Retrieved {len(results)} documented ground truth anomalies.",
        data=results
    )
