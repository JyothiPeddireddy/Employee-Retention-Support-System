"""Role model."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String(32), primary_key=True)  # e.g., ROLE-IC3-SWE
    title = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)  # IC1..IC6, M1..M3
    band_id = Column(String(32), ForeignKey("compensation_bands.band_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    compensation_band = relationship("CompensationBand", back_populates="roles")
    employees = relationship("Employee", back_populates="role", foreign_keys="Employee.current_role_id")
    team_memberships = relationship("TeamMembershipHistory", back_populates="role")

    __table_args__ = (
        Index("idx_roles_band", "band_id"),
        Index("idx_roles_level", "level"),
    )
