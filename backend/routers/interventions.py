"""Supportive Interventions API Router (Human-in-the-Loop)."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Intervention, Employee
from backend.schemas.intervention import InterventionCreate, InterventionResponse
from backend.schemas.common import APIResponse, PaginatedResponse
from backend.services.store import store_coordinator

router = APIRouter(prefix="/interventions", tags=["Supportive Interventions"])


@router.get("", response_model=APIResponse[PaginatedResponse[InterventionResponse]])
def list_interventions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List logged supportive retention check-ins."""
    query = db.query(Intervention).order_by(Intervention.intervention_date.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    results = []
    for i in items:
        resp = InterventionResponse(
            intervention_id=i.intervention_id,
            employee_id=i.employee_id,
            employee_name=i.employee.full_name if i.employee else "Unknown",
            conducted_by_id=i.conducted_by_id,
            conducted_by_name=i.conducted_by.full_name if i.conducted_by else "Unknown",
            intervention_date=i.intervention_date,
            intervention_type=i.intervention_type,
            discussion_summary=i.discussion_summary,
            agreed_actions=i.agreed_actions,
            follow_up_date=i.follow_up_date,
            status=i.status,
            simulated_outcome=i.simulated_outcome,
            created_at=i.created_at
        )
        results.append(resp)

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        data=PaginatedResponse(
            items=results,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.post("", response_model=APIResponse[InterventionResponse], status_code=201)
def log_supportive_intervention(
    payload: InterventionCreate,
    db: Session = Depends(get_db)
):
    """Log a human-in-the-loop retention check-in, enforcing explainability & human review."""
    # Policy validation: Reject unexplained or purely automated triggers
    if not payload.discussion_summary or len(payload.discussion_summary.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Human review required: discussion summary must contain actionable notes from supportive conversation."
        )

    if "AUTOMATED_TRIGGER_NO_REVIEW" in payload.discussion_summary:
        raise HTTPException(
            status_code=400,
            detail="Compliance violation: retention interventions cannot be logged automatically without human manager review."
        )

    emp = db.query(Employee).filter(Employee.employee_id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {payload.employee_id} not found.")

    manager = db.query(Employee).filter(Employee.employee_id == payload.conducted_by_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail=f"Manager {payload.conducted_by_id} not found.")

    # Generate deterministic formatted ID
    count = db.query(Intervention).count() + 1
    new_id = f"INT-2026-{count:06d}"

    intervention = Intervention(
        intervention_id=new_id,
        employee_id=payload.employee_id,
        conducted_by_id=payload.conducted_by_id,
        intervention_date=payload.intervention_date,
        intervention_type=payload.intervention_type,
        discussion_summary=payload.discussion_summary,
        agreed_actions=payload.agreed_actions,
        follow_up_date=payload.follow_up_date,
        status=payload.status,
        simulated_outcome="RETENTION_REINFORCED",
        created_at=datetime.utcnow()
    )

    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    # Refresh in-memory store
    store_coordinator.load_from_db(db)

    return APIResponse(
        success=True,
        message="Supportive retention intervention logged successfully.",
        data=InterventionResponse(
            intervention_id=intervention.intervention_id,
            employee_id=intervention.employee_id,
            employee_name=emp.full_name,
            conducted_by_id=intervention.conducted_by_id,
            conducted_by_name=manager.full_name,
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
