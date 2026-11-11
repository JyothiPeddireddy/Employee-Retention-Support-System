"""Authentication and user management schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from backend.app.models.app_user import UserRole


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="jdoe")
    email: EmailStr = Field(..., example="jdoe@example.com")
    password: str = Field(..., min_length=8, description="Password at least 8 characters", example="SecurePass123!")
    role: UserRole = Field(default=UserRole.EMPLOYEE, example=UserRole.EMPLOYEE)
    employee_id: Optional[str] = Field(None, example="EMP-000001")


class UserLoginRequest(BaseModel):
    username: str = Field(..., example="jdoe")
    password: str = Field(..., example="SecurePass123!")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
    username: str
    role: str
    employee_id: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    username: str
    email: str
    role: str
    employee_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, description="New password at least 8 characters")
