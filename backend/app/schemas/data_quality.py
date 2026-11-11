"""Schemas for Data Quality and Validation Runs."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ValidationRunCreate(BaseModel):
    seed: Optional[int] = Field(20261022, description="Random seed used for reconciliation")
    scale: Optional[int] = Field(500, description="Cohort size to validate")


class ValidationIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    issue_id: str
    run_id: str
    table_name: str
    record_id: str
    issue_type: str
    severity: str
    description: str
    created_at: datetime


class ValidationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    run_id: str
    run_timestamp: datetime
    dataset_version: str
    seed_used: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    status: str
    issues: List[ValidationIssueResponse] = []
