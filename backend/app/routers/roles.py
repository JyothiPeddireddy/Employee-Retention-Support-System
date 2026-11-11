"""Roles & Job Classification API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import get_current_user, require_roles
from backend.app.schemas.team_role import RoleCreate, RoleResponse
from backend.app.schemas.common import APIResponse
from backend.app.services.team_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles & Job Classifications"])


@router.post("", response_model=APIResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new job classification role."""
    role = RoleService.create_role(db=db, req=payload, performed_by=current_user.user_id)
    return APIResponse(
        success=True,
        message=f"Role '{role.title}' created successfully.",
        data=RoleResponse.model_validate(role)
    )


@router.get("", response_model=APIResponse[List[RoleResponse]])
def list_roles(
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List standard job classification roles."""
    roles = RoleService.list_roles(db=db, department=department)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(roles)} roles.",
        data=roles
    )
