"""System Administration, User Management & Audit Log API Router."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.session import get_db, engine
from backend.app.models.app_user import AppUser, UserRole
from backend.app.models.audit_log import AuditLog
from backend.app.models.employee import Employee
from backend.app.models.team import Team
from backend.app.models.role import Role
from backend.app.models.intervention import Intervention
from backend.app.core.dependencies import require_roles
from backend.app.core.config import get_settings
from backend.app.schemas.admin import (
    UserAdminCreate, UserRoleUpdateRequest, SystemStatsResponse, AuditLogResponse
)
from backend.app.schemas.auth import UserResponse
from backend.app.schemas.common import APIResponse
from backend.app.services.auth_service import AuthService
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["System Administration & RBAC"])
settings = get_settings()


@router.get("/users", response_model=APIResponse[List[UserResponse]])
def list_system_users(
    role: Optional[str] = Query(None, description="Filter by user role"),
    current_user: AppUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List all registered system users."""
    query = db.query(AppUser)
    if role:
        query = query.filter(AppUser.role == role)
    users = query.order_by(AppUser.created_at.desc()).all()
    return APIResponse(
        success=True,
        message=f"Retrieved {len(users)} users.",
        data=[UserResponse.model_validate(u) for u in users]
    )


@router.post("/users", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def admin_create_user(
    payload: UserAdminCreate,
    current_user: AppUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Admin-managed user creation with explicit role assignment."""
    from backend.app.schemas.auth import UserRegisterRequest
    reg_req = UserRegisterRequest(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        employee_id=payload.employee_id
    )
    user = AuthService.register_user(db=db, req=reg_req, performed_by=current_user.user_id)
    return APIResponse(
        success=True,
        message=f"User '{user.username}' created with role '{user.role}'.",
        data=UserResponse.model_validate(user)
    )


@router.put("/users/{user_id}/role", response_model=APIResponse[UserResponse])
def update_user_role(
    user_id: str,
    payload: UserRoleUpdateRequest,
    current_user: AppUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update role for a user account."""
    target_user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    old_role = target_user.role
    new_role = payload.role.value if isinstance(payload.role, UserRole) else str(payload.role)
    target_user.role = new_role

    AuditService.log_action(
        db=db,
        entity_name="app_users",
        entity_id=user_id,
        action="UPDATE",
        performed_by=current_user.user_id,
        changes={"field": "role", "from": old_role, "to": new_role}
    )

    db.commit()
    db.refresh(target_user)
    return APIResponse(
        success=True,
        message=f"Role for user '{user_id}' updated to '{new_role}'.",
        data=UserResponse.model_validate(target_user)
    )


@router.get("/system-stats", response_model=APIResponse[SystemStatsResponse])
def get_system_statistics(
    current_user: AppUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve operational database metrics and table counts."""
    # Mask database password
    masked_url = settings.database_url
    if "@" in masked_url and ":" in masked_url:
        prefix, rest = masked_url.split("://", 1)
        creds, host = rest.split("@", 1)
        user = creds.split(":")[0] if ":" in creds else creds
        masked_url = f"{prefix}://{user}:***@{host}"

    table_counts = {
        "employees": db.query(Employee).count(),
        "teams": db.query(Team).count(),
        "roles": db.query(Role).count(),
        "interventions": db.query(Intervention).count(),
        "app_users": db.query(AppUser).count(),
        "audit_logs": db.query(AuditLog).count()
    }

    active_users = db.query(AppUser).filter(AppUser.is_active == True).count()

    return APIResponse(
        success=True,
        message="System statistics retrieved.",
        data=SystemStatsResponse(
            database_url_masked=masked_url,
            database_engine=engine.name,
            is_sqlite=settings.is_sqlite,
            table_counts=table_counts,
            system_timestamp=datetime.utcnow(),
            active_users=active_users
        )
    )


@router.get("/audit-logs", response_model=APIResponse[List[AuditLogResponse]])
def get_audit_logs(
    entity_name: Optional[str] = Query(None, description="Filter by entity table (e.g. employees, interventions)"),
    action: Optional[str] = Query(None, description="Filter by action (INSERT, UPDATE, DELETE)"),
    performed_by: Optional[str] = Query(None, description="Filter by actor ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: AppUser = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve comprehensive audit logs for regulatory and compliance review."""
    query = db.query(AuditLog)
    if entity_name:
        query = query.filter(AuditLog.entity_name == entity_name)
    if action:
        query = query.filter(AuditLog.action == action)
    if performed_by:
        query = query.filter(AuditLog.performed_by == performed_by)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return APIResponse(
        success=True,
        message=f"Retrieved {len(logs)} audit log records.",
        data=[AuditLogResponse.model_validate(l) for l in logs]
    )
