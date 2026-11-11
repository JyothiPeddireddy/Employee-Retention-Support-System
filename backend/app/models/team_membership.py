"""TeamMembershipHistory model for effective-dated team assignment tracking."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Date, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class TeamMembershipHistory(Base):
    __tablename__ = "team_membership_history"

    membership_id = Column(String(64), primary_key=True)  # MEM-<emp_id>-<seq>
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    team_id = Column(String(32), ForeignKey("teams.team_id"), nullable=False)
    role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date, nullable=True)  # NULL indicates active current assignment
    is_current = Column(Boolean, default=True, nullable=False)
    transfer_reason = Column(String(50), default="HIRE", nullable=False)  # HIRE, INTERNAL_TRANSFER, REORGANIZATION, PROMOTION
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="team_memberships")
    team = relationship("Team", back_populates="memberships")
    role = relationship("Role", back_populates="team_memberships")

    __table_args__ = (
        CheckConstraint(
            "effective_end_date IS NULL OR effective_end_date >= effective_start_date",
            name="chk_membership_dates"
        ),
        Index("idx_membership_emp", "employee_id"),
        Index("idx_membership_team", "team_id"),
        Index("idx_membership_active", "employee_id", "is_current"),
    )
