"""Application entrypoint forwarding to backend.app.main."""
from backend.app.main import app, health_check

__all__ = ["app", "health_check"]
