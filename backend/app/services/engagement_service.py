"""Service for Engagement Pulse Surveys & Survey Neutrality Enforcement."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.engagement_survey import EngagementSurvey
from backend.app.models.employee import Employee
from backend.app.schemas.engagement import SurveyCreate, SurveyUpdate, SurveyResponse
from backend.app.services.audit_service import AuditService


class EngagementService:
    @staticmethod
    def create_survey(db: Session, req: SurveyCreate, performed_by: str) -> EngagementSurvey:
        """Record quarterly engagement survey enforcing strict neutrality."""
        emp = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail=f"Employee '{req.employee_id}' not found.")

        # Prevent duplicate quarterly survey
        existing = db.query(EngagementSurvey).filter(
            EngagementSurvey.employee_id == req.employee_id,
            EngagementSurvey.survey_quarter == req.survey_quarter
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Survey for employee '{req.employee_id}' in quarter '{req.survey_quarter}' already exists."
            )

        survey_id = req.survey_id
        if not survey_id:
            count = db.query(EngagementSurvey).count() + 1
            survey_id = f"SURV-2026-{count:06d}"

        if req.is_missing:
            comp_score = None
            sat = None
            wlb = None
            cg = None
            mgr = None
        else:
            sat = req.satisfaction_score
            wlb = req.work_life_balance_score
            cg = req.career_growth_score
            mgr = req.manager_support_score
            comp_score = round((sat + wlb + cg + mgr) / 4.0, 2)

        survey = EngagementSurvey(
            survey_id=survey_id,
            employee_id=req.employee_id,
            survey_quarter=req.survey_quarter,
            survey_date=req.survey_date,
            is_missing=req.is_missing,
            satisfaction_score=sat,
            work_life_balance_score=wlb,
            career_growth_score=cg,
            manager_support_score=mgr,
            composite_engagement=comp_score
        )
        db.add(survey)
        db.flush()

        AuditService.log_action(
            db=db,
            entity_name="engagement_surveys",
            entity_id=survey_id,
            action="INSERT",
            performed_by=performed_by,
            changes={"employee_id": req.employee_id, "quarter": req.survey_quarter, "is_missing": req.is_missing}
        )

        db.commit()
        db.refresh(survey)
        return survey

    @staticmethod
    def list_surveys(
        db: Session,
        employee_id: Optional[str] = None,
        survey_quarter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SurveyResponse]:
        """Retrieve engagement survey history."""
        query = db.query(EngagementSurvey)
        if employee_id:
            query = query.filter(EngagementSurvey.employee_id == employee_id)
        if survey_quarter:
            query = query.filter(EngagementSurvey.survey_quarter == survey_quarter)

        surveys = query.order_by(EngagementSurvey.survey_date.desc()).offset(offset).limit(limit).all()

        return [
            SurveyResponse(
                survey_id=s.survey_id,
                employee_id=s.employee_id,
                survey_quarter=s.survey_quarter,
                survey_date=s.survey_date,
                is_missing=s.is_missing,
                satisfaction_score=float(s.satisfaction_score) if s.satisfaction_score is not None else None,
                work_life_balance_score=float(s.work_life_balance_score) if s.work_life_balance_score is not None else None,
                career_growth_score=float(s.career_growth_score) if s.career_growth_score is not None else None,
                manager_support_score=float(s.manager_support_score) if s.manager_support_score is not None else None,
                composite_engagement=float(s.composite_engagement) if s.composite_engagement is not None else None,
                created_at=s.created_at
            )
            for s in surveys
        ]

    @staticmethod
    def update_survey(
        db: Session,
        survey_id: str,
        req: SurveyUpdate,
        performed_by: str
    ) -> EngagementSurvey:
        """Update permitted survey fields, recomputing composite engagement."""
        survey = db.query(EngagementSurvey).filter(EngagementSurvey.survey_id == survey_id).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey '{survey_id}' not found.")

        if survey.is_missing:
            raise HTTPException(
                status_code=400,
                detail="Cannot set numerical scores on a missing survey submission without unmarking missing status."
            )

        if req.satisfaction_score is not None:
            survey.satisfaction_score = req.satisfaction_score
        if req.work_life_balance_score is not None:
            survey.work_life_balance_score = req.work_life_balance_score
        if req.career_growth_score is not None:
            survey.career_growth_score = req.career_growth_score
        if req.manager_support_score is not None:
            survey.manager_support_score = req.manager_support_score

        # Recompute composite
        survey.composite_engagement = round(
            (float(survey.satisfaction_score) + float(survey.work_life_balance_score) + float(survey.career_growth_score) + float(survey.manager_support_score)) / 4.0,
            2
        )

        AuditService.log_action(
            db=db,
            entity_name="engagement_surveys",
            entity_id=survey_id,
            action="UPDATE",
            performed_by=performed_by,
            changes={"composite": float(survey.composite_engagement)}
        )

        db.commit()
        db.refresh(survey)
        return survey
