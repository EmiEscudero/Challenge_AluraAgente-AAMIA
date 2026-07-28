"""AAMIA: un pequeño asistente RAG auditable para el cuidado de personas mayores."""

from .config import Settings
from .service import ElderCareAgent

__all__ = ["ElderCareAgent", "Settings"]
__version__ = "1.0.0"
