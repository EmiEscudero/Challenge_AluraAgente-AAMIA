from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .config import Settings
from .models import DocumentChunk, IngestionReport
from .text import normalize_text, stable_hash


def _safe_metadata(reader: PdfReader) -> dict[str, str]:
    metadata = reader.metadata or {}
    return {str(key): str(value) for key, value in metadata.items() if value is not None}


def _split_page(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]

    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > size:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                end = min(len(paragraph), start + size)
                if end < len(paragraph):
                    boundary = paragraph.rfind(" ", start + size // 2, end)
                    if boundary > start:
                        end = boundary
                piece = paragraph[start:end].strip()
                if piece:
                    chunks.append(piece)
                if end >= len(paragraph):
                    break
                next_start = max(start + 1, end - overlap)
                if next_start > 0 and next_start < len(paragraph) and paragraph[next_start - 1].isalnum():
                    boundary = paragraph.find(" ", next_start)
                    next_start = boundary + 1 if boundary != -1 else next_start
                start = next_start
            continue

        proposed = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(proposed) <= size:
            current = proposed
            continue

        chunks.append(current.strip())
        tail = current[-overlap:].lstrip() if overlap else ""
        if overlap and len(current) > overlap and tail and current[-overlap - 1].isalnum():
            first_space = tail.find(" ")
            if first_space != -1:
                tail = tail[first_space + 1:].lstrip()
        current = f"{tail}\n\n{paragraph}".strip()

    if current:
        chunks.append(current.strip())
    return [chunk for chunk in chunks if len(chunk) >= 40]


def discover_pdfs(docs_dir: Path) -> list[Path]:
    if not docs_dir.exists():
        return []
    return sorted(
        (path for path in docs_dir.rglob("*.pdf") if path.is_file()),
        key=lambda path: path.name.casefold(),
    )


def corpus_manifest(docs_dir: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in discover_pdfs(docs_dir):
        stat = path.stat()
        files.append({
            "name": str(path.relative_to(docs_dir)).replace("\\", "/"),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        })
    encoded = json.dumps(files, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return {"fingerprint": hashlib.sha256(encoded).hexdigest(), "files": files}


def ingest_pdfs(settings: Settings) -> tuple[list[DocumentChunk], IngestionReport, dict[str, Any]]:
    files = discover_pdfs(settings.docs_dir)
    chunks: list[DocumentChunk] = []
    pages_total = 0
    pages_indexed = 0
    pages_skipped = 0
    errors: list[str] = []
    document_metadata: dict[str, dict[str, str]] = {}

    for path in files:
        try:
            reader = PdfReader(str(path), strict=False)
            pages_total += len(reader.pages)
            metadata = _safe_metadata(reader)
            document_metadata[path.name] = metadata
            title = metadata.get("/Title", "").strip() or path.stem
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = normalize_text(page.extract_text() or "")
                except Exception as exc:  # noqa: BLE001 - one corrupt page must not stop the corpus
                    pages_skipped += 1
                    errors.append(f"{path.name}, página {page_number}: {type(exc).__name__}")
                    continue
                if len(text) < settings.min_page_chars:
                    pages_skipped += 1
                    continue
                pages_indexed += 1
                page_chunks = _split_page(text, settings.chunk_size, settings.chunk_overlap)
                for chunk_index, chunk_text in enumerate(page_chunks, start=1):
                    chunks.append(DocumentChunk(
                        chunk_id=stable_hash(path.name, str(page_number), str(chunk_index), chunk_text),
                        text=chunk_text,
                        source=path.name,
                        page=page_number,
                        chunk_index=chunk_index,
                        title=title,
                    ))
        except Exception as exc:  # noqa: BLE001 - isolate failures to the affected PDF
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")

    report = IngestionReport(
        pdf_files=len(files),
        pages_total=pages_total,
        pages_indexed=pages_indexed,
        pages_skipped=pages_skipped,
        chunks=len(chunks),
        errors=tuple(errors[:100]),
    )
    metadata_out = {
        "manifest": corpus_manifest(settings.docs_dir),
        "documents": document_metadata,
        "settings": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "min_page_chars": settings.min_page_chars,
        },
    }
    return chunks, report, metadata_out
