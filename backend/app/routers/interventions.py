"""Supportive Retention Interventions API Router (Human-in-the-Loop)."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import require_roles
from backend.app.schemas.intervention import (
    InterventionCreate, InterventionStatusUpdate, InterventionOutcomeUpdate,
    InterventionEventCreate, InterventionResponse, InterventionDetailResponse,
    InterventionEventResponse
)
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.intervention_service import InterventionService

router = APIRouter(prefix="/interventions", tags=["Supportive Retention Interventions"])


@router.post("", response_model=APIResponse[InterventionResponse], status_code=status.HTTP_201_CREATED)
def log_supportive_intervention(
    payload: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[AppUser] = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN))
):
    """Log a human-in-the-loop retention check-in, enforcing human review and explainability."""
    actor_id = current_user.user_id if isinstance(current_user, AppUser) else "SYSTEM"
    intervention = InterventionService.create_intervention(
        db=db,
        req=payload,
        performed_by=actor_id
    )
    return APIResponse(
        success=True,
        message=f"Intervention '{intervention.intervention_id}' logged successfully.",
        data=InterventionResponse(
            intervention_id=intervention.intervention_id,
            employee_id=intervention.employee_id,
            employee_name=intervention.employee.full_name if intervention.employee else "Unknown",
            conducted_by_id=intervention.conducted_by_id,
            conducted_by_name=intervention.conducted_by.full_name if intervention.conducted_by else "Unknown",
            intervention_date=intervention.intervention_date,
            intervention_type=intervention.intervention_type,
            discussion_summary=intervention.discussion_summary,
            agreed_actions=intervention.agreed_actions,
            follow_up_date=intervention.follow_up_date,
            status=intervention.status,
            simulated_outcome=intervention.simulated_outcome,
            created_at=intervention.created_at
        )
    )


@router.get("", response_model=APIResponse[PaginatedResponse[InterventionResponse]])
def list_interventions(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    status: Optional[str] = Query(None, description="Filter by status (SCHEDULED, COMPLETED, CANCELLED)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List logged supportive retention check-ins with pagination."""
    items, total = InterventionService.list_interventions(
        db=db,
        employee_id=employee_id,
        status_filter=status,
        page=page,
        page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message=f"Retrieved {len(items)} interventions.",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get("/{intervention_id}", response_model=APIResponse[InterventionDetailResponse])
def get_intervention_detail(
    intervention_id: str,
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve full intervention history including all lifecycle events."""
    detail = InterventionService.get_intervention_detail(db=db, intervention_id=intervention_id)
    return APIResponse(
        success=True,
        message=f"Intervention '{intervention_id}' details retrieved.",
        data=detail
    )


@router.put("/{intervention_id}/status", response_model=APIResponse[dict])
def update_intervention_status(
    intervention_id: str,
    payload: InterventionStatusUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update intervention lifecycle status and append event."""
    actor_id = current_user.employee_id or current_user.user_id
    updated = InterventionService.update_status(
        db=db,
        intervention_id=intervention_id,
        req=payload,
        actor_id=actor_id,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Intervention '{intervention_id}' status updated to {updated.status}."
    )


@router.put("/{intervention_id}/outcome", response_model=APIResponse[dict])
def update_intervention_outcome(
    intervention_id: str,
    payload: InterventionOutcomeUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update simulated retention outcome and append event."""
    actor_id = current_user.employee_id or current_user.user_id
    updated = InterventionService.update_outcome(
        db=db,
        intervention_id=intervention_id,
        req=payload,
        actor_id=actor_id,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Intervention '{intervention_id}' outcome updated to {updated.simulated_outcome}."
    )


@router.post("/{intervention_id}/events", response_model=APIResponse[InterventionEventResponse], status_code=status.HTTP_201_CREATED)
def record_intervention_event(
    intervention_id: str,
    payload: InterventionEventCreate,
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.IT_OPS_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Append a lifecycle touchpoint event to an existing intervention."""
    event = InterventionService.add_event(
        db=db,
        intervention_id=intervention_id,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Event '{event.event_id}' recorded on intervention '{intervention_id}'.",
        data=InterventionEventResponse(
            event_id=event.event_id,
            intervention_id=event.intervention_id,
            event_type=event.event_type,
            event_timestamp=event.event_timestamp,
            actor_id=event.actor_id,
            actor_name=event.actor.full_name if event.actor else "Unknown",
            notes=event.notes
        )
    )
