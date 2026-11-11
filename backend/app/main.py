"""Main FastAPI entrypoint for Supportive Retention Signal Engine."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.app.core.config import get_settings
from backend.app.routers import (
    employees_router,
    interventions_router,
    audit_router,
    generator_router
)
from backend.app.services.store import store_coordinator

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize store only if not already initialized
    if not store_coordinator.rules_engine:
        print("[Startup] Initializing Retention Signal Engine...")
        store_coordinator.initialize(scale=500)
    yield


app = FastAPI(
    title="Supportive Retention Signal Engine API",
    description="Analyze synthetic engagement, tenure, role and workload signals to prioritize supportive retention conversations.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(employees_router, prefix="/api/v1")
app.include_router(interventions_router, prefix="/api/v1")
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
            "message": "Supportive Retention Signal Engine API is running.",
            "docs": "/docs",
            "health": "/health"
        }
