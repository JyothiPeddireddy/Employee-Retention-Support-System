"""Team model."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(String(32), primary_key=True)  # e.g., TEAM-ENG-01
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employees = relationship("Employee", back_populates="team", foreign_keys="Employee.current_team_id")
    memberships = relationship("TeamMembershipHistory", back_populates="team")

    __table_args__ = (
        Index("idx_teams_dept", "department"),
    )
