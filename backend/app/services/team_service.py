"""Service for Team, Role, and Historical Team Membership Management."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.team import Team
from backend.app.models.role import Role
from backend.app.models.employee import Employee
from backend.app.models.team_membership import TeamMembershipHistory
from backend.app.schemas.team_role import (
    TeamCreate, TeamUpdate, TeamResponse, TeamMemberResponse, TeamTransferRequest,
    RoleCreate, RoleUpdate, RoleResponse
)
from backend.app.services.audit_service import AuditService


class TeamService:
    @staticmethod
    def create_team(db: Session, req: TeamCreate, performed_by: str) -> Team:
        """Create new organizational team."""
        team_id = req.team_id
        if not team_id:
            count = db.query(Team).count() + 1
            team_id = f"TEAM-{count:03d}"

        if db.query(Team).filter(Team.team_id == team_id).first():
            raise HTTPException(status_code=400, detail=f"Team ID '{team_id}' already exists.")

        if req.lead_employee_id:
            lead = db.query(Employee).filter(Employee.employee_id == req.lead_employee_id).first()
            if not lead:
                raise HTTPException(status_code=400, detail=f"Lead employee '{req.lead_employee_id}' not found.")

        team = Team(
            team_id=team_id,
            name=req.name,
            department=req.department,
            lead_employee_id=req.lead_employee_id
        )
        db.add(team)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="teams",
            entity_id=team_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"name": req.name, "department": req.department}
        )

        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def list_teams(db: Session, department: Optional[str] = None) -> List[TeamResponse]:
        """List all teams with member count."""
        query = db.query(Team)
        if department:
            query = query.filter(Team.department.ilike(f"%{department}%"))

        teams = query.all()
        results = []
        for t in teams:
            member_count = db.query(Employee).filter(Employee.team_id == t.team_id).count()
            results.append(TeamResponse(
                team_id=t.team_id,
                name=t.name,
                department=t.department,
                lead_employee_id=t.lead_employee_id,
                member_count=member_count,
                created_at=t.created_at
            ))
        return results

    @staticmethod
    def get_team_members(db: Session, team_id: str) -> List[TeamMemberResponse]:
        """List current members belonging to a team."""
        team = db.query(Team).filter(Team.team_id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")

        members = db.query(Employee).filter(Employee.team_id == team_id).all()
        results = []
        for m in members:
            results.append(TeamMemberResponse(
                employee_id=m.employee_id,
                full_name=m.full_name,
                email=m.email,
                role_title=m.role.title if m.role else "N/A",
                role_level=m.role.level if m.role else "N/A",
                status=m.status,
                is_lead=(m.employee_id == team.lead_employee_id)
            ))
        return results

    @staticmethod
    def transfer_employee_team(
        db: Session,
        req: TeamTransferRequest,
        performed_by: str
    ) -> TeamMembershipHistory:
        """Transfer employee to another team preserving historical membership timeline."""
        emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{req.employee_id}' not found.")

        target_team = db.query(Team).filter(Team.team_id == req.target_team_id).first()
        if not target_team:
            raise HTTPException(status_code=404, detail=f"Target team '{req.target_team_id}' not found.")

        old_team_id = emp.team_id

        # Close current membership history record
        current_membership = db.query(TeamMembershipHistory).filter(
            TeamMembershipHistory.employee_id == req.employee_id,
            TeamMembershipHistory.is_current == True
        ).first()

        if current_membership:
            current_membership.is_current = False
            current_membership.effective_end_date = req.effective_date
            db.add(current_membership)

        # Create new membership history record
        mem_count = db.query(TeamMembershipHistory).filter(
            TeamMembershipHistory.employee_id == req.employee_id
        ).count() + 1
        new_membership_id = f"MEM-{req.employee_id}-{mem_count:03d}"

        new_membership = TeamMembershipHistory(
            membership_id=new_membership_id,
            employee_id=req.employee_id,
            team_id=req.target_team_id,
            role_id=emp.current_role_id,
            effective_start_date=req.effective_date,
            effective_end_date=None,
            is_current=True,
            transfer_reason=req.transfer_reason or "INTERNAL_TRANSFER"
        )
        db.add(new_membership)

        # Update current employee team
        emp.current_team_id = req.target_team_id
        db.add(emp)

        AuditService.log_action(
            db=db,
            entity_name="team_memberships",
            entity_id=new_membership_id,
            action="UPDATE",
            performed_by=performed_by,
            changes={
                "employee_id": req.employee_id,
                "from_team": old_team_id,
                "to_team": req.target_team_id,
                "effective_date": str(req.effective_date)
            }
        )

        db.commit()
        db.refresh(new_membership)
        return new_membership


class RoleService:
    @staticmethod
    def create_role(db: Session, req: RoleCreate, performed_by: str) -> Role:
        """Create new standard job role."""
        role_id = req.role_id
        if not role_id:
            count = db.query(Role).count() + 1
            role_id = f"ROLE-{count:03d}"

        if db.query(Role).filter(Role.role_id == role_id).first():
            raise HTTPException(status_code=400, detail=f"Role ID '{role_id}' already exists.")

        role = Role(
            role_id=role_id,
            title=req.title,
            department=req.department,
            level=req.level,
            band_id=req.band_id
        )
        db.add(role)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="roles",
            entity_id=role_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"title": req.title, "level": req.level, "band_id": req.band_id}
        )

        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def list_roles(db: Session, department: Optional[str] = None) -> List[RoleResponse]:
        """List standard company roles."""
        query = db.query(Role)
        if department:
            query = query.filter(Role.department.ilike(f"%{department}%"))
        roles = query.all()
        return [
            RoleResponse(
                role_id=r.role_id,
                title=r.title,
                department=r.department,
                level=r.level,
                band_id=r.band_id,
                created_at=r.created_at
            )
            for r in roles
        ]
