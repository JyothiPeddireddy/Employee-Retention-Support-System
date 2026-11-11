"""Authentication and User Lifecycle API Router."""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser
from backend.app.core.security import create_access_token
from backend.app.core.config import get_settings
from backend.app.core.dependencies import get_current_user, oauth2_scheme
from backend.app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, ChangePasswordRequest
)
from backend.app.schemas.common import APIResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])
settings = get_settings()


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user account."""
    user = AuthService.register_user(db=db, req=payload)
    return APIResponse(
        success=True,
        message=f"User '{user.username}' successfully registered.",
        data=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate with username/password and receive a signed JWT access token."""
    user = AuthService.authenticate(db=db, username=payload.username, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.user_id}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.access_token_expire_minutes,
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        employee_id=user.employee_id
    )


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 standard form endpoint for Swagger UI Authorization button."""
    user = AuthService.authenticate(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.user_id}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.access_token_expire_minutes,
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        employee_id=user.employee_id
    )


@router.get("/me", response_model=APIResponse[UserResponse])
def get_current_user_profile(
    current_user: AppUser = Depends(get_current_user)
):
    """Retrieve authenticated user's profile and active permissions."""
    return APIResponse(
        success=True,
        message="Current user profile retrieved.",
        data=UserResponse.model_validate(current_user)
    )


@router.post("/change-password", response_model=APIResponse[dict])
def change_password(
    payload: ChangePasswordRequest,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current authenticated user's password."""
    AuthService.change_password(db=db, user=current_user, req=payload)
    return APIResponse(
        success=True,
        message="Password updated successfully."
    )


@router.post("/logout", response_model=APIResponse[dict])
def logout(
    token: str = Depends(oauth2_scheme)
):
    """Invalidate current JWT access token."""
    AuthService.logout(token)
    return APIResponse(
        success=True,
        message="Token revoked. User logged out successfully."
    )
