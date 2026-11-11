"""PromotionHistory model for tracking career progression and salary velocity."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Numeric, Date, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class PromotionHistory(Base):
    __tablename__ = "promotion_histories"

    # Deterministic format: PROM-EMP-000001-0001
    promotion_id = Column(String(64), primary_key=True)
    employee_id = Column(String(32), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    effective_date = Column(Date, nullable=False)
    from_role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    to_role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    from_salary = Column(Numeric(12, 2), nullable=False)
    to_salary = Column(Numeric(12, 2), nullable=False)
    movement_type = Column(String(20), nullable=False)  # PROMOTION, LATERAL_TRANSFER
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="promotion_histories", foreign_keys=[employee_id])
    from_role = relationship("Role", foreign_keys=[from_role_id])
    to_role = relationship("Role", foreign_keys=[to_role_id])

    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('PROMOTION', 'LATERAL_TRANSFER')",
            name="chk_movement_type"
        ),
        Index("idx_promo_emp", "employee_id"),
        Index("idx_promo_date", "effective_date"),
    )
