"""Schemas for Explainable Retention Support Assessments."""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.prioritization import FactorAttribution


class AssessmentGenerateRequest(BaseModel):
    cutoff_date: Optional[date] = Field(None, description="Observation cutoff date for strict pre-outcome data barrier")
    department: Optional[str] = Field(None, example="Engineering")
    min_tier: Optional[str] = Field(None, example="MEDIUM")


class SupportAssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    assessment_id: str
    analysis_id: str
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    role_title: Optional[str] = None
    composite_priority_score: float
    priority_tier: str  # HIGH, MEDIUM, LOW
    workload_strain_score: float
    career_stagnation_score: float
    engagement_trajectory_score: float
    data_completeness_percentage: float = 100.0
    factors: List[FactorAttribution] = []
    recommended_topics: List[str] = []
    created_at: datetime


class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    analysis_id: str
    execution_date: datetime
    rule_version: str
    cutoff_date: date
    cohort_size: int
    high_priority_count: int
    medium_priority_count: int
    status: str
