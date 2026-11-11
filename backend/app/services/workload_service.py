"""Service for Workload Snapshots and Capacity Strain Monitoring."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.workload_snapshot import WorkloadSnapshot
from backend.app.models.employee import Employee
from backend.app.schemas.workload import WorkloadCreate, WorkloadResponse
from backend.app.services.audit_service import AuditService


class WorkloadService:
    @staticmethod
    def create_snapshot(db: Session, req: WorkloadCreate, performed_by: str) -> WorkloadSnapshot:
        """Record quarterly workload snapshot."""
        emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{req.employee_id}' not found.")

        # Prevent duplicate quarterly snapshot
        existing = db.query(WorkloadSnapshot).filter(
            WorkloadSnapshot.employee_id == req.employee_id,
            WorkloadSnapshot.period_quarter == req.period_quarter
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Workload snapshot for employee '{req.employee_id}' in quarter '{req.period_quarter}' already exists."
            )

        workload_id = req.workload_id
        if not workload_id:
            workload_id = f"WKL-{req.employee_id}-{req.period_quarter}"

        snapshot = WorkloadSnapshot(
            workload_id=workload_id,
            employee_id=req.employee_id,
            period_quarter=req.period_quarter,
            period_date=req.period_date,
            avg_weekly_hours=req.avg_weekly_hours,
            overtime_hours=req.overtime_hours,
            consecutive_overtime_weeks=req.consecutive_overtime_weeks,
            active_project_count=req.active_project_count,
            is_benign_surge=req.is_benign_surge
        )
        db.add(snapshot)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="workload_snapshots",
            entity_id=workload_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"hours": req.avg_weekly_hours, "benign_surge": req.is_benign_surge}
        )

        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def list_snapshots(
        db: Session,
        employee_id: Optional[str] = None,
        period_quarter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkloadResponse]:
        """Retrieve workload history."""
        query = db.query(WorkloadSnapshot)
        if employee_id:
            query = query.filter(WorkloadSnapshot.employee_id == employee_id)
        if period_quarter:
            query = query.filter(WorkloadSnapshot.period_quarter == period_quarter)

        snaps = query.order_by(WorkloadSnapshot.period_date.desc()).offset(offset).limit(limit).all()

        return [
            WorkloadResponse(
                workload_id=w.workload_id,
                employee_id=w.employee_id,
                period_quarter=w.period_quarter,
                period_date=w.period_date,
                avg_weekly_hours=float(w.avg_weekly_hours),
                overtime_hours=float(w.overtime_hours),
                consecutive_overtime_weeks=w.consecutive_overtime_weeks,
                active_project_count=w.active_project_count,
                is_benign_surge=w.is_benign_surge,
                created_at=w.created_at
            )
            for w in snaps
        ]
