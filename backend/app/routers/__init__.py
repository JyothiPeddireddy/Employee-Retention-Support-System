"""Package exports for API routers."""
from backend.app.routers.employees import router as employees_router
from backend.app.routers.interventions import router as interventions_router
from backend.app.routers.audit import router as audit_router
from backend.app.routers.generator import router as generator_router

__all__ = [
    "employees_router",
    "interventions_router",
    "audit_router",
    "generator_router"
]
