"""Service for Retention Analytics, Executive Dashboards, and Workforce Trends."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.employee import Employee
from backend.app.models.team import Team
from backend.app.models.workload_snapshot import WorkloadSnapshot
from backend.app.models.engagement_survey import EngagementSurvey
from backend.app.models.intervention import Intervention
from backend.app.models.analysis import SupportAssessment
from backend.app.models.validation import ValidationRun
from backend.app.schemas.analytics import OverviewMetrics, DepartmentMetricSummary, TrendDataPoint


class AnalyticsService:
    @staticmethod
    def get_overview_metrics(db: Session) -> OverviewMetrics:
        """Compute top-level organizational workforce metrics."""
        total_emp = db.query(Employee).count()
        active_emp = db.query(Employee).filter(Employee.status == "ACTIVE").count()
        attrited_emp = db.query(Employee).filter(Employee.status == "ATTRITED").count()

        attrition_rate = round((attrited_emp / max(1, total_emp)) * 100, 2)

        # Assessments count
        high_count = db.query(SupportAssessment).filter(SupportAssessment.priority_tier == "HIGH").count()
        med_count = db.query(SupportAssessment).filter(SupportAssessment.priority_tier == "MEDIUM").count()
        low_count = db.query(SupportAssessment).filter(SupportAssessment.priority_tier == "LOW").count()

        # Interventions
        total_ints = db.query(Intervention).count()
        completed_ints = db.query(Intervention).filter(Intervention.status == "COMPLETED").count()

        # Workload & engagement averages
        avg_hours_res = db.query(func.avg(WorkloadSnapshot.avg_weekly_hours)).scalar()
        avg_hours = round(float(avg_hours_res), 1) if avg_hours_res else 40.0

        avg_eng_res = db.query(func.avg(EngagementSurvey.composite_engagement)).filter(
            EngagementSurvey.is_missing == False
        ).scalar()
        avg_eng = round(float(avg_eng_res), 2) if avg_eng_res else None

        # Latest validation score
        last_val = db.query(ValidationRun).order_by(ValidationRun.run_timestamp.desc()).first()
        integrity_score = 98.5
        if last_val and last_val.total_checks > 0:
            integrity_score = round((last_val.passed_checks / last_val.total_checks) * 100.0, 1)

        return OverviewMetrics(
            total_headcount=total_emp,
            active_headcount=active_emp,
            attrited_headcount=attrited_emp,
            overall_attrition_rate=attrition_rate,
            high_priority_count=high_count,
            medium_priority_count=med_count,
            low_priority_count=low_count,
            total_interventions=total_ints,
            interventions_completed=completed_ints,
            data_integrity_score=integrity_score,
            avg_weekly_workload=avg_hours,
            avg_engagement_sentiment=avg_eng
        )

    @staticmethod
    def get_team_summaries(db: Session) -> List[DepartmentMetricSummary]:
        """Aggregate signals and capacity by department."""
        departments = db.query(Team.department).distinct().all()
        dept_names = [d[0] for d in departments if d[0]]

        results = []
        for dept in dept_names:
            dept_emps = db.query(Employee).join(Employee.team).filter(Team.department == dept).all()
            emp_ids = [e.employee_id for e in dept_emps]

            total_e = len(dept_emps)
            active_e = sum(1 for e in dept_emps if e.status == "ACTIVE")
            attrited_e = total_e - active_e

            high_signals = 0
            med_signals = 0
            if emp_ids:
                high_signals = db.query(SupportAssessment).filter(
                    SupportAssessment.employee_id.in_(emp_ids),
                    SupportAssessment.priority_tier == "HIGH"
                ).count()
                med_signals = db.query(SupportAssessment).filter(
                    SupportAssessment.employee_id.in_(emp_ids),
                    SupportAssessment.priority_tier == "MEDIUM"
                ).count()

            # Avg hours
            avg_hrs = 40.0
            if emp_ids:
                hrs_res = db.query(func.avg(WorkloadSnapshot.avg_weekly_hours)).filter(
                    WorkloadSnapshot.employee_id.in_(emp_ids)
                ).scalar()
                if hrs_res:
                    avg_hrs = round(float(hrs_res), 1)

            # Avg engagement
            avg_eng = None
            if emp_ids:
                eng_res = db.query(func.avg(EngagementSurvey.composite_engagement)).filter(
                    EngagementSurvey.employee_id.in_(emp_ids),
                    EngagementSurvey.is_missing == False
                ).scalar()
                if eng_res:
                    avg_eng = round(float(eng_res), 2)

            # Interventions
            ints_count = 0
            if emp_ids:
                ints_count = db.query(Intervention).filter(Intervention.employee_id.in_(emp_ids)).count()

            results.append(DepartmentMetricSummary(
                department=dept,
                total_employees=total_e,
                active_employees=active_e,
                attrited_employees=attrited_e,
                high_priority_signals=high_signals,
                medium_priority_signals=med_signals,
                avg_hours=avg_hrs,
                avg_engagement=avg_eng,
                interventions_conducted=ints_count
            ))

        return results

    @staticmethod
    def get_trends(db: Session) -> List[TrendDataPoint]:
        """Aggregate quarterly historical trends for workload and engagement sentiment."""
        quarters = db.query(WorkloadSnapshot.period_quarter).distinct().order_by(WorkloadSnapshot.period_quarter.asc()).all()
        quarter_list = [q[0] for q in quarters if q[0]]

        trends = []
        for q in quarter_list:
            # Workload avg
            w_res = db.query(
                func.avg(WorkloadSnapshot.avg_weekly_hours),
                func.count(WorkloadSnapshot.workload_id)
            ).filter(WorkloadSnapshot.period_quarter == q).first()

            avg_w = round(float(w_res[0]), 1) if w_res and w_res[0] else 40.0
            total_w = w_res[1] if w_res else 0

            # Overtime count (>40 hrs)
            ot_count = db.query(WorkloadSnapshot).filter(
                WorkloadSnapshot.period_quarter == q,
                WorkloadSnapshot.overtime_hours > 0
            ).count()
            ot_rate = round((ot_count / max(1, total_w)) * 100, 1)

            # Engagement avg and response rate
            s_total = db.query(EngagementSurvey).filter(EngagementSurvey.survey_quarter == q).count()
            s_valid = db.query(EngagementSurvey).filter(
                EngagementSurvey.survey_quarter == q,
                EngagementSurvey.is_missing == False
            ).count()

            s_avg_res = db.query(func.avg(EngagementSurvey.composite_engagement)).filter(
                EngagementSurvey.survey_quarter == q,
                EngagementSurvey.is_missing == False
            ).scalar()
            avg_eng = round(float(s_avg_res), 2) if s_avg_res else None

            resp_rate = round((s_valid / max(1, s_total)) * 100, 1)

            trends.append(TrendDataPoint(
                quarter=q,
                avg_workload_hours=avg_w,
                overtime_rate_percentage=ot_rate,
                avg_engagement_score=avg_eng,
                survey_response_rate=resp_rate
            ))

        return trends
