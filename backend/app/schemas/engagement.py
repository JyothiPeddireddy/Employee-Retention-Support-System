"""Schemas for Engagement Surveys."""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SurveyCreate(BaseModel):
    survey_id: Optional[str] = Field(None, example="SURV-2026-000001")
    employee_id: str = Field(..., example="EMP-000001")
    survey_quarter: str = Field(..., example="2026Q1")
    survey_date: date = Field(..., example="2026-03-31")
    is_missing: bool = Field(False, description="Whether survey was skipped/missing")
    satisfaction_score: Optional[float] = Field(None, ge=1.0, le=5.0, example=4.2)
    work_life_balance_score: Optional[float] = Field(None, ge=1.0, le=5.0, example=3.8)
    career_growth_score: Optional[float] = Field(None, ge=1.0, le=5.0, example=4.0)
    manager_support_score: Optional[float] = Field(None, ge=1.0, le=5.0, example=4.5)

    @model_validator(mode="after")
    def validate_survey_neutrality(self):
        if self.is_missing:
            # Neutrality enforcement: if missing, scores must be None
            self.satisfaction_score = None
            self.work_life_balance_score = None
            self.career_growth_score = None
            self.manager_support_score = None
        else:
            if any(s is None for s in [self.satisfaction_score, self.work_life_balance_score, self.career_growth_score, self.manager_support_score]):
                raise ValueError("Active survey submissions must include all core sentiment dimensions.")
        return self


class SurveyUpdate(BaseModel):
    satisfaction_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    work_life_balance_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    career_growth_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    manager_support_score: Optional[float] = Field(None, ge=1.0, le=5.0)


class SurveyResponse(BaseModel):
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
    created_at: datetime
