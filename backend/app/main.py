"""Main FastAPI entrypoint for Supportive Retention Signal Engine."""
import sys
import os

# Ensure both backend directory and workspace root are in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workspace_root = os.path.dirname(backend_dir)
for p in [workspace_root, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import get_settings
from backend.app.routers import (
    auth_router,
    employees_router,
    teams_router,
    roles_router,
    engagement_router,
    workload_router,
    compensation_router,
    assessments_router,
    interventions_router,
    analytics_router,
    data_quality_router,
    admin_router,
    audit_router,
    generator_router
)
from backend.app.services.store import store_coordinator

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize store coordinator if not already initialized
    if not store_coordinator.rules_engine:
        print("[Startup] Initializing Retention Signal Engine...")
        store_coordinator.initialize(scale=500)
    yield


app = FastAPI(
    title="Employee Retention Support System API",
    description="Analyze synthetic engagement, tenure, role and workload signals to prioritize supportive retention conversations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler ensuring CORS headers and clean error reporting."""
    logging.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "detail": str(exc)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation errors ensuring clear frontend reporting."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "detail": exc.errors()
        }
    )

# Mount all API Routers under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
app.include_router(engagement_router, prefix="/api/v1")
app.include_router(workload_router, prefix="/api/v1")
app.include_router(compensation_router, prefix="/api/v1")
app.include_router(assessments_router, prefix="/api/v1")
app.include_router(interventions_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(data_quality_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(generator_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Supportive Retention Signal Engine",
        "version": "1.0.0"
    }


# Mount frontend static directory if exists
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dist = os.path.join(workspace_root, "frontend", "dist")
frontend_dir = frontend_dist if os.path.exists(frontend_dist) else os.path.join(workspace_root, "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", tags=["Frontend"])
    def serve_frontend_root():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {
            "message": "Employee Retention Support System API is running.",
            "docs": "/docs",
            "health": "/health"
        }
