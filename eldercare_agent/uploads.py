from __future__ import annotations

import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path

from .config import Settings
from .service import ElderCareAgent

MAX_UPLOAD_FILES = 5
MAX_UPLOAD_MB = 15
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


class UploadValidationError(ValueError):
    """Se genera cuando una carga del usuario no puede indexarse de forma segura."""


@dataclass(frozen=True)
class UploadedPDF:
    name: str
    data: bytes


@dataclass
class SessionCorpus:
    """Corpus BM25 aislado cuyos archivos existen solo durante una sesión del usuario."""

    agent: ElderCareAgent
    documents: tuple[str, ...]
    _temporary_directory: tempfile.TemporaryDirectory[str] = field(repr=False)

    def close(self) -> None:
        self._temporary_directory.cleanup()


def validate_uploads(files: list[UploadedPDF]) -> tuple[UploadedPDF, ...]:
    if not files:
        raise UploadValidationError("Selecciona al menos un archivo PDF.")
    if len(files) > MAX_UPLOAD_FILES:
        raise UploadValidationError(f"Puedes cargar como máximo {MAX_UPLOAD_FILES} archivos PDF.")

    validated: list[UploadedPDF] = []
    names: set[str] = set()
    for uploaded in files:
        normalized = uploaded.name.replace("\\", "/")
        safe_name = Path(normalized).name.strip()
        if not safe_name or normalized != safe_name:
            raise UploadValidationError("Uno de los archivos tiene un nombre no permitido.")
        if not safe_name.casefold().endswith(".pdf"):
            raise UploadValidationError(f"{safe_name}: el archivo debe tener extensión .pdf.")
        if safe_name.casefold() in names:
            raise UploadValidationError(f"{safe_name}: el nombre está repetido.")
        if not uploaded.data:
            raise UploadValidationError(f"{safe_name}: el archivo está vacío.")
        if len(uploaded.data) > MAX_UPLOAD_BYTES:
            raise UploadValidationError(
                f"{safe_name}: supera el límite de {MAX_UPLOAD_MB} MB por archivo."
            )
        if b"%PDF-" not in uploaded.data[:1024]:
            raise UploadValidationError(f"{safe_name}: el contenido no parece ser un PDF válido.")

        names.add(safe_name.casefold())
        validated.append(UploadedPDF(name=safe_name, data=uploaded.data))
    return tuple(validated)


def build_session_corpus(files: list[UploadedPDF], base_settings: Settings) -> SessionCorpus:
    """Construye un agente BM25 efímero y aislado por sesión a partir de PDF cargados."""

    validated = validate_uploads(files)
    temporary_directory = tempfile.TemporaryDirectory(prefix="aamia-upload-")
    root = Path(temporary_directory.name)
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    try:
        for uploaded in validated:
            (docs_dir / uploaded.name).write_bytes(uploaded.data)

        session_settings = replace(
            base_settings,
            root_dir=root,
            docs_dir=docs_dir,
            index_dir=root / "index",
            logs_dir=root / "logs",
        )
        agent, _rebuilt = ElderCareAgent.create(session_settings, force_rebuild=True)
        if not agent.retriever.chunks:
            raise UploadValidationError(
                "No se pudo extraer texto consultable. El PDF puede estar escaneado, vacío o protegido."
            )
        return SessionCorpus(
            agent=agent,
            documents=tuple(uploaded.name for uploaded in validated),
            _temporary_directory=temporary_directory,
        )
    except Exception:
        temporary_directory.cleanup()
        raise
