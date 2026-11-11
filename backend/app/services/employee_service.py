"""Service for Employee management, queries, and longitudinal timeline."""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from fastapi import HTTPException, status
from backend.app.models.employee import Employee
from backend.app.models.team import Team
from backend.app.models.role import Role
from backend.app.models.team_membership import TeamMembershipHistory
from backend.app.models.tenure_snapshot import TenureSnapshot
from backend.app.models.workload_snapshot import WorkloadSnapshot
from backend.app.models.engagement_survey import EngagementSurvey
from backend.app.models.promotion_history import PromotionHistory
from backend.app.models.attrition_outcome import AttritionOutcome
from backend.app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeListItem, EmployeeDetail, EmployeeTimeline,
    TenureSnapshotSchema, WorkloadSnapshotSchema, EngagementSurveySchema,
    PromotionHistorySchema, AttritionOutcomeSchema
)
from backend.app.services.audit_service import AuditService


class EmployeeService:
    @staticmethod
    def create_employee(db: Session, req: EmployeeCreate, performed_by: str) -> Employee:
        """Create new employee and initialize current team membership."""
        # Validate team
        team = db.query(Team).filter(Team.team_id == req.team_id).first()
        if not team:
            raise HTTPException(status_code=400, detail=f"Team '{req.team_id}' not found.")

        # Validate role
        role = db.query(Role).filter(Role.role_id == req.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Role '{req.role_id}' not found.")

        # Validate manager if supplied
        if req.manager_id:
            manager = db.query(Employee).filter(Employee.employee_id == req.manager_id).first()
            if not manager:
                raise HTTPException(status_code=400, detail=f"Manager '{req.manager_id}' not found.")

        # ID generation
        if req.employee_id:
            emp_id = req.employee_id
            if db.query(Employee).filter(Employee.employee_id == emp_id).first():
                raise HTTPException(status_code=400, detail=f"Employee ID '{emp_id}' already exists.")
        else:
            count = db.query(Employee).count() + 1
            emp_id = f"EMP-{count:06d}"

        # Email uniqueness
        if db.query(Employee).filter(Employee.email == req.email).first():
            raise HTTPException(status_code=400, detail=f"Email '{req.email}' already exists.")

        emp = Employee(
            employee_id=emp_id,
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            current_role_id=req.role_id,
            current_team_id=req.team_id,
            manager_id=req.manager_id,
            hire_date=req.hire_date,
            current_salary=req.current_salary,
            status=req.status or "ACTIVE"
        )
        db.add(emp)
        db.flush()

        # Create effective-dated team membership record
        membership_id = f"MEM-{emp_id}-001"
        membership = TeamMembershipHistory(
            membership_id=membership_id,
            employee_id=emp_id,
            team_id=req.team_id,
            role_id=req.role_id,
            effective_start_date=req.hire_date,
            effective_end_date=None,
            is_current=True,
            transfer_reason="HIRE"
        )
        db.add(membership)

        AuditService.log_action(
            db=db,
            entity_name="employees",
            entity_id=emp_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"employee_id": emp_id, "name": emp.full_name, "team": team.name}
        )

        db.commit()
        db.refresh(emp)
        return emp

    @staticmethod
    def get_employee_detail(db: Session, employee_id: str) -> EmployeeDetail:
        """Fetch complete employee profile including manager and tenure info."""
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

        latest_tenure = db.query(TenureSnapshot).filter(
            TenureSnapshot.employee_id == employee_id
        ).order_by(TenureSnapshot.snapshot_date.desc()).first()

        manager_name = emp.manager.full_name if emp.manager else None

        return EmployeeDetail(
            employee_id=emp.employee_id,
            full_name=emp.full_name,
            first_name=emp.first_name,
            last_name=emp.last_name,
            email=emp.email,
            team_id=emp.team_id,
            team_name=emp.team.name if emp.team else "N/A",
            department=emp.team.department if emp.team else "N/A",
            role_id=emp.role_id,
            role_title=emp.role.title if emp.role else "N/A",
            role_level=emp.role.level if emp.role else "N/A",
            manager_id=emp.manager_id,
            manager_name=manager_name,
            hire_date=emp.hire_date,
            current_salary=float(emp.current_salary),
            status=emp.status,
            tenure_months=latest_tenure.tenure_months if latest_tenure else 0,
            months_in_role=latest_tenure.months_in_current_role if latest_tenure else 0
        )

    @staticmethod
    def list_employees(
        db: Session,
        department: Optional[str] = None,
        team_id: Optional[str] = None,
        role_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "employee_id",
        sort_order: str = "asc"
    ) -> Tuple[List[EmployeeListItem], int]:
        """Query employees with filtering, searching, and pagination."""
        query = db.query(Employee).join(Employee.team).join(Employee.role)

        if department:
            query = query.filter(Team.department.ilike(f"%{department}%"))
        if team_id:
            query = query.filter(Employee.team_id == team_id)
        if role_id:
            query = query.filter(Employee.role_id == role_id)
        if status_filter:
            query = query.filter(Employee.status == status_filter)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(search_pattern),
                    Employee.last_name.ilike(search_pattern),
                    Employee.email.ilike(search_pattern),
                    Employee.employee_id.ilike(search_pattern)
                )
            )

        total = query.count()

        # Sorting
        sort_column = getattr(Employee, sort_by, Employee.employee_id)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        items = query.offset((page - 1) * page_size).limit(page_size).all()

        results = [
            EmployeeListItem(
                employee_id=e.employee_id,
                full_name=e.full_name,
                email=e.email,
                team_name=e.team.name if e.team else "N/A",
                department=e.team.department if e.team else "N/A",
                role_title=e.role.title if e.role else "N/A",
                role_level=e.role.level if e.role else "N/A",
                hire_date=e.hire_date,
                current_salary=float(e.current_salary),
                status=e.status
            )
            for e in items
        ]
        return results, total

    @staticmethod
    def update_employee(
        db: Session,
        employee_id: str,
        req: EmployeeUpdate,
        performed_by: str
    ) -> Employee:
        """Update mutable employee attributes."""
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

        changes = {}
        if req.first_name is not None and req.first_name != emp.first_name:
            changes["first_name"] = {"from": emp.first_name, "to": req.first_name}
            emp.first_name = req.first_name

        if req.last_name is not None and req.last_name != emp.last_name:
            changes["last_name"] = {"from": emp.last_name, "to": req.last_name}
            emp.last_name = req.last_name

        if req.email is not None and req.email != emp.email:
            existing = db.query(Employee).filter(Employee.email == req.email).first()
            if existing and existing.employee_id != employee_id:
                raise HTTPException(status_code=400, detail=f"Email '{req.email}' is already taken.")
            changes["email"] = {"from": emp.email, "to": req.email}
            emp.email = req.email

        if req.current_salary is not None:
            changes["current_salary"] = {"from": float(emp.current_salary), "to": float(req.current_salary)}
            emp.current_salary = req.current_salary

        if req.status is not None and req.status != emp.status:
            changes["status"] = {"from": emp.status, "to": req.status}
            emp.status = req.status

        if req.role_id is not None and req.role_id != emp.current_role_id:
            role = db.query(Role).filter(Role.role_id == req.role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail=f"Role '{req.role_id}' not found.")
            changes["role_id"] = {"from": emp.current_role_id, "to": req.role_id}
            emp.current_role_id = req.role_id

        if req.manager_id is not None and req.manager_id != emp.manager_id:
            if req.manager_id != "":
                mgr = db.query(Employee).filter(Employee.employee_id == req.manager_id).first()
                if not mgr:
                    raise HTTPException(status_code=400, detail=f"Manager '{req.manager_id}' not found.")
            changes["manager_id"] = {"from": emp.manager_id, "to": req.manager_id}
            emp.manager_id = req.manager_id or None

        if changes:
            AuditService.log_action(
                db=db,
                entity_name="employees",
                entity_id=employee_id,
                action="UPDATE",
                performed_by=performed_by,
                changes=changes
            )

        db.commit()
        db.refresh(emp)
        return emp

    @staticmethod
    def get_timeline(db: Session, employee_id: str) -> EmployeeTimeline:
        """Fetch 24-month longitudinal timeline for 360 review."""
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")

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
            current_salary=float(emp.current_salary),
            status=emp.status
        )

        return EmployeeTimeline(
            employee=emp_item,
            tenure_history=[TenureSnapshotSchema.model_validate(t) for t in tenures],
            workload_history=[WorkloadSnapshotSchema.model_validate(w) for w in workloads],
            survey_history=[EngagementSurveySchema.model_validate(s) for s in surveys],
            promotions=[PromotionHistorySchema.model_validate(p) for p in promos],
            attrition_outcome=AttritionOutcomeSchema.model_validate(outcome) if outcome else None
        )
