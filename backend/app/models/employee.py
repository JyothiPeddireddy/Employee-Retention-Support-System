"""Employee model with historical tracking and relationships."""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Numeric, Date, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, synonym
from backend.app.models.base import Base


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    LEAVE = "LEAVE"
    ATTRITED = "ATTRITED"


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(32), primary_key=True)  # Format: EMP-000001
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    email = Column(String(160), nullable=False, unique=True)
    hire_date = Column(Date, nullable=False)
    current_role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    current_team_id = Column(String(32), ForeignKey("teams.team_id"), nullable=False)
    current_salary = Column(Numeric(12, 2), nullable=False)
    manager_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=True)
    status = Column(String(20), default=EmployeeStatus.ACTIVE.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="employees", foreign_keys=[current_role_id])
    team = relationship("Team", back_populates="employees", foreign_keys=[current_team_id])
    manager = relationship("Employee", remote_side=[employee_id], backref="direct_reports")

    team_memberships = relationship("TeamMembershipHistory", back_populates="employee", cascade="all, delete-orphan")
    tenure_snapshots = relationship("TenureSnapshot", back_populates="employee", cascade="all, delete-orphan")
    workload_snapshots = relationship("WorkloadSnapshot", back_populates="employee", cascade="all, delete-orphan")
    engagement_surveys = relationship("EngagementSurvey", back_populates="employee", cascade="all, delete-orphan")
    promotion_histories = relationship("PromotionHistory", back_populates="employee", foreign_keys="PromotionHistory.employee_id", cascade="all, delete-orphan")
    attrition_outcome = relationship("AttritionOutcome", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="employee", foreign_keys="Intervention.employee_id", cascade="all, delete-orphan")
    support_assessments = relationship("SupportAssessment", back_populates="employee", cascade="all, delete-orphan")

    role_id = synonym("current_role_id")
    team_id = synonym("current_team_id")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'LEAVE', 'ATTRITED')",
            name="chk_employee_status"
        ),
        Index("idx_employees_team", "current_team_id"),
        Index("idx_employees_role", "current_role_id"),
        Index("idx_employees_manager", "manager_id"),
        Index("idx_employees_status", "status"),
    )
