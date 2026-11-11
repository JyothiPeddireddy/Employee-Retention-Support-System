"""Diagnostic script to check local PostgreSQL connection and guide the user in plain English."""
import sys
import os
from sqlalchemy import text
from backend.app.core.config import get_settings
from backend.app.database.session import engine


def check_database():
    settings = get_settings()
    print("=" * 70)
    print("Employee Retention Support System - Database Connection Diagnostic")
    print("=" * 70)
    print(f"Target Database URL: {settings.database_url}")
    print(f"Environment:         {settings.environment}")
    print("-" * 70)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print("[SUCCESS] Successfully connected to the database!")
            print(f"Database Server Version: {result[0]}")
            return True
    except Exception as e:
        err_msg = str(e)
        print(f"[CONNECTION FAILED] Could not connect to the PostgreSQL server.")
        print(f"\nExact Error Encountered:\n{err_msg}\n")
        print("=" * 70)
        print("HOW TO FIX THIS (Simple English Instructions):")
        print("=" * 70)
        print("1. START YOUR LOCAL POSTGRESQL SERVICE:")
        print("   On Windows, open Command Prompt as Administrator and run:")
        print("       net start postgresql-x64-18")
        print("   (Or press Windows Key + R, type 'services.msc', find 'postgresql-x64-18',")
        print("    right-click it, and click 'Start').")
        print()
        print("2. CREATE THE DATABASE IN PGADMIN OR PSQL:")
        print("   Open pgAdmin 4 or psql and run:")
        print("       CREATE DATABASE retention_db;")
        print()
        print("3. CONFIGURE YOUR PASSWORD IN .env:")
        print("   In the backend/ folder, copy .env.example to .env and set your password:")
        print("       DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/retention_db")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
