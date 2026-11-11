"""Service for Explainable Retention Support Assessments and Analysis Runs."""
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.analysis import AnalysisRun, SupportAssessment
from backend.app.models.employee import Employee
from backend.app.models.team import Team
from backend.app.models.role import Role
from backend.app.models.compensation_band import CompensationBand
from backend.app.models.tenure_snapshot import TenureSnapshot
from backend.app.models.workload_snapshot import WorkloadSnapshot
from backend.app.models.engagement_survey import EngagementSurvey
from backend.app.models.intervention import Intervention
from backend.app.schemas.assessment import (
    AssessmentGenerateRequest, SupportAssessmentDetailResponse, AnalysisRunResponse
)
from backend.app.schemas.prioritization import FactorAttribution
from backend.app.services.audit_service import AuditService


class AssessmentService:
    @staticmethod
    def generate_assessments(
        db: Session,
        req: AssessmentGenerateRequest,
        performed_by: str
    ) -> AnalysisRun:
        """Run explainable, supportive retention evaluation using database records strictly up to cutoff date."""
        cutoff_date = req.cutoff_date or date.today()

        # Fetch active employees
        emp_query = db.query(Employee).filter(Employee.status == "ACTIVE")
        if req.department:
            emp_query = emp_query.join(Employee.team).filter(Team.department.ilike(f"%{req.department}%"))

        employees = emp_query.all()
        cohort_size = len(employees)

        # Unique run ID
        run_count = db.query(AnalysisRun).count() + 1
        analysis_id = f"ARUN-2026-{run_count:06d}"

        analysis_run = AnalysisRun(
            analysis_id=analysis_id,
            execution_date=datetime.utcnow(),
            rule_version="v1.0-explainable",
            cutoff_date=cutoff_date,
            cohort_size=cohort_size,
            high_priority_count=0,
            medium_priority_count=0,
            status="IN_PROGRESS"
        )
        db.add(analysis_run)
        db.flush()

        high_count = 0
        med_count = 0
        asmt_counter = 1

        for emp in employees:
            assessment = AssessmentService._evaluate_single_employee(
                db=db,
                emp=emp,
                cutoff_date=cutoff_date,
                analysis_id=analysis_id,
                asmt_index=asmt_counter
            )
            asmt_counter += 1

            if assessment.priority_tier == "HIGH":
                high_count += 1
            elif assessment.priority_tier == "MEDIUM":
                med_count += 1

            if req.min_tier:
                tier_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
                if tier_order.get(assessment.priority_tier, 0) < tier_order.get(req.min_tier, 0):
                    continue

            db.add(assessment)

        analysis_run.high_priority_count = high_count
        analysis_run.medium_priority_count = med_count
        analysis_run.status = "COMPLETED"

        AuditService.log_action(
            db=db,
            entity_name="analysis_runs",
            entity_id=analysis_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"cohort_size": cohort_size, "high": high_count, "medium": med_count}
        )

        db.commit()
        db.refresh(analysis_run)
        return analysis_run

    @staticmethod
    def _evaluate_single_employee(
        db: Session,
        emp: Employee,
        cutoff_date: date,
        analysis_id: str,
        asmt_index: int
    ) -> SupportAssessment:
        """Evaluate a single employee with pre-outcome barrier and explainable factor attribution."""
        # 1. Workload evaluation (pre-outcome up to cutoff_date)
        workloads = db.query(WorkloadSnapshot).filter(
            WorkloadSnapshot.employee_id == emp.employee_id,
            WorkloadSnapshot.period_date <= cutoff_date
        ).order_by(WorkloadSnapshot.period_date.desc()).limit(3).all()

        workload_score = 20.0
        workload_factors = []
        if workloads:
            avg_hours = sum(float(w.avg_weekly_hours) for w in workloads) / len(workloads)
            max_ot = max((w.consecutive_overtime_weeks for w in workloads), default=0)
            has_benign = any(w.is_benign_surge for w in workloads)

            if avg_hours >= 48.0 and not has_benign:
                workload_score = 85.0
                workload_factors.append(FactorAttribution(
                    category="WORKLOAD",
                    signal_name="Sustained High Overtime",
                    raw_value=f"{avg_hours:.1f} hrs/wk avg ({max_ot} consec. OT weeks)",
                    impact_level="HIGH",
                    supportive_guidance="Discuss project bandwidth and schedule temporary workload rebalancing."
                ))
            elif avg_hours >= 44.0:
                workload_score = 60.0
                workload_factors.append(FactorAttribution(
                    category="WORKLOAD",
                    signal_name="Elevated Workload",
                    raw_value=f"{avg_hours:.1f} hrs/wk avg",
                    impact_level="MEDIUM",
                    supportive_guidance="Verify whether workload surge is linked to temporary release deadlines."
                ))
            elif has_benign:
                workload_score = 25.0
                workload_factors.append(FactorAttribution(
                    category="WORKLOAD",
                    signal_name="Recognized Launch Surge",
                    raw_value="Benign surge detected during release cycle",
                    impact_level="LOW",
                    supportive_guidance="Acknowledge team milestone contribution and ensure recovery downtime."
                ))

        # 2. Career velocity & Compensation stagnation
        latest_tenure = db.query(TenureSnapshot).filter(
            TenureSnapshot.employee_id == emp.employee_id,
            TenureSnapshot.snapshot_date <= cutoff_date
        ).order_by(TenureSnapshot.snapshot_date.desc()).first()

        months_in_role = latest_tenure.months_in_current_role if latest_tenure else 12
        career_score = 15.0
        career_factors = []

        if months_in_role >= 30:
            career_score += 55.0
            career_factors.append(FactorAttribution(
                category="CAREER_GROWTH",
                signal_name="Extended Role Tenure Without Movement",
                raw_value=f"{months_in_role} months in current role",
                impact_level="HIGH",
                supportive_guidance="Conduct career pathing discussion; explore internal lateral or promotional readiness."
            ))
        elif months_in_role >= 20:
            career_score += 30.0
            career_factors.append(FactorAttribution(
                category="CAREER_GROWTH",
                signal_name="Approaching Career Milestone Window",
                raw_value=f"{months_in_role} months in current role",
                impact_level="MEDIUM",
                supportive_guidance="Review skill development roadmap and upcoming leadership opportunities."
            ))

        # Compensation equity against band midpoint
        band = None
        if emp.role and emp.role.band_id:
            band = db.query(CompensationBand).filter(CompensationBand.band_id == emp.role.band_id).first()

        if band and float(band.mid_salary) > 0:
            curr_sal = float(emp.current_salary)
            mid_sal = float(band.mid_salary)
            comp_ratio = curr_sal / mid_sal
            if comp_ratio < 0.90:
                career_score += 25.0
                career_factors.append(FactorAttribution(
                    category="COMPENSATION",
                    signal_name="Compensation Below Band Midpoint",
                    raw_value=f"{comp_ratio*100:.0f}% of market midpoint (${curr_sal:,.0f} vs ${mid_sal:,.0f})",
                    impact_level="MEDIUM",
                    supportive_guidance="Partner with HR compensation team to schedule an equity adjustment review."
                ))

        career_score = min(100.0, career_score)

        # 3. Engagement trajectory (Strict Neutrality: Missing surveys do NOT increase score!)
        surveys = db.query(EngagementSurvey).filter(
            EngagementSurvey.employee_id == emp.employee_id,
            EngagementSurvey.survey_date <= cutoff_date
        ).order_by(EngagementSurvey.survey_date.asc()).all()

        engagement_score = 25.0
        engagement_factors = []
        valid_surveys = [s for s in surveys if not s.is_missing and s.composite_engagement is not None]

        if not valid_surveys:
            engagement_factors.append(FactorAttribution(
                category="ENGAGEMENT",
                signal_name="Pulse Survey Neutral Absence",
                raw_value="No optional survey submissions on file",
                impact_level="LOW",
                supportive_guidance="Encourage voluntary feedback participation without pressure."
            ))
        else:
            latest_val = float(valid_surveys[-1].composite_engagement)
            engagement_score = max(0.0, (5.0 - latest_val) * 20.0)

            if len(valid_surveys) >= 2:
                earlier_val = float(valid_surveys[0].composite_engagement)
                delta = round(latest_val - earlier_val, 2)
                if delta <= -0.80:
                    engagement_score += 45.0
                    engagement_factors.append(FactorAttribution(
                        category="ENGAGEMENT",
                        signal_name="Downward Engagement Trend",
                        raw_value=f"Score shifted from {earlier_val:.1f} to {latest_val:.1f} (Δ {delta:+.1f})",
                        impact_level="HIGH",
                        supportive_guidance="Schedule informal touchpoint to listen to recent workplace friction points."
                    ))
                elif latest_val < 3.0:
                    engagement_factors.append(FactorAttribution(
                        category="ENGAGEMENT",
                        signal_name="Low Sentiment Score",
                        raw_value=f"Latest pulse composite: {latest_val:.1f} / 5.0",
                        impact_level="MEDIUM",
                        supportive_guidance="Explore satisfaction with manager support and team collaboration dynamics."
                    ))

        engagement_score = min(100.0, engagement_score)

        # Composite score weighting: Workload 40%, Career 35%, Engagement 25%
        raw_composite = (workload_score * 0.40) + (career_score * 0.35) + (engagement_score * 0.25)
        composite_score = round(min(100.0, max(0.0, raw_composite)), 1)

        if composite_score >= 70.0:
            tier = "HIGH"
        elif composite_score >= 40.0:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        all_factors = workload_factors + career_factors + engagement_factors

        # Actionable 1-on-1 recommendations
        recommended_topics = set()
        for f in all_factors:
            if f.category == "WORKLOAD":
                recommended_topics.add("Sprint Workload Rebalancing & Capacity Planning")
            elif f.category == "CAREER_GROWTH":
                recommended_topics.add("Quarterly Career Growth & Progression Roadmap")
            elif f.category == "COMPENSATION":
                recommended_topics.add("Annual Compensation & Market Equity Alignment")
            elif f.category == "ENGAGEMENT":
                recommended_topics.add("Open 1-on-1 Pulse & Well-being Check-in")

        if not recommended_topics:
            recommended_topics.add("Routine Supportive 1-on-1 Catchup")

        asmt_id = f"ASMT-2026-{asmt_index:06d}"

        return SupportAssessment(
            assessment_id=asmt_id,
            analysis_id=analysis_id,
            employee_id=emp.employee_id,
            composite_priority_score=composite_score,
            priority_tier=tier,
            workload_strain_score=round(workload_score, 1),
            career_stagnation_score=round(career_score, 1),
            engagement_trajectory_score=round(engagement_score, 1),
            factors_json=json.dumps([f.model_dump() for f in all_factors]),
            recommended_topics_json=json.dumps(sorted(list(recommended_topics))),
            created_at=datetime.utcnow()
        )

    @staticmethod
    def list_runs(db: Session, limit: int = 20) -> List[AnalysisRunResponse]:
        """List past analysis runs."""
        runs = db.query(AnalysisRun).order_by(AnalysisRun.execution_date.desc()).limit(limit).all()
        return [
            AnalysisRunResponse(
                analysis_id=r.analysis_id,
                execution_date=r.execution_date,
                rule_version=r.rule_version,
                cutoff_date=r.cutoff_date,
                cohort_size=r.cohort_size,
                high_priority_count=r.high_priority_count,
                medium_priority_count=r.medium_priority_count,
                status=r.status
            )
            for r in runs
        ]

    @staticmethod
    def list_assessments(
        db: Session,
        analysis_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SupportAssessmentDetailResponse]:
        """List support assessments with explainability details."""
        query = db.query(SupportAssessment).join(SupportAssessment.employee)
        if analysis_id:
            query = query.filter(SupportAssessment.analysis_id == analysis_id)
        if employee_id:
            query = query.filter(SupportAssessment.employee_id == employee_id)
        if tier:
            query = query.filter(SupportAssessment.priority_tier == tier)

        assessments = query.order_by(SupportAssessment.composite_priority_score.desc()).offset(offset).limit(limit).all()

        results = []
        for a in assessments:
            factors_raw = json.loads(a.factors_json) if a.factors_json else []
            topics_raw = json.loads(a.recommended_topics_json) if a.recommended_topics_json else []

            # Compute data completeness percentage
            surveys_count = db.query(EngagementSurvey).filter(
                EngagementSurvey.employee_id == a.employee_id,
                EngagementSurvey.is_missing == False
            ).count()
            workload_count = db.query(WorkloadSnapshot).filter(
                WorkloadSnapshot.employee_id == a.employee_id
            ).count()

            # Expecting 8 quarters total
            completeness = round(((surveys_count + workload_count) / 16.0) * 100.0, 1)
            completeness = min(100.0, max(25.0, completeness))

            results.append(SupportAssessmentDetailResponse(
                assessment_id=a.assessment_id,
                analysis_id=a.analysis_id,
                employee_id=a.employee_id,
                employee_name=a.employee.full_name if a.employee else "Unknown",
                department=a.employee.team.department if (a.employee and a.employee.team) else "N/A",
                role_title=a.employee.role.title if (a.employee and a.employee.role) else "N/A",
                composite_priority_score=float(a.composite_priority_score),
                priority_tier=a.priority_tier,
                workload_strain_score=float(a.workload_strain_score),
                career_stagnation_score=float(a.career_stagnation_score),
                engagement_trajectory_score=float(a.engagement_trajectory_score),
                data_completeness_percentage=completeness,
                factors=[FactorAttribution(**f) for f in factors_raw],
                recommended_topics=topics_raw,
                created_at=a.created_at
            ))
        return results

    @staticmethod
    def get_assessment(db: Session, assessment_id: str) -> SupportAssessmentDetailResponse:
        """Fetch single assessment by ID."""
        a = db.query(SupportAssessment).filter(SupportAssessment.assessment_id == assessment_id).first()
        if not a:
            raise HTTPException(status_code=404, detail=f"Assessment '{assessment_id}' not found.")

        factors_raw = json.loads(a.factors_json) if a.factors_json else []
        topics_raw = json.loads(a.recommended_topics_json) if a.recommended_topics_json else []

        return SupportAssessmentDetailResponse(
            assessment_id=a.assessment_id,
            analysis_id=a.analysis_id,
            employee_id=a.employee_id,
            employee_name=a.employee.full_name if a.employee else "Unknown",
            department=a.employee.team.department if (a.employee and a.employee.team) else "N/A",
            role_title=a.employee.role.title if (a.employee and a.employee.role) else "N/A",
            composite_priority_score=float(a.composite_priority_score),
            priority_tier=a.priority_tier,
            workload_strain_score=float(a.workload_strain_score),
            career_stagnation_score=float(a.career_stagnation_score),
            engagement_trajectory_score=float(a.engagement_trajectory_score),
            data_completeness_percentage=100.0,
            factors=[FactorAttribution(**f) for f in factors_raw],
            recommended_topics=topics_raw,
            created_at=a.created_at
        )
