from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _as_int(value: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value) if value is not None else default
    except ValueError:
        parsed = default
    return max(minimum, min(maximum, parsed))


def _as_float(value: str | None, default: float, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value) if value is not None else default
    except ValueError:
        parsed = default
    return max(minimum, min(maximum, parsed))


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    docs_dir: Path
    index_dir: Path
    logs_dir: Path
    chunk_size: int = 1_400
    chunk_overlap: int = 220
    min_page_chars: int = 60
    top_k: int = 5
    candidate_k: int = 24
    retrieval_threshold: float = 1.0
    llm_provider: str = "extractive"
    openai_model: str = "gpt-5.6-luna"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    oci_genai_api_key: str | None = None
    oci_genai_region: str = "us-chicago-1"
    oci_genai_project: str | None = None
    oci_genai_model: str = "openai.gpt-oss-120b"
    log_content: bool = False
    app_env: str = "development"

    @classmethod
    def from_env(cls, root_dir: Path | None = None) -> Settings:
        root = (root_dir or Path(__file__).resolve().parents[1]).resolve()

        def local_path(name: str, default: str) -> Path:
            candidate = Path(os.getenv(name, default))
            return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()

        return cls(
            root_dir=root,
            docs_dir=local_path("DOCS_DIR", "docs"),
            index_dir=local_path("INDEX_DIR", "data/index"),
            logs_dir=local_path("LOGS_DIR", "logs"),
            chunk_size=_as_int(os.getenv("CHUNK_SIZE"), 1_400, 500, 4_000),
            chunk_overlap=_as_int(os.getenv("CHUNK_OVERLAP"), 220, 0, 800),
            min_page_chars=_as_int(os.getenv("MIN_PAGE_CHARS"), 60, 20, 500),
            top_k=_as_int(os.getenv("TOP_K"), 5, 2, 10),
            candidate_k=_as_int(os.getenv("CANDIDATE_K"), 24, 5, 80),
            retrieval_threshold=_as_float(os.getenv("RETRIEVAL_THRESHOLD"), 1.0, 0.0, 20.0),
            llm_provider=os.getenv("LLM_PROVIDER", "extractive").strip().lower(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip(),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
            oci_genai_api_key=os.getenv("OCI_GENAI_API_KEY") or None,
            oci_genai_region=os.getenv("OCI_GENAI_REGION", "us-chicago-1").strip(),
            oci_genai_project=os.getenv("OCI_GENAI_PROJECT") or None,
            oci_genai_model=os.getenv("OCI_GENAI_MODEL", "openai.gpt-oss-120b").strip(),
            log_content=_as_bool(os.getenv("LOG_CONTENT"), False),
            app_env=os.getenv("APP_ENV", "development").strip().lower(),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.chunk_overlap >= self.chunk_size:
            errors.append("CHUNK_OVERLAP debe ser menor que CHUNK_SIZE.")
        if self.llm_provider not in {"extractive", "openai", "oci"}:
            errors.append("LLM_PROVIDER debe ser extractive, openai u oci.")
        if self.llm_provider == "openai" and not self.openai_api_key:
            errors.append("LLM_PROVIDER=openai requiere OPENAI_API_KEY.")
        if self.llm_provider == "oci":
            if not self.oci_genai_api_key:
                errors.append("LLM_PROVIDER=oci requiere OCI_GENAI_API_KEY.")
            if not self.oci_genai_project:
                errors.append("LLM_PROVIDER=oci requiere OCI_GENAI_PROJECT.")
        return errors
