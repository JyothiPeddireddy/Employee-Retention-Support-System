"""Teams & Effective-Dated Membership API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import get_current_user, require_roles
from backend.app.schemas.team_role import (
    TeamCreate, TeamUpdate, TeamResponse, TeamMemberResponse, TeamTransferRequest
)
from backend.app.schemas.common import APIResponse
from backend.app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams & Organizational Structure"])


@router.post("", response_model=APIResponse[TeamResponse], status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new team within the organization."""
    team = TeamService.create_team(db=db, req=payload, performed_by=current_user.user_id)
    return APIResponse(
        success=True,
        message=f"Team '{team.name}' created successfully.",
        data=TeamResponse(
            team_id=team.team_id,
            name=team.name,
            department=team.department,
            lead_employee_id=getattr(team, "lead_employee_id", None),
            member_count=0,
            created_at=team.created_at
        )
    )


@router.put("/{team_id}", response_model=APIResponse[TeamResponse])
def update_team(
    team_id: str,
    payload: TeamUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update existing team details."""
    team = TeamService.update_team(db=db, team_id=team_id, req=payload, performed_by=current_user.user_id)
    member_count = db.query(Employee).filter(Employee.current_team_id == team_id).count()
    return APIResponse(
        success=True,
        message=f"Team '{team.name}' updated successfully.",
        data=TeamResponse(
            team_id=team.team_id,
            name=team.name,
            department=team.department,
            lead_employee_id=getattr(team, "lead_employee_id", None),
            member_count=member_count,
            created_at=team.created_at
        )
    )


@router.get("", response_model=APIResponse[List[TeamResponse]])
def list_teams(
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List organizational teams."""
    teams = TeamService.list_teams(db=db, department=department)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(teams)} teams.",
        data=teams
    )


@router.get("/{team_id}/members", response_model=APIResponse[List[TeamMemberResponse]])
def get_team_members(
    team_id: str,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List members belonging to a team."""
    members = TeamService.get_team_members(db=db, team_id=team_id)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(members)} team members.",
        data=members
    )


@router.post("/{team_id}/transfer", response_model=APIResponse[dict])
def transfer_employee(
    team_id: str,
    payload: TeamTransferRequest,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN, UserRole.MANAGER)),
    db: Session = Depends(get_db)
):
    """Transfer an employee to a new team preserving historical membership timeline."""
    payload.target_team_id = team_id
    membership = TeamService.transfer_employee_team(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Employee '{payload.employee_id}' successfully transferred to team '{team_id}'.",
        data={
            "membership_id": membership.membership_id,
            "employee_id": membership.employee_id,
            "team_id": membership.team_id,
            "effective_start_date": str(membership.effective_start_date)
        }
    )
