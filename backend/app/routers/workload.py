"""Workload & Capacity Strain API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import require_roles
from backend.app.schemas.workload import WorkloadCreate, WorkloadResponse
from backend.app.schemas.common import APIResponse
from backend.app.services.workload_service import WorkloadService

router = APIRouter(prefix="/workload", tags=["Workload & Capacity Strain"])


@router.post("/snapshots", response_model=APIResponse[WorkloadResponse], status_code=status.HTTP_201_CREATED)
def record_workload_snapshot(
    payload: WorkloadCreate,
    current_user: AppUser = Depends(require_roles(UserRole.IT_OPS_PARTNER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Record a quarterly workload and overtime snapshot."""
    snapshot = WorkloadService.create_snapshot(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Workload snapshot '{snapshot.workload_id}' recorded successfully.",
        data=WorkloadResponse.model_validate(snapshot)
    )


@router.get("/snapshots", response_model=APIResponse[List[WorkloadResponse]])
def list_workload_snapshots(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    period_quarter: Optional[str] = Query(None, description="Filter by quarter (e.g. 2026Q1)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve historical workload and capacity records."""
    snapshots = WorkloadService.list_snapshots(
        db=db,
        employee_id=employee_id,
        period_quarter=period_quarter,
        limit=limit,
        offset=offset
    )
    return APIResponse(
        success=True,
        message=f"Retrieved {len(snapshots)} workload snapshots.",
        data=snapshots
    )
