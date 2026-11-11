"""Schemas for Employee and Longitudinal Snapshots."""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class TeamSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: str
    name: str
    department: str


class RoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: str
    title: str
    level: str
    band_id: str


class TenureSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    snapshot_id: str
    employee_id: str
    snapshot_quarter: str
    snapshot_date: date
    tenure_months: int
    role_id: str
    team_id: str
    months_in_current_role: int


class WorkloadSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    workload_id: str
    employee_id: str
    period_quarter: str
    period_date: date
    avg_weekly_hours: float
    overtime_hours: float
    consecutive_overtime_weeks: int
    active_project_count: int
    is_benign_surge: bool


class EngagementSurveySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    survey_id: str
    employee_id: str
    survey_quarter: str
    survey_date: date
    is_missing: bool
    satisfaction_score: Optional[float] = None
    work_life_balance_score: Optional[float] = None
    career_growth_score: Optional[float] = None
    manager_support_score: Optional[float] = None
    composite_engagement: Optional[float] = None


class PromotionHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    promotion_id: str
    employee_id: str
    effective_date: date
    from_role_id: str
    to_role_id: str
    from_salary: float
    to_salary: float
    movement_type: str


class AttritionOutcomeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    outcome_id: str
    employee_id: str
    attrition_date: Optional[date] = None
    voluntary: bool
    primary_reason: Optional[str] = None
    horizon_period: str


class EmployeeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    employee_id: str
    full_name: str
    email: str
    team_name: str
    department: str
    role_title: str
    role_level: str
    hire_date: date
    current_salary: float
    status: str


class EmployeeDetail(EmployeeListItem):
    manager_id: Optional[str] = None
    tenure_months: int
    months_in_role: int


class EmployeeTimeline(BaseModel):
    employee: EmployeeListItem
    tenure_history: List[TenureSnapshotSchema]
    workload_history: List[WorkloadSnapshotSchema]
    survey_history: List[EngagementSurveySchema]
    promotions: List[PromotionHistorySchema]
    attrition_outcome: Optional[AttritionOutcomeSchema] = None
