"""Engagement Pulse Surveys API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import get_current_user, require_roles
from backend.app.schemas.engagement import SurveyCreate, SurveyUpdate, SurveyResponse
from backend.app.schemas.common import APIResponse
from backend.app.services.engagement_service import EngagementService

router = APIRouter(prefix="/engagement", tags=["Engagement Pulse Surveys"])


@router.post("/surveys", response_model=APIResponse[SurveyResponse], status_code=status.HTTP_201_CREATED)
def record_survey(
    payload: SurveyCreate,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a quarterly engagement pulse survey enforcing strict survey neutrality."""
    survey = EngagementService.create_survey(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Survey '{survey.survey_id}' recorded successfully.",
        data=SurveyResponse.model_validate(survey)
    )


@router.get("/surveys", response_model=APIResponse[List[SurveyResponse]])
def list_surveys(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    survey_quarter: Optional[str] = Query(None, description="Filter by quarter (e.g. 2026Q1)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve engagement survey history."""
    surveys = EngagementService.list_surveys(
        db=db,
        employee_id=employee_id,
        survey_quarter=survey_quarter,
        limit=limit,
        offset=offset
    )
    return APIResponse(
        success=True,
        message=f"Retrieved {len(surveys)} survey records.",
        data=surveys
    )


@router.put("/surveys/{survey_id}", response_model=APIResponse[SurveyResponse])
def update_survey(
    survey_id: str,
    payload: SurveyUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update permitted fields of an engagement survey."""
    survey = EngagementService.update_survey(
        db=db,
        survey_id=survey_id,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Survey '{survey_id}' updated successfully.",
        data=SurveyResponse.model_validate(survey)
    )
