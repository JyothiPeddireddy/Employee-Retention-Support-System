"""Global in-memory & persistent data coordinator.
Ensures data consistency between SQLAlchemy models, file exports, and rule engines.
"""
import os
import json
from datetime import datetime, date
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from backend.core.config import get_settings
from backend.database import SessionLocal, init_db, engine
from backend.models import (
    Team, CompensationBand, Role, Employee, TenureSnapshot,
    WorkloadSnapshot, EngagementSurvey, PromotionHistory,
    AttritionOutcome, Intervention, GroundTruthAnomaly
)
from backend.services.generator import SyntheticDataGenerator
from backend.services.validator import DataValidator
from backend.services.rules import PrioritizationRulesEngine

settings = get_settings()


class DataStoreCoordinator:
    """Manages synthetic data lifecycle, database persistence, and service engines."""

    def __init__(self):
        self.raw_data: Dict[str, List[Dict[str, Any]]] = {}
        self.validator: DataValidator = None
        self.rules_engine: PrioritizationRulesEngine = None
        self.last_validation_report = None
        self.seed = settings.generator_seed

    def initialize(self, scale: int = 500, force_regenerate: bool = False):
        """Initialize database and seed baseline synthetic data if empty."""
        init_db()

        # Check if DB has employees
        db = SessionLocal()
        try:
            emp_count = db.query(Employee).count()
            if emp_count == 0 or force_regenerate:
                print(f"[DataStore] Generating synthetic workforce data (scale={scale}, seed={self.seed})...")
                gen = SyntheticDataGenerator(seed=self.seed, scale=scale)
                gen.generate_all()
                gen.export_to_files("data")
                self.persist_to_db(gen, db)
            else:
                print(f"[DataStore] Loading {emp_count} employees from database...")

            self.load_from_db(db)
        finally:
            db.close()

        # Initialize engines
        self.validator = DataValidator(self.raw_data)
        self.rules_engine = PrioritizationRulesEngine(self.raw_data)
        self.last_validation_report = self.validator.run_all_validations(seed=self.seed)

    def persist_to_db(self, gen: SyntheticDataGenerator, db: Session):
        """Wipe and bulk insert generated records into database with high performance."""
        # Clean existing
        db.query(GroundTruthAnomaly).delete()
        db.query(Intervention).delete()
        db.query(AttritionOutcome).delete()
        db.query(PromotionHistory).delete()
        db.query(EngagementSurvey).delete()
        db.query(WorkloadSnapshot).delete()
        db.query(TenureSnapshot).delete()
        db.query(Employee).delete()
        db.query(Role).delete()
        db.query(CompensationBand).delete()
        db.query(Team).delete()
        db.commit()

        # High-performance bulk inserts
        if gen.teams:
            team_rows = [
                {
                    "team_id": t["team_id"],
                    "name": t["name"],
                    "department": t["department"],
                    "created_at": datetime(2023, 1, 1, 0, 0, 0)
                }
                for t in gen.teams
            ]
            db.bulk_insert_mappings(Team, team_rows)

        if gen.bands:
            db.bulk_insert_mappings(CompensationBand, gen.bands)

        if gen.roles:
            db.bulk_insert_mappings(Role, gen.roles)

        if gen.employees:
            emp_rows = [
                {
                    "employee_id": e["employee_id"],
                    "full_name": e["full_name"],
                    "email": e["email"],
                    "team_id": e["team_id"],
                    "role_id": e["role_id"],
                    "manager_id": e.get("manager_id"),
                    "hire_date": e["hire_date"] if isinstance(e["hire_date"], date) else date.fromisoformat(str(e["hire_date"])),
                    "current_salary": e["current_salary"],
                    "status": e["status"],
                    "created_at": datetime(2024, 1, 1, 0, 0, 0)
                }
                for e in gen.employees
            ]
            db.bulk_insert_mappings(Employee, emp_rows)
        db.commit()

        if gen.tenure_snapshots:
            snap_rows = [
                {
                    "snapshot_id": s["snapshot_id"],
                    "employee_id": s["employee_id"],
                    "snapshot_quarter": s["snapshot_quarter"],
                    "snapshot_date": s["snapshot_date"] if isinstance(s["snapshot_date"], date) else date.fromisoformat(str(s["snapshot_date"])),
                    "tenure_months": s["tenure_months"],
                    "role_id": s["role_id"],
                    "team_id": s["team_id"],
                    "months_in_current_role": s["months_in_current_role"]
                }
                for s in gen.tenure_snapshots
            ]
            db.bulk_insert_mappings(TenureSnapshot, snap_rows)

        if gen.workload_snapshots:
            work_rows = [
                {
                    "workload_id": w["workload_id"],
                    "employee_id": w["employee_id"],
                    "period_quarter": w["period_quarter"],
                    "period_date": w["period_date"] if isinstance(w["period_date"], date) else date.fromisoformat(str(w["period_date"])),
                    "avg_weekly_hours": w["avg_weekly_hours"],
                    "overtime_hours": w["overtime_hours"],
                    "consecutive_overtime_weeks": w["consecutive_overtime_weeks"],
                    "active_project_count": w["active_project_count"],
                    "is_benign_surge": w["is_benign_surge"]
                }
                for w in gen.workload_snapshots
            ]
            db.bulk_insert_mappings(WorkloadSnapshot, work_rows)

        if gen.engagement_surveys:
            surv_rows = [
                {
                    "survey_id": s["survey_id"],
                    "employee_id": s["employee_id"],
                    "survey_quarter": s["survey_quarter"],
                    "survey_date": s["survey_date"] if isinstance(s["survey_date"], date) else date.fromisoformat(str(s["survey_date"])),
                    "is_missing": s["is_missing"],
                    "satisfaction_score": s["satisfaction_score"],
                    "work_life_balance_score": s.get("work_life_balance_score"),
                    "career_growth_score": s.get("career_growth_score"),
                    "manager_support_score": s.get("manager_support_score"),
                    "composite_engagement": s["composite_engagement"]
                }
                for s in gen.engagement_surveys
            ]
            db.bulk_insert_mappings(EngagementSurvey, surv_rows)

        if gen.promotion_histories:
            promo_rows = [
                {
                    "promotion_id": p["promotion_id"],
                    "employee_id": p["employee_id"],
                    "effective_date": p["effective_date"] if isinstance(p["effective_date"], date) else date.fromisoformat(str(p["effective_date"])),
                    "from_role_id": p["from_role_id"],
                    "to_role_id": p["to_role_id"],
                    "from_salary": p["from_salary"],
                    "to_salary": p["to_salary"],
                    "movement_type": p["movement_type"]
                }
                for p in gen.promotion_histories
            ]
            db.bulk_insert_mappings(PromotionHistory, promo_rows)

        if gen.attrition_outcomes:
            out_rows = [
                {
                    "outcome_id": a["outcome_id"],
                    "employee_id": a["employee_id"],
                    "attrition_date": (a["attrition_date"] if isinstance(a["attrition_date"], date) else date.fromisoformat(str(a["attrition_date"]))) if a.get("attrition_date") else None,
                    "voluntary": a["voluntary"],
                    "primary_reason": a.get("primary_reason"),
                    "horizon_period": a["horizon_period"]
                }
                for a in gen.attrition_outcomes
            ]
            db.bulk_insert_mappings(AttritionOutcome, out_rows)

        if gen.interventions:
            int_rows = [
                {
                    "intervention_id": i["intervention_id"],
                    "employee_id": i["employee_id"],
                    "conducted_by_id": i["conducted_by_id"],
                    "intervention_date": i["intervention_date"] if isinstance(i["intervention_date"], date) else date.fromisoformat(str(i["intervention_date"])),
                    "intervention_type": i["intervention_type"],
                    "discussion_summary": i["discussion_summary"],
                    "agreed_actions": i.get("agreed_actions"),
                    "follow_up_date": (i["follow_up_date"] if isinstance(i["follow_up_date"], date) else date.fromisoformat(str(i["follow_up_date"]))) if i.get("follow_up_date") else None,
                    "status": i.get("status", "SCHEDULED"),
                    "simulated_outcome": i.get("simulated_outcome"),
                    "created_at": datetime.utcnow()
                }
                for i in gen.interventions
            ]
            db.bulk_insert_mappings(Intervention, int_rows)

        if gen.ground_truth_anomalies:
            gt_rows = [
                {
                    "anomaly_id": g["anomaly_id"],
                    "record_id": g["record_id"],
                    "table_name": g["table_name"],
                    "issue_type": g["issue_type"],
                    "description": g["description"],
                    "expected_validation_error": g["expected_validation_error"],
                    "created_at": datetime.utcnow()
                }
                for g in gen.ground_truth_anomalies
            ]
            db.bulk_insert_mappings(GroundTruthAnomaly, gt_rows)

        db.commit()
        print(f"[DataStore] Successfully persisted synthetic data to database in milliseconds.")

    def load_from_db(self, db: Session):
        """Read all rows from database into internal dictionary cache for high-speed queries."""
        self.raw_data = {
            "teams": [
                {"team_id": t.team_id, "name": t.name, "department": t.department}
                for t in db.query(Team).all()
            ],
            "compensation_bands": [
                {
                    "band_id": b.band_id, "name": b.name,
                    "min_salary": b.min_salary, "mid_salary": b.mid_salary, "max_salary": b.max_salary
                }
                for b in db.query(CompensationBand).all()
            ],
            "roles": [
                {"role_id": r.role_id, "title": r.title, "level": r.level, "band_id": r.band_id}
                for r in db.query(Role).all()
            ],
            "employees": [
                {
                    "employee_id": e.employee_id, "full_name": e.full_name, "email": e.email,
                    "team_id": e.team_id, "role_id": e.role_id, "manager_id": e.manager_id,
                    "hire_date": str(e.hire_date), "current_salary": e.current_salary, "status": e.status
                }
                for e in db.query(Employee).all()
            ],
            "tenure_snapshots": [
                {
                    "snapshot_id": s.snapshot_id, "employee_id": s.employee_id,
                    "snapshot_quarter": s.snapshot_quarter, "snapshot_date": str(s.snapshot_date),
                    "tenure_months": s.tenure_months, "role_id": s.role_id, "team_id": s.team_id,
                    "months_in_current_role": s.months_in_current_role
                }
                for s in db.query(TenureSnapshot).all()
            ],
            "workload_snapshots": [
                {
                    "workload_id": w.workload_id, "employee_id": w.employee_id,
                    "period_quarter": w.period_quarter, "period_date": str(w.period_date),
                    "avg_weekly_hours": w.avg_weekly_hours, "overtime_hours": w.overtime_hours,
                    "consecutive_overtime_weeks": w.consecutive_overtime_weeks,
                    "active_project_count": w.active_project_count,
                    "is_benign_surge": w.is_benign_surge
                }
                for w in db.query(WorkloadSnapshot).all()
            ],
            "engagement_surveys": [
                {
                    "survey_id": s.survey_id, "employee_id": s.employee_id,
                    "survey_quarter": s.survey_quarter, "survey_date": str(s.survey_date),
                    "is_missing": s.is_missing, "satisfaction_score": s.satisfaction_score,
                    "composite_engagement": s.composite_engagement
                }
                for s in db.query(EngagementSurvey).all()
            ],
            "promotion_histories": [
                {
                    "promotion_id": p.promotion_id, "employee_id": p.employee_id,
                    "effective_date": str(p.effective_date), "from_role_id": p.from_role_id,
                    "to_role_id": p.to_role_id, "from_salary": p.from_salary, "to_salary": p.to_salary,
                    "movement_type": p.movement_type
                }
                for p in db.query(PromotionHistory).all()
            ],
            "attrition_outcomes": [
                {
                    "outcome_id": a.outcome_id, "employee_id": a.employee_id,
                    "attrition_date": str(a.attrition_date) if a.attrition_date else None,
                    "voluntary": a.voluntary, "primary_reason": a.primary_reason,
                    "horizon_period": a.horizon_period
                }
                for a in db.query(AttritionOutcome).all()
            ],
            "interventions": [
                {
                    "intervention_id": i.intervention_id, "employee_id": i.employee_id,
                    "conducted_by_id": i.conducted_by_id, "intervention_date": str(i.intervention_date),
                    "intervention_type": i.intervention_type, "discussion_summary": i.discussion_summary,
                    "agreed_actions": i.agreed_actions, "follow_up_date": str(i.follow_up_date) if i.follow_up_date else None,
                    "status": i.status, "simulated_outcome": i.simulated_outcome
                }
                for i in db.query(Intervention).all()
            ],
            "ground_truth_anomalies": [
                {
                    "anomaly_id": g.anomaly_id, "record_id": g.record_id, "table_name": g.table_name,
                    "issue_type": g.issue_type, "description": g.description,
                    "expected_validation_error": g.expected_validation_error
                }
                for g in db.query(GroundTruthAnomaly).all()
            ]
        }


# Singleton instance
store_coordinator = DataStoreCoordinator()
