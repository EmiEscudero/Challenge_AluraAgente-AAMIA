"""AAMIA: a small, auditable RAG assistant for elder care."""

from .config import Settings
from .service import ElderCareAgent

__all__ = ["ElderCareAgent", "Settings"]
__version__ = "1.0.0"
