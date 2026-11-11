"""AppUser model for authentication, authorization, and RBAC."""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class UserRole(str, enum.Enum):
    HR_PARTNER = "HR_PARTNER"
    MANAGER = "MANAGER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    AUDITOR = "AUDITOR"


class AppUser(Base):
    __tablename__ = "app_users"

    user_id = Column(String(32), primary_key=True)  # USR-000001
    username = Column(String(80), nullable=False, unique=True)
    email = Column(String(160), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default=UserRole.HR_PARTNER.value, nullable=False)
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=True)  # Optional linked employee
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee")

    __table_args__ = (
        CheckConstraint(
            "role IN ('HR_PARTNER', 'MANAGER', 'SYSTEM_ADMIN', 'AUDITOR')",
            name="chk_user_role"
        ),
        Index("idx_users_role", "role"),
    )
