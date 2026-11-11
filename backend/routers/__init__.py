"""Package exports for API routers."""
from backend.routers.employees import router as employees_router
from backend.routers.interventions import router as interventions_router
from backend.routers.audit import router as audit_router
from backend.routers.generator import router as generator_router

__all__ = [
    "employees_router",
    "interventions_router",
    "audit_router",
    "generator_router"
]
