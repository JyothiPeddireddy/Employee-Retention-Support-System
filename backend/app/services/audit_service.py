"""Service for recording audit logs for compliance, state transitions, and traceability."""
import json
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        entity_name: str,
        entity_id: str,
        action: str,  # INSERT, UPDATE, DELETE, ACCESS, INTERVENTION
        performed_by: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Create and persist an audit log entry."""
        count = db.query(AuditLog).count() + 1
        log_id = f"AUD-2026-{count:06d}"

        changes_str = json.dumps(changes, default=str) if changes else None

        log_entry = AuditLog(
            log_id=log_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            performed_by=performed_by,
            timestamp=datetime.utcnow(),
            changes_json=changes_str,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.flush()
        return log_entry
