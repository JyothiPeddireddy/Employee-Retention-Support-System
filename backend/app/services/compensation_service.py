"""Service for Compensation Bands, Equity, and Career Promotions."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.compensation_band import CompensationBand
from backend.app.models.promotion_history import PromotionHistory
from backend.app.models.employee import Employee
from backend.app.models.role import Role
from backend.app.schemas.compensation import (
    BandCreate, BandUpdate, BandResponse, PromotionCreate, PromotionResponse
)
from backend.app.services.audit_service import AuditService


class CompensationService:
    @staticmethod
    def create_band(db: Session, req: BandCreate, performed_by: str) -> CompensationBand:
        """Create new standard compensation band."""
        if db.query(CompensationBand).filter(CompensationBand.band_id == req.band_id).first():
            raise HTTPException(status_code=400, detail=f"Band ID '{req.band_id}' already exists.")

        if req.min_salary >= req.max_salary:
            raise HTTPException(status_code=400, detail="min_salary must be strictly less than max_salary.")

        band = CompensationBand(
            band_id=req.band_id,
            name=getattr(req, "name", f"{req.band_id} Band"),
            min_salary=req.min_salary,
            mid_salary=req.mid_salary,
            max_salary=req.max_salary,
            currency=req.currency or "USD"
        )
        db.add(band)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="compensation_bands",
            entity_id=req.band_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"min": req.min_salary, "mid": req.mid_salary, "max": req.max_salary}
        )

        db.commit()
        db.refresh(band)
        return band

    @staticmethod
    def list_bands(db: Session, department: Optional[str] = None) -> List[BandResponse]:
        """List compensation bands."""
        query = db.query(CompensationBand)
        if department:
            query = query.filter(CompensationBand.name.ilike(f"%{department}%") | CompensationBand.band_id.ilike(f"%{department}%"))
        bands = query.all()
        return [
            BandResponse(
                band_id=b.band_id,
                name=b.name,
                min_salary=float(b.min_salary),
                mid_salary=float(b.mid_salary),
                max_salary=float(b.max_salary),
                currency=b.currency
            )
            for b in bands
        ]

    @staticmethod
    def update_band(db: Session, band_id: str, req: BandUpdate, performed_by: str) -> CompensationBand:
        """Update an existing compensation band."""
        band = db.query(CompensationBand).filter(CompensationBand.band_id == band_id).first()
        if not band:
            raise HTTPException(status_code=404, detail=f"Compensation band '{band_id}' not found.")

        changes = {}
        if req.name is not None:
            changes["name"] = req.name
            band.name = req.name
        if req.min_salary is not None:
            changes["min_salary"] = req.min_salary
            band.min_salary = req.min_salary
        if req.mid_salary is not None:
            changes["mid_salary"] = req.mid_salary
            band.mid_salary = req.mid_salary
        if req.max_salary is not None:
            changes["max_salary"] = req.max_salary
            band.max_salary = req.max_salary
        if req.currency is not None:
            changes["currency"] = req.currency
            band.currency = req.currency

        if band.min_salary >= band.max_salary:
            raise HTTPException(status_code=400, detail="min_salary must be strictly less than max_salary.")

        AuditService.log_action(
            db=db,
            entity_name="compensation_bands",
            entity_id=band_id,
            action="UPDATE",
            performed_by=performed_by,
            changes=changes
        )

        db.commit()
        db.refresh(band)
        return band

    @staticmethod
    def record_promotion(db: Session, req: PromotionCreate, performed_by: str) -> PromotionHistory:
        """Record career promotion or lateral transition and update employee profile."""
        emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{req.employee_id}' not found.")

        to_role = db.query(Role).filter(Role.role_id == req.to_role_id).first()
        if not to_role:
            raise HTTPException(status_code=404, detail=f"Target role '{req.to_role_id}' not found.")

        prom_id = req.promotion_id
        if not prom_id:
            count = db.query(PromotionHistory).count() + 1
            prom_id = f"PROM-{count:06d}"

        prom = PromotionHistory(
            promotion_id=prom_id,
            employee_id=req.employee_id,
            effective_date=req.effective_date,
            from_role_id=req.from_role_id,
            to_role_id=req.to_role_id,
            from_salary=req.from_salary,
            to_salary=req.to_salary,
            movement_type=req.movement_type
        )
        db.add(prom)

        # Update employee's current role and salary
        emp.current_role_id = req.to_role_id
        emp.current_salary = req.to_salary
        db.add(emp)

        AuditService.log_action(
            db=db,
            entity_name="promotion_history",
            entity_id=prom_id,
            action="INSERT",
            performed_by=performed_by,
            changes={
                "employee_id": req.employee_id,
                "from_role": req.from_role_id,
                "to_role": req.to_role_id,
                "new_salary": req.to_salary
            }
        )

        db.commit()
        db.refresh(prom)
        return prom

    @staticmethod
    def list_promotions(
        db: Session,
        employee_id: Optional[str] = None
    ) -> List[PromotionResponse]:
        """List career promotion history."""
        query = db.query(PromotionHistory)
        if employee_id:
            query = query.filter(PromotionHistory.employee_id == employee_id)
        proms = query.order_by(PromotionHistory.effective_date.desc()).all()
        return [
            PromotionResponse(
                promotion_id=p.promotion_id,
                employee_id=p.employee_id,
                effective_date=p.effective_date,
                from_role_id=p.from_role_id,
                to_role_id=p.to_role_id,
                from_salary=float(p.from_salary),
                to_salary=float(p.to_salary),
                movement_type=p.movement_type,
                created_at=p.created_at
            )
            for p in proms
        ]
