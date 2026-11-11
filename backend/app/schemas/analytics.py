"""Schemas for Analytics and Reporting."""
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict


class DepartmentMetricSummary(BaseModel):
    department: str
    total_employees: int
    active_employees: int
    attrited_employees: int
    high_priority_signals: int
    medium_priority_signals: int
    avg_hours: float
    avg_engagement: Optional[float] = None
    interventions_conducted: int


class OverviewMetrics(BaseModel):
    total_headcount: int
    active_headcount: int
    attrited_headcount: int
    overall_attrition_rate: float
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    total_interventions: int
    interventions_completed: int
    data_integrity_score: float
    avg_weekly_workload: float
    avg_engagement_sentiment: Optional[float] = None


class TrendDataPoint(BaseModel):
    quarter: str
    avg_workload_hours: float
    overtime_rate_percentage: float
    avg_engagement_score: Optional[float] = None
    survey_response_rate: float
