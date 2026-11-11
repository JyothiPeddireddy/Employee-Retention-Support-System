"""Schemas for Team, Role, and Team Membership Management."""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    team_id: Optional[str] = Field(None, example="TEAM-010")
    name: str = Field(..., min_length=2, max_length=100, example="Platform Engineering")
    department: str = Field(..., min_length=2, max_length=100, example="Engineering")
    lead_employee_id: Optional[str] = Field(None, example="EMP-000001")


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    lead_employee_id: Optional[str] = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: str
    name: str
    department: str
    lead_employee_id: Optional[str] = None
    member_count: Optional[int] = 0
    created_at: datetime


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    employee_id: str
    full_name: str
    email: str
    role_title: str
    role_level: str
    status: str
    is_lead: bool = False


class TeamTransferRequest(BaseModel):
    employee_id: str = Field(..., example="EMP-000005")
    target_team_id: str = Field(..., example="TEAM-002")
    new_role_id: Optional[str] = Field(None, example="ROLE-IC3-SWE")
    effective_date: date = Field(..., example="2026-04-01")
    transfer_reason: Optional[str] = Field("Strategic internal mobility", example="Strategic internal mobility")
    reason: Optional[str] = None


class RoleCreate(BaseModel):
    role_id: Optional[str] = Field(None, example="ROLE-010")
    title: str = Field(..., min_length=2, max_length=100, example="Senior Systems Architect")
    department: str = Field(..., min_length=2, max_length=100, example="Engineering")
    level: str = Field(..., example="IC4")  # IC1..IC6, M1..M3
    band_id: str = Field(..., example="BAND-ENG-L4")


class RoleUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    band_id: Optional[str] = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: str
    title: str
    department: str
    level: str
    band_id: str
    created_at: datetime
