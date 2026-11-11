"""Pytest configuration and PostgreSQL test database fixtures."""
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workspace_dir = os.path.dirname(backend_dir)
for p in [workspace_dir, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Dedicated PostgreSQL test database URL
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:Hack2026@localhost:5432/retention_test"
)
os.environ["DATABASE_URL"] = TEST_DB_URL

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database.session import get_db, SessionLocal
from backend.app.main import app
from backend.app.models.app_user import AppUser, UserRole
from backend.app.core.security import get_password_hash, create_access_token
from backend.scripts.seed_synthetic_data import DatabaseSeeder

# Test engine bound to retention_test
test_engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

TRUNCATE_TABLES_SQL = """
TRUNCATE TABLE
    employees,
    teams,
    roles,
    compensation_bands,
    app_users,
    audit_logs,
    tenure_snapshots,
    workload_snapshots,
    engagement_surveys,
    promotion_histories,
    attrition_outcomes,
    interventions,
    intervention_events,
    validation_runs,
    validation_issues,
    analysis_runs,
    support_assessments
RESTART IDENTITY CASCADE;
"""


@pytest.fixture(scope="function")
def db_session():
    """Yield a pristine PostgreSQL test database session, truncated clean before each test."""
    with test_engine.connect() as conn:
        conn.execute(text(TRUNCATE_TABLES_SQL))
        conn.commit()

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def seeded_db(db_session):
    """Seed synthetic cohort (50 employees) with complete longitudinal history for testing."""
    seeder = DatabaseSeeder(seed=20261022, scale=50)
    seeder.run(db_session)
    return db_session


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with get_db dependency overridden to retention_test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def get_token_for(username: str, role: str, user_id: str = "USR-000001") -> dict:
    """Helper to generate Authorization header for API testing."""
    token = create_access_token(data={"sub": username, "role": role, "user_id": user_id})
    return {"Authorization": f"Bearer {token}"}
