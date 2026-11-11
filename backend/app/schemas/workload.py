"""Schemas for Workload Snapshots."""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class WorkloadCreate(BaseModel):
    workload_id: Optional[str] = Field(None, example="WKL-EMP-000001-2026Q1")
    employee_id: str = Field(..., example="EMP-000001")
    period_quarter: str = Field(..., example="2026Q1")
    period_date: date = Field(..., example="2026-03-31")
    avg_weekly_hours: float = Field(..., ge=20.0, le=90.0, example=45.5)
    overtime_hours: float = Field(0.0, ge=0.0, le=50.0, example=5.5)
    consecutive_overtime_weeks: int = Field(0, ge=0, le=52, example=3)
    active_project_count: int = Field(..., ge=1, le=20, example=3)
    is_benign_surge: bool = Field(False, description="True if surge is acknowledged release cycle milestone")


class WorkloadResponse(BaseModel):
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
    created_at: datetime
