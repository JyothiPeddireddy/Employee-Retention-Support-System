"""Schemas for Supportive Retention Interventions (Human-in-the-Loop)."""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class InterventionCreate(BaseModel):
    employee_id: str = Field(..., example="EMP-000001")
    conducted_by_id: str = Field(..., example="EMP-000002")
    intervention_date: date
    intervention_type: str = Field(
        ...,
        description="Type of supportive check-in",
        example="1_ON_1_CAREER_CHECKIN"  # WORKLOAD_REBALANCING, COMP_REVIEW, MENTORSHIP_ALIGNMENT
    )
    discussion_summary: str = Field(..., min_length=10)
    agreed_actions: Optional[str] = None
    follow_up_date: Optional[date] = None
    status: str = "SCHEDULED"


class InterventionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    intervention_id: str
    employee_id: str
    employee_name: Optional[str] = None
    conducted_by_id: str
    conducted_by_name: Optional[str] = None
    intervention_date: date
    intervention_type: str
    discussion_summary: str
    agreed_actions: Optional[str] = None
    follow_up_date: Optional[date] = None
    status: str
    simulated_outcome: Optional[str] = None
    created_at: datetime
