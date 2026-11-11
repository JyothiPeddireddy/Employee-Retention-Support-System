"""InterventionEvent model for lifecycle and event logging of retention touchpoints."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class InterventionEvent(Base):
    __tablename__ = "intervention_events"

    event_id = Column(String(64), primary_key=True)  # INTEV-2026-000001
    intervention_id = Column(String(64), ForeignKey("interventions.intervention_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # CREATED, NOTES_UPDATED, ACTION_COMPLETED, FOLLOW_UP_SCHEDULED, CANCELLED
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    intervention = relationship("Intervention", back_populates="events")
    actor = relationship("Employee", foreign_keys=[actor_id])

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('CREATED', 'NOTES_UPDATED', 'ACTION_COMPLETED', 'FOLLOW_UP_SCHEDULED', 'CANCELLED')",
            name="chk_event_type"
        ),
        Index("idx_intev_intervention", "intervention_id"),
        Index("idx_intev_timestamp", "event_timestamp"),
    )
