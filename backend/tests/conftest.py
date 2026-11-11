"""Pytest configuration and test database fixtures."""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.app.models.base import Base
from backend.scripts.seed_synthetic_data import DatabaseSeeder

# In-memory SQLite engine for rapid, deterministic test execution
TEST_DB_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False}
)

# Enforce foreign key constraints in SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh tables for each test and tear down afterwards."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def seeded_db(db_session):
    """Seed a small synthetic cohort (50 employees) for relationship and consistency tests."""
    seeder = DatabaseSeeder(seed=20261022, scale=50)
    seeder.run(db_session)
    return db_session
