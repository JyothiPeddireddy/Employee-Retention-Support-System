"""Schemas for Supportive Retention Interventions (Human-in-the-Loop)."""
from typing import Optional, List
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


class InterventionUpdate(BaseModel):
    discussion_summary: Optional[str] = Field(None, min_length=10)
    agreed_actions: Optional[str] = None
    follow_up_date: Optional[date] = None
    status: Optional[str] = None
    simulated_outcome: Optional[str] = None


class InterventionStatusUpdate(BaseModel):
    status: str = Field(..., example="COMPLETED")  # SCHEDULED, COMPLETED, CANCELLED
    notes: Optional[str] = Field(None, example="Check-in successfully completed.")


class InterventionOutcomeUpdate(BaseModel):
    simulated_outcome: str = Field(..., example="RETENTION_REINFORCED")  # RETENTION_REINFORCED, STILL_AT_RISK
    notes: Optional[str] = Field(None, example="Employee agreed to updated project timeline.")


class InterventionEventCreate(BaseModel):
    event_type: str = Field(..., example="NOTES_UPDATED")  # CREATED, NOTES_UPDATED, ACTION_COMPLETED, FOLLOW_UP_SCHEDULED, CANCELLED
    actor_id: str = Field(..., example="EMP-000002")
    notes: Optional[str] = Field(None, example="Added follow-up action plan.")


class InterventionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_id: str
    intervention_id: str
    event_type: str
    event_timestamp: datetime
    actor_id: str
    actor_name: Optional[str] = None
    notes: Optional[str] = None


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


class InterventionDetailResponse(InterventionResponse):
    events: List[InterventionEventResponse] = []
