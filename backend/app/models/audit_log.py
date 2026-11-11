"""AuditLog model for complete traceability and regulatory compliance."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Index
from backend.app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String(64), primary_key=True)  # AUD-2026-000001
    entity_name = Column(String(80), nullable=False)  # employees, interventions, etc.
    entity_id = Column(String(64), nullable=False)
    action = Column(String(30), nullable=False)  # INSERT, UPDATE, DELETE, ACCESS, INTERVENTION
    performed_by = Column(String(64), nullable=False)  # user_id or actor name
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    changes_json = Column(Text, nullable=True)  # JSON diff of state before/after
    ip_address = Column(String(45), nullable=True)

    __table_args__ = (
        Index("idx_audit_entity", "entity_name", "entity_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_actor", "performed_by"),
    )
