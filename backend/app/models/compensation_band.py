"""CompensationBand model."""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class CompensationBand(Base):
    __tablename__ = "compensation_bands"

    band_id = Column(String(32), primary_key=True)  # e.g., BAND-IC1
    name = Column(String(100), nullable=False)
    min_salary = Column(Numeric(12, 2), nullable=False)
    mid_salary = Column(Numeric(12, 2), nullable=False)
    max_salary = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("Role", back_populates="compensation_band")

    __table_args__ = (
        CheckConstraint(
            "min_salary <= mid_salary AND mid_salary <= max_salary",
            name="chk_salary_order"
        ),
    )
