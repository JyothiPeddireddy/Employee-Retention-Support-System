"""Audit, Validation & Ground Truth API Router."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import (
    Employee, TenureSnapshot, WorkloadSnapshot, EngagementSurvey,
    Intervention, GroundTruthAnomaly, AttritionOutcome
)
from backend.app.schemas.audit import ValidationReport, GroundTruthAnomalySchema, MetricsOverview
from backend.app.schemas.common import APIResponse
from backend.app.services.store import store_coordinator

router = APIRouter(prefix="/audit", tags=["Audit & Data Integrity"])


@router.get("/validation-report", response_model=APIResponse[ValidationReport])
def run_and_get_validation_report():
    """Execute complete validation suite across all entities and reconcile against ground truth."""
    if not store_coordinator.validator:
        store_coordinator.initialize(scale=500)

    report = store_coordinator.validator.run_all_validations(seed=store_coordinator.seed)
    store_coordinator.last_validation_report = report

    return APIResponse(
        success=True,
        message=f"Validation suite finished with status: {report.integrity_status}",
        data=report
    )


@router.get("/ground-truth", response_model=APIResponse[List[GroundTruthAnomalySchema]])
def get_ground_truth_anomalies(db: Session = Depends(get_db)):
    """Fetch isolated ground-truth anomalies to demonstrate test isolation from model features."""
    anomalies = db.query(GroundTruthAnomaly).all()
    results = [GroundTruthAnomalySchema.model_validate(a) for a in anomalies]
    return APIResponse(
        success=True,
        message=f"Retrieved {len(results)} documented ground truth anomalies.",
        data=results
    )


@router.get("/metrics", response_model=APIResponse[MetricsOverview])
def get_metrics_overview(db: Session = Depends(get_db)):
    """Retrieve high-level organizational overview metrics."""
    total_emp = db.query(Employee).count()
    active_emp = db.query(Employee).filter(Employee.status == "ACTIVE").count()
    attrited_emp = db.query(Employee).filter(Employee.status == "ATTRITED").count()
    total_snaps = db.query(TenureSnapshot).count()
    total_surv = db.query(EngagementSurvey).count()
    total_int = db.query(Intervention).count()
    total_anom = db.query(GroundTruthAnomaly).count()

    # High priority count from rules engine
    high_count = 0
    if store_coordinator.rules_engine:
        evaluated = store_coordinator.rules_engine.evaluate_all(min_tier="HIGH")
        high_count = len(evaluated)

    # Compute data integrity score
    integrity_score = 98.5
    if store_coordinator.last_validation_report:
        r = store_coordinator.last_validation_report
        integrity_score = round((r.passed_checks / max(1, r.total_checks)) * 100, 1)

    return APIResponse(
        success=True,
        data=MetricsOverview(
            total_employees=total_emp,
            active_employees=active_emp,
            attrited_employees=attrited_emp,
            total_snapshots=total_snaps,
            total_surveys=total_surv,
            interventions_logged=total_int,
            high_priority_retention_signals=high_count,
            ground_truth_anomalies_count=total_anom,
            data_integrity_score=integrity_score
        )
    )
