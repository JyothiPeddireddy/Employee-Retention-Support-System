"""Package exports for all API routers."""
from backend.app.routers.auth import router as auth_router
from backend.app.routers.employees import router as employees_router
from backend.app.routers.teams import router as teams_router
from backend.app.routers.roles import router as roles_router
from backend.app.routers.engagement import router as engagement_router
from backend.app.routers.workload import router as workload_router
from backend.app.routers.compensation import router as compensation_router
from backend.app.routers.assessments import router as assessments_router
from backend.app.routers.interventions import router as interventions_router
from backend.app.routers.analytics import router as analytics_router
from backend.app.routers.data_quality import router as data_quality_router
from backend.app.routers.admin import router as admin_router
from backend.app.routers.audit import router as audit_router
from backend.app.routers.generator import router as generator_router

__all__ = [
    "auth_router",
    "employees_router",
    "teams_router",
    "roles_router",
    "engagement_router",
    "workload_router",
    "compensation_router",
    "assessments_router",
    "interventions_router",
    "analytics_router",
    "data_quality_router",
    "admin_router",
    "audit_router",
    "generator_router"
]
