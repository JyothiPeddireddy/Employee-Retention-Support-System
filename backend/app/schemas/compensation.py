"""Schemas for Compensation Bands and Promotion History."""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class BandCreate(BaseModel):
    band_id: str = Field(..., example="BAND-IC5")
    name: str = Field("Senior Staff Band", example="Senior Staff Band")
    min_salary: float = Field(..., gt=0, example=140000.0)
    mid_salary: float = Field(..., gt=0, example=170000.0)
    max_salary: float = Field(..., gt=0, example=210000.0)
    currency: str = Field("USD", max_length=3, example="USD")


class BandUpdate(BaseModel):
    name: Optional[str] = None
    min_salary: Optional[float] = Field(None, gt=0, example=145000.0)
    mid_salary: Optional[float] = Field(None, gt=0, example=175000.0)
    max_salary: Optional[float] = Field(None, gt=0, example=215000.0)
    currency: Optional[str] = Field(None, max_length=3, example="USD")


class BandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    band_id: str
    name: str
    min_salary: float
    mid_salary: float
    max_salary: float
    currency: str


class PromotionCreate(BaseModel):
    promotion_id: Optional[str] = Field(None, example="PROM-000001")
    employee_id: str = Field(..., example="EMP-000001")
    effective_date: date = Field(..., example="2026-01-15")
    from_role_id: str = Field(..., example="ROLE-IC1-SWE")
    to_role_id: str = Field(..., example="ROLE-IC2-SWE")
    from_salary: float = Field(..., gt=0, example=110000.0)
    to_salary: float = Field(..., gt=0, example=130000.0)
    movement_type: str = Field("PROMOTION", description="PROMOTION or LATERAL", example="PROMOTION")


class PromotionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    promotion_id: str
    employee_id: str
    effective_date: date
    from_role_id: str
    to_role_id: str
    from_salary: float
    to_salary: float
    movement_type: str
    created_at: datetime
