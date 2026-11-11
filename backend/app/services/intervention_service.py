"""Service for Supportive Interventions and Lifecycle Event History."""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.intervention import Intervention
from backend.app.models.intervention_event import InterventionEvent
from backend.app.models.employee import Employee
from backend.app.schemas.intervention import (
    InterventionCreate, InterventionUpdate, InterventionStatusUpdate,
    InterventionOutcomeUpdate, InterventionEventCreate, InterventionResponse,
    InterventionDetailResponse, InterventionEventResponse
)
from backend.app.services.audit_service import AuditService


class InterventionService:
    @staticmethod
    def create_intervention(
        db: Session,
        req: InterventionCreate,
        performed_by: str
    ) -> Intervention:
        """Create new supportive retention intervention with mandatory human review notes."""
        if not req.discussion_summary or len(req.discussion_summary.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Human review required: discussion summary must contain actionable notes from supportive conversation."
            )

        if "AUTOMATED_TRIGGER_NO_REVIEW" in req.discussion_summary:
            raise HTTPException(
                status_code=400,
                detail="Compliance violation: retention interventions cannot be logged automatically without human manager review."
            )

        emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{req.employee_id}' not found.")

        conductor = db.query(Employee).filter(Employee.employee_id == req.conducted_by_id).first()
        if not conductor:
            raise HTTPException(status_code=404, detail=f"Conductor employee '{req.conducted_by_id}' not found.")

        count = db.query(Intervention).count() + 1
        intervention_id = f"INT-2026-{count:06d}"

        intervention = Intervention(
            intervention_id=intervention_id,
            employee_id=req.employee_id,
            conducted_by_id=req.conducted_by_id,
            intervention_date=req.intervention_date,
            intervention_type=req.intervention_type,
            discussion_summary=req.discussion_summary,
            agreed_actions=req.agreed_actions,
            follow_up_date=req.follow_up_date,
            status=req.status or "SCHEDULED",
            simulated_outcome="RETENTION_REINFORCED"
        )
        db.add(intervention)
        db.flush()

        # Log initial event
        event_count = db.query(InterventionEvent).count() + 1
        init_event = InterventionEvent(
            event_id=f"INTEV-2026-{event_count:06d}",
            intervention_id=intervention_id,
            event_type="CREATED",
            event_timestamp=datetime.utcnow(),
            actor_id=req.conducted_by_id,
            notes="Initial supportive intervention scheduled."
        )
        db.add(init_event)

        AuditService.log_action(
            db=db,
            entity_name="interventions",
            entity_id=intervention_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"employee_id": req.employee_id, "type": req.intervention_type}
        )

        db.commit()
        db.refresh(intervention)
        return intervention

    @staticmethod
    def get_intervention_detail(db: Session, intervention_id: str) -> InterventionDetailResponse:
        """Fetch intervention details and its complete event history."""
        i = db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()
        if not i:
            raise HTTPException(status_code=404, detail=f"Intervention '{intervention_id}' not found.")

        events = db.query(InterventionEvent).filter(
            InterventionEvent.intervention_id == intervention_id
        ).order_by(InterventionEvent.event_timestamp.asc()).all()

        event_schemas = [
            InterventionEventResponse(
                event_id=e.event_id,
                intervention_id=e.intervention_id,
                event_type=e.event_type,
                event_timestamp=e.event_timestamp,
                actor_id=e.actor_id,
                actor_name=e.actor.full_name if e.actor else "Unknown",
                notes=e.notes
            )
            for e in events
        ]

        return InterventionDetailResponse(
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
            created_at=i.created_at,
            events=event_schemas
        )

    @staticmethod
    def list_interventions(
        db: Session,
        employee_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InterventionResponse], int]:
        """List interventions with pagination."""
        query = db.query(Intervention)
        if employee_id:
            query = query.filter(Intervention.employee_id == employee_id)
        if status_filter:
            query = query.filter(Intervention.status == status_filter)

        total = query.count()
        items = query.order_by(Intervention.intervention_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

        results = [
            InterventionResponse(
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
            for i in items
        ]
        return results, total

    @staticmethod
    def update_status(
        db: Session,
        intervention_id: str,
        req: InterventionStatusUpdate,
        actor_id: str,
        performed_by: str
    ) -> Intervention:
        """Update intervention lifecycle status and append event."""
        i = db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()
        if not i:
            raise HTTPException(status_code=404, detail=f"Intervention '{intervention_id}' not found.")

        old_status = i.status
        i.status = req.status

        # Create event
        event_count = db.query(InterventionEvent).count() + 1
        ev_type = "ACTION_COMPLETED" if req.status == "COMPLETED" else ("CANCELLED" if req.status == "CANCELLED" else "NOTES_UPDATED")
        event = InterventionEvent(
            event_id=f"INTEV-2026-{event_count:06d}",
            intervention_id=intervention_id,
            event_type=ev_type,
            event_timestamp=datetime.utcnow(),
            actor_id=actor_id,
            notes=req.notes or f"Status transitioned from {old_status} to {req.status}"
        )
        db.add(event)

        AuditService.log_action(
            db=db,
            entity_name="interventions",
            entity_id=intervention_id,
            action="UPDATE",
            performed_by=performed_by,
            changes={"old_status": old_status, "new_status": req.status}
        )

        db.commit()
        db.refresh(i)
        return i

    @staticmethod
    def update_outcome(
        db: Session,
        intervention_id: str,
        req: InterventionOutcomeUpdate,
        actor_id: str,
        performed_by: str
    ) -> Intervention:
        """Update simulated outcome and append event."""
        i = db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()
        if not i:
            raise HTTPException(status_code=404, detail=f"Intervention '{intervention_id}' not found.")

        old_outcome = i.simulated_outcome
        i.simulated_outcome = req.simulated_outcome

        event_count = db.query(InterventionEvent).count() + 1
        event = InterventionEvent(
            event_id=f"INTEV-2026-{event_count:06d}",
            intervention_id=intervention_id,
            event_type="NOTES_UPDATED",
            event_timestamp=datetime.utcnow(),
            actor_id=actor_id,
            notes=req.notes or f"Outcome evaluated as {req.simulated_outcome}"
        )
        db.add(event)

        AuditService.log_action(
            db=db,
            entity_name="interventions",
            entity_id=intervention_id,
            action="UPDATE",
            performed_by=performed_by,
            changes={"old_outcome": old_outcome, "new_outcome": req.simulated_outcome}
        )

        db.commit()
        db.refresh(i)
        return i

    @staticmethod
    def add_event(
        db: Session,
        intervention_id: str,
        req: InterventionEventCreate,
        performed_by: str
    ) -> InterventionEvent:
        """Append an event to an existing intervention."""
        i = db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()
        if not i:
            raise HTTPException(status_code=404, detail=f"Intervention '{intervention_id}' not found.")

        event_count = db.query(InterventionEvent).count() + 1
        event_id = f"INTEV-2026-{event_count:06d}"

        event = InterventionEvent(
            event_id=event_id,
            intervention_id=intervention_id,
            event_type=req.event_type,
            event_timestamp=datetime.utcnow(),
            actor_id=req.actor_id,
            notes=req.notes
        )
        db.add(event)

        AuditService.log_action(
            db=db,
            entity_name="intervention_events",
            entity_id=event_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"intervention_id": intervention_id, "event_type": req.event_type}
        )

        db.commit()
        db.refresh(event)
        return event
