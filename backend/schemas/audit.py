"""Schemas for Validation, Audit Reports, and Ground Truth Anomalies."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GroundTruthAnomalySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    anomaly_id: str
    record_id: str
    table_name: str
    issue_type: str
    description: str
    expected_validation_error: str
    created_at: datetime


class ValidationCheckResult(BaseModel):
    check_name: str
    passed: bool
    total_records_checked: int
    failed_count: int
    details: str
    anomaly_type_detected: Optional[str] = None


class ValidationReport(BaseModel):
    generated_at: str
    dataset_version: str
    seed_used: int
    total_checks: int
    passed_checks: int
    failed_checks: int
    integrity_status: str  # PASSED, ANOMALIES_DETECTED
    check_results: List[ValidationCheckResult]
    ground_truth_reconciliation: Dict[str, Any]


class MetricsOverview(BaseModel):
    total_employees: int
    active_employees: int
    attrited_employees: int
    total_snapshots: int
    total_surveys: int
    interventions_logged: int
    high_priority_retention_signals: int
    ground_truth_anomalies_count: int
    data_integrity_score: float
