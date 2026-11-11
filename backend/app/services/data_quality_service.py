"""Service for Data Quality Assurance, Schema Validation, and Ground Truth Anomaly Reconciliation."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.validation import ValidationRun, ValidationIssue, GroundTruthAnomaly
from backend.app.models.employee import Employee
from backend.app.models.engagement_survey import EngagementSurvey
from backend.app.models.workload_snapshot import WorkloadSnapshot
from backend.app.models.tenure_snapshot import TenureSnapshot
from backend.app.models.attrition_outcome import AttritionOutcome
from backend.app.schemas.data_quality import ValidationRunResponse, ValidationIssueResponse
from backend.app.services.audit_service import AuditService


class DataQualityService:
    @staticmethod
    def run_full_validation(
        db: Session,
        seed: int = 20261022,
        performed_by: str = "SYSTEM"
    ) -> ValidationRun:
        """Execute automated database integrity suite, detecting temporal leaks and neutrality violations."""
        run_count = db.query(ValidationRun).count() + 1
        run_id = f"VRUN-2026-{run_count:06d}"

        total_checks = 0
        passed_checks = 0
        failed_checks = 0

        val_run = ValidationRun(
            run_id=run_id,
            run_timestamp=datetime.utcnow(),
            dataset_version="v1.0-postgresql",
            seed_used=seed,
            total_checks=0,
            passed_checks=0,
            failed_checks=0,
            status="IN_PROGRESS"
        )
        db.add(val_run)
        db.flush()

        issue_counter = 1

        # Check 1: Temporal Integrity & Future Leakage Prevention
        total_checks += 1
        attrited_outcomes = db.query(AttritionOutcome).all()
        outcome_dates = {o.employee_id: o.attrition_date for o in attrited_outcomes if o.attrition_date}

        leak_found = False
        for emp_id, a_date in outcome_dates.items():
            # Check surveys with survey_date > a_date used for pre-outcome signals
            post_surveys = db.query(EngagementSurvey).filter(
                EngagementSurvey.employee_id == emp_id,
                EngagementSurvey.survey_date > a_date
            ).all()
            for ps in post_surveys:
                leak_found = True
                failed_checks += 1
                v_issue = ValidationIssue(
                    issue_id=f"VISS-2026-{issue_counter:06d}",
                    run_id=run_id,
                    table_name="engagement_surveys",
                    record_id=ps.survey_id,
                    issue_type="FUTURE_INFO_LEAK",
                    severity="CRITICAL",
                    description=f"Survey {ps.survey_id} dated {ps.survey_date} is recorded after employee attrition date {a_date}."
                )
                db.add(v_issue)
                issue_counter += 1

        if not leak_found:
            passed_checks += 1

        # Check 2: Pulse Survey Neutrality Check
        total_checks += 1
        non_neutral_surveys = db.query(EngagementSurvey).filter(
            EngagementSurvey.is_missing == True,
            EngagementSurvey.satisfaction_score.isnot(None)
        ).all()

        if non_neutral_surveys:
            failed_checks += 1
            for s in non_neutral_surveys:
                v_issue = ValidationIssue(
                    issue_id=f"VISS-2026-{issue_counter:06d}",
                    run_id=run_id,
                    table_name="engagement_surveys",
                    record_id=s.survey_id,
                    issue_type="MISSING_SURVEY_PUNITIVE",
                    severity="HIGH",
                    description=f"Survey {s.survey_id} marked as missing but contains punitive non-null scores."
                )
                db.add(v_issue)
                issue_counter += 1
        else:
            passed_checks += 1

        # Check 3: Foreign Key & Orphan Records
        total_checks += 1
        all_emp_ids = set(r[0] for r in db.query(Employee.employee_id).all())
        survey_emp_ids = set(r[0] for r in db.query(EngagementSurvey.employee_id).distinct().all())
        orphans = survey_emp_ids - all_emp_ids
        if orphans:
            failed_checks += 1
            for orphan_id in orphans:
                v_issue = ValidationIssue(
                    issue_id=f"VISS-2026-{issue_counter:06d}",
                    run_id=run_id,
                    table_name="engagement_surveys",
                    record_id=orphan_id,
                    issue_type="SCHEMA_ERROR",
                    severity="CRITICAL",
                    description=f"Survey references nonexistent employee_id '{orphan_id}'."
                )
                db.add(v_issue)
                issue_counter += 1
        else:
            passed_checks += 1

        # Check 4: Workload Overtime Non-negativity
        total_checks += 1
        invalid_hours = db.query(WorkloadSnapshot).filter(
            (WorkloadSnapshot.avg_weekly_hours < 0) | (WorkloadSnapshot.overtime_hours < 0)
        ).all()
        if invalid_hours:
            failed_checks += 1
            for inv in invalid_hours:
                v_issue = ValidationIssue(
                    issue_id=f"VISS-2026-{issue_counter:06d}",
                    run_id=run_id,
                    table_name="workload_snapshots",
                    record_id=inv.workload_id,
                    issue_type="SCHEMA_ERROR",
                    severity="HIGH",
                    description=f"Workload {inv.workload_id} has negative hours."
                )
                db.add(v_issue)
                issue_counter += 1
        else:
            passed_checks += 1

        val_run.total_checks = total_checks
        val_run.passed_checks = passed_checks
        val_run.failed_checks = failed_checks
        val_run.status = "PASSED" if failed_checks == 0 else "ANOMALIES_DETECTED"

        AuditService.log_action(
            db=db,
            entity_name="validation_runs",
            entity_id=run_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"status": val_run.status, "passed": passed_checks, "failed": failed_checks}
        )

        db.commit()
        db.refresh(val_run)
        return val_run

    @staticmethod
    def list_validation_runs(db: Session, limit: int = 20) -> List[ValidationRunResponse]:
        """List validation run summaries."""
        runs = db.query(ValidationRun).order_by(ValidationRun.run_timestamp.desc()).limit(limit).all()
        return [
            ValidationRunResponse(
                run_id=r.run_id,
                run_timestamp=r.run_timestamp,
                dataset_version=r.dataset_version,
                seed_used=r.seed_used,
                total_checks=r.total_checks,
                passed_checks=r.passed_checks,
                failed_checks=r.failed_checks,
                status=r.status,
                issues=[]
            )
            for r in runs
        ]

    @staticmethod
    def get_run_issues(db: Session, run_id: str) -> List[ValidationIssueResponse]:
        """Retrieve issues detected during a specific validation run."""
        issues = db.query(ValidationIssue).filter(ValidationIssue.run_id == run_id).all()
        return [
            ValidationIssueResponse(
                issue_id=i.issue_id,
                run_id=i.run_id,
                table_name=i.table_name,
                record_id=i.record_id,
                issue_type=i.issue_type,
                severity=i.severity,
                description=i.description,
                created_at=i.created_at
            )
            for i in issues
        ]
