"""Employee & Prioritized Retention API Router with RBAC."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.dependencies import get_current_user, require_roles, check_employee_access
from backend.app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeListItem, EmployeeDetail, EmployeeTimeline
)
from backend.app.schemas.prioritization import PrioritizedEmployee, PrioritizationSummary
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.employee_service import EmployeeService
from backend.app.services.store import store_coordinator

router = APIRouter(prefix="/employees", tags=["Employees & Retention Workbench"])


@router.post("", response_model=APIResponse[EmployeeDetail], status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new employee and initialize historical team membership."""
    emp = EmployeeService.create_employee(db=db, req=payload, performed_by=current_user.user_id)
    detail = EmployeeService.get_employee_detail(db=db, employee_id=emp.employee_id)
    return APIResponse(
        success=True,
        message=f"Employee '{emp.employee_id}' successfully created.",
        data=detail
    )


@router.get("", response_model=APIResponse[PaginatedResponse[EmployeeListItem]])
def list_employees(
    department: Optional[str] = Query(None, description="Filter by department"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, ATTRITED)"),
    search: Optional[str] = Query(None, description="Search by name, email, or employee ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("employee_id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List employees with filtering, searching, sorting, and pagination."""
    items, total = EmployeeService.list_employees(
        db=db,
        department=department,
        team_id=team_id,
        role_id=role_id,
        status_filter=status,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message=f"Retrieved {len(items)} employees.",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get("/prioritized", response_model=APIResponse[PaginatedResponse[PrioritizedEmployee]])
def get_prioritized_retention_list(
    department: Optional[str] = Query(None, description="Filter by department (e.g. Engineering, Sales)"),
    min_tier: Optional[str] = Query(None, description="Minimum priority tier: HIGH, MEDIUM, LOW"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN))
):
    """Fetch employees prioritized for supportive retention check-ins with explainability chips."""
    if not store_coordinator.rules_engine:
        store_coordinator.initialize(scale=500)

    dept_val = department if isinstance(department, str) else None
    tier_val = min_tier if isinstance(min_tier, str) else None

    evaluated = store_coordinator.rules_engine.evaluate_all(
        department_filter=dept_val,
        min_tier=tier_val
    )

    total = len(evaluated)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = evaluated[start_idx:end_idx]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message=f"Found {total} prioritized retention candidates.",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get("/summary", response_model=APIResponse[PrioritizationSummary])
def get_prioritization_summary(
    current_user: AppUser = Depends(require_roles(UserRole.MANAGER, UserRole.HR_PARTNER, UserRole.ADMIN))
):
    """Summary counts of supportive retention candidates by priority tier."""
    if not store_coordinator.rules_engine:
        store_coordinator.initialize(scale=500)

    all_evaluated = store_coordinator.rules_engine.evaluate_all()
    summary = store_coordinator.rules_engine.get_summary(all_evaluated)
    return APIResponse(success=True, data=summary)


@router.get("/{employee_id}", response_model=APIResponse[EmployeeDetail])
def get_employee_details(
    employee_id: str,
    current_user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed employee profile with permission verification."""
    check_employee_access(current_user=current_user, target_employee_id=employee_id, db=db)
    detail = EmployeeService.get_employee_detail(db=db, employee_id=employee_id)
    return APIResponse(
        success=True,
        message=f"Retrieved profile for employee '{employee_id}'.",
        data=detail
    )


@router.put("/{employee_id}", response_model=APIResponse[EmployeeDetail])
def update_employee_profile(
    employee_id: str,
    payload: EmployeeUpdate,
    current_user: AppUser = Depends(require_roles(UserRole.HR_PARTNER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update employee details and log audit trail."""
    EmployeeService.update_employee(
        db=db,
        employee_id=employee_id,
        req=payload,
        performed_by=current_user.user_id
    )
    detail = EmployeeService.get_employee_detail(db=db, employee_id=employee_id)
    return APIResponse(
        success=True,
        message=f"Employee '{employee_id}' updated successfully.",
        data=detail
    )


@router.get("/{employee_id}/timeline", response_model=APIResponse[EmployeeTimeline])
def get_employee_longitudinal_timeline(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[AppUser] = Depends(get_current_user)
):
    """Retrieve full 24-month longitudinal history (workload, survey scores, promotions) for 360 review."""
    if current_user:
        check_employee_access(current_user=current_user, target_employee_id=employee_id, db=db)
    timeline = EmployeeService.get_timeline(db=db, employee_id=employee_id)
    return APIResponse(
        success=True,
        message=f"Timeline retrieved for employee '{employee_id}'.",
        data=timeline
    )
