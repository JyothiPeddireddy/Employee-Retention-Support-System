"""Compensation & Career Promotion History API Router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import require_roles
from backend.app.schemas.compensation import (
    BandCreate, BandUpdate, BandResponse, PromotionCreate, PromotionResponse
)
from backend.app.schemas.common import APIResponse
from backend.app.services.compensation_service import CompensationService

router = APIRouter(prefix="/compensation", tags=["Compensation & Career Promotions"])


@router.post("/bands", response_model=APIResponse[BandResponse], status_code=status.HTTP_201_CREATED)
def create_compensation_band(
    payload: BandCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new standardized compensation band."""
    band = CompensationService.create_band(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Band '{band.band_id}' created successfully.",
        data=BandResponse.model_validate(band)
    )


@router.get("/bands", response_model=APIResponse[List[BandResponse]])
def list_compensation_bands(
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List standard compensation bands."""
    bands = CompensationService.list_bands(db=db, department=department)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(bands)} compensation bands.",
        data=bands
    )


@router.put("/bands/{band_id}", response_model=APIResponse[BandResponse])
def update_compensation_band(
    band_id: str,
    payload: BandUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update an existing compensation band."""
    band = CompensationService.update_band(
        db=db,
        band_id=band_id,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Band '{band.band_id}' updated successfully.",
        data=BandResponse.model_validate(band)
    )


@router.post("/promotions", response_model=APIResponse[PromotionResponse], status_code=status.HTTP_201_CREATED)
def record_promotion(
    payload: PromotionCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Record an employee promotion or lateral career move."""
    prom = CompensationService.record_promotion(
        db=db,
        req=payload,
        performed_by=current_user.user_id
    )
    return APIResponse(
        success=True,
        message=f"Promotion '{prom.promotion_id}' recorded successfully.",
        data=PromotionResponse.model_validate(prom)
    )


@router.get("/promotions", response_model=APIResponse[List[PromotionResponse]])
def list_promotions(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve promotion and career movement history."""
    proms = CompensationService.list_promotions(db=db, employee_id=employee_id)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(proms)} promotion records.",
        data=proms
    )
