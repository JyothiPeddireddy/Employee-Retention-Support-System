"""Schemas for System Administration, RBAC and Audit Trail."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from backend.app.models.app_user import UserRole


class UserAdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    employee_id: Optional[str] = None
    is_active: bool = True


class UserRoleUpdateRequest(BaseModel):
    role: UserRole = Field(..., description="Target role to assign")


class SystemStatsResponse(BaseModel):
    database_url_masked: str
    database_engine: str
    is_sqlite: bool
    table_counts: Dict[str, int]
    system_timestamp: datetime
    active_users: int


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    log_id: str
    entity_name: str
    entity_id: str
    action: str
    performed_by: str
    timestamp: datetime
    changes_json: Optional[str] = None
    ip_address: Optional[str] = None
