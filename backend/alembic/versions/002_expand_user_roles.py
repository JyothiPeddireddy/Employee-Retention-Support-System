"""Expand user roles to include EMPLOYEE, IT_OPS_PARTNER, and ADMIN.

Revision ID: 002_expand_user_roles
Revises: 001_initial_schema
Create Date: 2026-11-11 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_expand_user_roles"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("chk_user_role", "app_users", type_="check")
    op.create_check_constraint(
        "chk_user_role",
        "app_users",
        "role IN ('EMPLOYEE', 'MANAGER', 'HR_PARTNER', 'IT_OPS_PARTNER', 'ADMIN', 'SYSTEM_ADMIN', 'AUDITOR')"
    )


def downgrade() -> None:
    op.drop_constraint("chk_user_role", "app_users", type_="check")
    op.create_check_constraint(
        "chk_user_role",
        "app_users",
        "role IN ('HR_PARTNER', 'MANAGER', 'SYSTEM_ADMIN', 'AUDITOR')"
    )
