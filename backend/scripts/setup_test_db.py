"""Utility script to verify and create PostgreSQL retention_test database."""
import os
import sys
import psycopg
from urllib.parse import urlparse

# Ensure backend and workspace are on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import get_settings


def setup_test_database():
    settings = get_settings()
    # Parse main database url
    main_url = settings.database_url
    cleaned_url = main_url.replace("postgresql+psycopg://", "postgresql://")
    parsed = urlparse(cleaned_url)

    admin_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/postgres"
    test_db_name = "retention_test"

    print(f"Connecting to PostgreSQL server at {parsed.hostname}:{parsed.port or 5432} to check '{test_db_name}'...")
    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,))
            exists = cur.fetchone() is not None
            if not exists:
                print(f"Creating test database '{test_db_name}'...")
                cur.execute(f"CREATE DATABASE {test_db_name}")
                print(f"Database '{test_db_name}' created successfully!")
            else:
                print(f"Test database '{test_db_name}' already exists.")

    # Now apply migrations to retention_test
    from alembic.config import Config
    from alembic import command
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    cfg = Config(alembic_ini_path)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    cfg.set_main_option("version_locations", os.path.join(backend_dir, "alembic", "versions"))
    test_db_url = f"postgresql+psycopg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/{test_db_name}"
    cfg.set_main_option("sqlalchemy.url", test_db_url)
    print(f"Running Alembic migrations on '{test_db_name}'...")
    command.upgrade(cfg, "head")
    print(f"Successfully migrated '{test_db_name}' to head!")


if __name__ == "__main__":
    setup_test_database()
