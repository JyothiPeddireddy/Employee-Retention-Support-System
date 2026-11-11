"""Authentication and User Lifecycle Service."""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.app_user import AppUser, UserRole
from backend.app.models.employee import Employee
from backend.app.core.security import verify_password, get_password_hash, revoke_token
from backend.app.schemas.auth import UserRegisterRequest, ChangePasswordRequest
from backend.app.services.audit_service import AuditService


class AuthService:
    @staticmethod
    def register_user(db: Session, req: UserRegisterRequest, performed_by: Optional[str] = None) -> AppUser:
        """Register a new user with bcrypt password and unique username/email."""
        existing_username = db.query(AppUser).filter(AppUser.username == req.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{req.username}' is already registered."
            )

        existing_email = db.query(AppUser).filter(AppUser.email == req.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{req.email}' is already registered."
            )

        if req.employee_id:
            emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
            if not emp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Linked employee '{req.employee_id}' does not exist."
                )

        count = db.query(AppUser).count() + 1
        user_id = f"USR-{count:06d}"

        role_str = req.role.value if isinstance(req.role, UserRole) else str(req.role)

        user = AppUser(
            user_id=user_id,
            username=req.username,
            email=req.email,
            hashed_password=get_password_hash(req.password),
            role=role_str,
            employee_id=req.employee_id,
            is_active=True
        )
        db.add(user)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="app_users",
            entity_id=user_id,
            action="INSERT",
            performed_by=performed_by or user_id,
            changes={"username": req.username, "role": role_str, "email": req.email}
        )

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[AppUser]:
        """Authenticate username/email and password."""
        user = db.query(AppUser).filter(
            (AppUser.username == username) | (AppUser.email == username)
        ).first()

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )
        return user

    @staticmethod
    def change_password(db: Session, user: AppUser, req: ChangePasswordRequest) -> None:
        """Verify current password and update with new bcrypt hash."""
        if not verify_password(req.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password."
            )

        user.hashed_password = get_password_hash(req.new_password)
        db.add(user)

        AuditService.log_action(
            db=db,
            entity_name="app_users",
            entity_id=user.user_id,
            action="UPDATE",
            performed_by=user.user_id,
            changes={"action": "PASSWORD_CHANGED"}
        )
        db.commit()

    @staticmethod
    def logout(token: str) -> None:
        """Revoke current access token."""
        revoke_token(token)
