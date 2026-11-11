"""Retention Analytics & Organizational Reporting API Router."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import require_roles
from backend.app.schemas.analytics import (
    OverviewMetrics, DepartmentMetricSummary, TrendDataPoint
)
from backend.app.schemas.common import APIResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Retention Analytics & Reports"])


@router.get("/overview", response_model=APIResponse[OverviewMetrics])
def get_overview_metrics(
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve high-level organizational workforce metrics and retention posture."""
    metrics = AnalyticsService.get_overview_metrics(db=db)
    return APIResponse(
        success=True,
        message="Overview metrics computed successfully.",
        data=metrics
    )


@router.get("/team-summary", response_model=APIResponse[List[DepartmentMetricSummary]])
def get_team_summaries(
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve department and team retention metrics breakdown."""
    summaries = AnalyticsService.get_team_summaries(db=db)
    return APIResponse(
        success=True,
        message=f"Retrieved metrics across {len(summaries)} departments.",
        data=summaries
    )


@router.get("/trends", response_model=APIResponse[List[TrendDataPoint]])
def get_longitudinal_trends(
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve quarterly longitudinal trends for workload and engagement sentiment."""
    trends = AnalyticsService.get_trends(db=db)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(trends)} quarters of historical trends.",
        data=trends
    )
