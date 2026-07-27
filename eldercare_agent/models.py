from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    source: str
    page: int
    chunk_index: int
    title: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentChunk:
        return cls(**data)


@dataclass(frozen=True)
class SearchResult:
    chunk: DocumentChunk
    score: float
    rank: int


@dataclass
class AgentResponse:
    answer: str
    sources: list[SearchResult] = field(default_factory=list)
    provider: str = "extractive"
    latency_ms: int = 0
    confidence: str = "baja"
    emergency_notice: str | None = None
    fallback_used: bool = False
    error: str | None = None


@dataclass(frozen=True)
class IngestionReport:
    pdf_files: int
    pages_total: int
    pages_indexed: int
    pages_skipped: int
    chunks: int
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["errors"] = list(self.errors)
        return data
