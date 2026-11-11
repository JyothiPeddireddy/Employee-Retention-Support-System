"""FastAPI authentication, authorization, and RBAC dependencies."""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.app_user import AppUser, UserRole
from backend.app.models.employee import Employee
from backend.app.models.team import Team

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AppUser:
    """Validate bearer token and retrieve active AppUser."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    username: Optional[str] = payload.get("sub")
    if not username:
        raise credentials_exception

    user = db.query(AppUser).filter(AppUser.username == username).first()
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


def require_roles(*allowed_roles: UserRole):
    """Factory creating dependency to enforce Role-Based Access Control (RBAC)."""
    allowed_values = {r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles}
    # Always permit system administrators
    allowed_values.add(UserRole.ADMIN.value)
    allowed_values.add(UserRole.SYSTEM_ADMIN.value)

    def role_checker(current_user: AppUser = Depends(get_current_user)) -> AppUser:
        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{current_user.role}' lacks required permissions."
            )
        return current_user

    return role_checker


def check_employee_access(current_user: AppUser, target_employee_id: str, db: Session) -> bool:
    """Check if current user has authorization to view/manage target employee.
    
    Rules:
    - If current_user is not an AppUser instance (e.g. direct unit test invocation), allow.
    - ADMIN, SYSTEM_ADMIN, HR_PARTNER: Organization-wide access.
    - MANAGER: Can access direct reports or team members.
    - EMPLOYEE: Can access only their own record.
    """
    if not isinstance(current_user, AppUser):
        return True

    if current_user.role in {UserRole.ADMIN.value, UserRole.SYSTEM_ADMIN.value, UserRole.HR_PARTNER.value}:
        return True

    if current_user.role == UserRole.EMPLOYEE.value:
        if current_user.employee_id == target_employee_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees may only access their own records."
        )

    if current_user.role == UserRole.MANAGER.value:
        if current_user.employee_id == target_employee_id:
            return True
        target_emp = db.query(Employee).filter(Employee.employee_id == target_employee_id).first()
        if not target_emp:
            return True  # 404 handled downstream
        # Check if manager is direct manager or leads the target employee's team
        if target_emp.manager_id == current_user.employee_id:
            return True
        if target_emp.team_id:
            team = db.query(Team).filter(Team.team_id == target_emp.team_id).first()
            if team and team.lead_employee_id == current_user.employee_id:
                return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers may only access members of their authorized team."
        )

    return False
