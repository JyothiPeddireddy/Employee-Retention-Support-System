"""Schemas for Explainable Retention Prioritization & Signals."""
from typing import List, Optional
from pydantic import BaseModel


class FactorAttribution(BaseModel):
    category: str              # WORKLOAD, CAREER_GROWTH, ENGAGEMENT, COMPENSATION
    signal_name: str           # e.g., "Sustained Overtime Surge"
    raw_value: str             # e.g., "52 hrs/wk (6 consec weeks)"
    impact_level: str          # HIGH, MEDIUM, LOW
    supportive_guidance: str   # e.g., "Discuss project bandwidth and possible sprint offloading"


class PrioritizedEmployee(BaseModel):
    employee_id: str
    full_name: str
    email: str
    team_name: str
    department: str
    role_title: str
    role_level: str
    tenure_months: int
    months_in_role: int
    composite_priority_score: float  # 0 to 100
    priority_tier: str               # HIGH, MEDIUM, LOW
    factors: List[FactorAttribution]
    recommended_topics: List[str]
    has_active_intervention: bool = False
    last_intervention_date: Optional[str] = None


class PrioritizationSummary(BaseModel):
    total_evaluated: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    interventions_logged: int
    top_driver: str
