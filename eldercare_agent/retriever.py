from __future__ import annotations

import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .config import Settings
from .ingestion import corpus_manifest, ingest_pdfs
from .models import DocumentChunk, IngestionReport, SearchResult
from .text import strip_accents, tokenize

INDEX_VERSION = 3


class BM25Retriever:
    """Compact BM25 index with query expansion and diversity reranking."""

    def __init__(
        self,
        chunks: list[DocumentChunk],
        postings: dict[str, list[list[int]]],
        doc_lengths: list[int],
        report: IngestionReport,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.chunks = chunks
        self.postings = postings
        self.doc_lengths = doc_lengths
        self.report = report
        self.metadata = metadata or {}
        self.avg_doc_length = sum(doc_lengths) / max(1, len(doc_lengths))
        self._token_cache: dict[int, set[str]] = {}

    @classmethod
    def build(cls, settings: Settings) -> BM25Retriever:
        chunks, report, metadata = ingest_pdfs(settings)
        raw_postings: dict[str, list[list[int]]] = defaultdict(list)
        doc_lengths: list[int] = []

        for doc_id, chunk in enumerate(chunks):
            frequencies = Counter(tokenize(chunk.text))
            doc_lengths.append(sum(frequencies.values()))
            for term, frequency in frequencies.items():
                raw_postings[term].append([doc_id, frequency])

        return cls(
            chunks=chunks,
            postings=dict(raw_postings),
            doc_lengths=doc_lengths,
            report=report,
            metadata=metadata,
        )

    @property
    def index_file(self) -> str:
        return "bm25-index.json.gz"

    def save(self, index_dir: Path) -> Path:
        index_dir.mkdir(parents=True, exist_ok=True)
        target = index_dir / self.index_file
        temp = index_dir / f"{self.index_file}.tmp"
        payload = {
            "version": INDEX_VERSION,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "postings": self.postings,
            "doc_lengths": self.doc_lengths,
            "report": self.report.to_dict(),
            "metadata": self.metadata,
        }
        with gzip.open(temp, "wt", encoding="utf-8", compresslevel=5) as stream:
            json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
        temp.replace(target)
        return target

    @classmethod
    def load(cls, index_dir: Path) -> BM25Retriever:
        target = index_dir / "bm25-index.json.gz"
        with gzip.open(target, "rt", encoding="utf-8") as stream:
            payload = json.load(stream)
        if payload.get("version") != INDEX_VERSION:
            raise ValueError("Versión de índice incompatible")
        report_data = payload["report"]
        report = IngestionReport(
            pdf_files=report_data["pdf_files"],
            pages_total=report_data["pages_total"],
            pages_indexed=report_data["pages_indexed"],
            pages_skipped=report_data["pages_skipped"],
            chunks=report_data["chunks"],
            errors=tuple(report_data.get("errors", [])),
        )
        return cls(
            chunks=[DocumentChunk.from_dict(item) for item in payload["chunks"]],
            postings=payload["postings"],
            doc_lengths=payload["doc_lengths"],
            report=report,
            metadata=payload.get("metadata", {}),
        )

    def is_current(self, settings: Settings) -> bool:
        saved = self.metadata.get("manifest", {}).get("fingerprint")
        current = corpus_manifest(settings.docs_dir).get("fingerprint")
        saved_settings = self.metadata.get("settings", {})
        return bool(saved and saved == current) and saved_settings == {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "min_page_chars": settings.min_page_chars,
        }

    @classmethod
    def load_or_build(cls, settings: Settings, force: bool = False) -> tuple[BM25Retriever, bool]:
        target = settings.index_dir / "bm25-index.json.gz"
        if target.exists() and not force:
            try:
                retriever = cls.load(settings.index_dir)
                if retriever.is_current(settings):
                    return retriever, False
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                pass
        retriever = cls.build(settings)
        retriever.save(settings.index_dir)
        return retriever, True

    def _bm25_scores(self, query: str) -> dict[int, float]:
        query_terms = Counter(tokenize(query, expand=True))
        scores: dict[int, float] = defaultdict(float)
        total_docs = max(1, len(self.chunks))
        k1 = 1.35
        b = 0.72

        for term, query_frequency in query_terms.items():
            entries = self.postings.get(term)
            if not entries:
                continue
            doc_frequency = len(entries)
            inverse_doc_frequency = math.log(1 + (total_docs - doc_frequency + 0.5) / (doc_frequency + 0.5))
            query_weight = 1.0 + math.log1p(query_frequency)
            for doc_id, term_frequency in entries:
                length_norm = 1 - b + b * self.doc_lengths[doc_id] / max(1.0, self.avg_doc_length)
                term_score = inverse_doc_frequency * (
                    term_frequency * (k1 + 1) / (term_frequency + k1 * length_norm)
                )
                scores[doc_id] += term_score * query_weight

        normalized_query = strip_accents(query.lower())
        for doc_id in list(scores):
            chunk = self.chunks[doc_id]
            source = strip_accents(f"{chunk.source} {chunk.title}".lower())
            for term in set(tokenize(normalized_query)):
                if term in source:
                    scores[doc_id] += 0.35
            chunk_text = strip_accents(chunk.text.lower())
            if chunk.page <= 3:
                scores[doc_id] *= 0.65
            looks_like_contents = (
                chunk.page <= 10
                and (chunk_text.count("capitulo") >= 2 or "tabla de contenido" in chunk_text or "indice" in chunk_text)
            )
            if looks_like_contents:
                scores[doc_id] *= 0.45
        return scores

    def _chunk_tokens(self, doc_id: int) -> set[str]:
        if doc_id not in self._token_cache:
            self._token_cache[doc_id] = set(tokenize(self.chunks[doc_id].text))
        return self._token_cache[doc_id]

    def search(self, query: str, top_k: int = 5, candidate_k: int = 24) -> list[SearchResult]:
        if not query.strip() or not self.chunks:
            return []
        scores = self._bm25_scores(query)
        candidates = sorted(scores, key=scores.get, reverse=True)[:candidate_k]
        if not candidates:
            return []

        selected: list[int] = []
        source_counts: Counter[str] = Counter()
        while candidates and len(selected) < top_k:
            best_doc = candidates[0]
            best_adjusted = float("-inf")
            for doc_id in candidates:
                chunk = self.chunks[doc_id]
                redundancy = 0.0
                current_tokens = self._chunk_tokens(doc_id)
                for chosen in selected:
                    chosen_tokens = self._chunk_tokens(chosen)
                    union = len(current_tokens | chosen_tokens)
                    similarity = len(current_tokens & chosen_tokens) / union if union else 0.0
                    redundancy = max(redundancy, similarity)
                source_penalty = 0.55 * source_counts[chunk.source]
                adjusted = scores[doc_id] - (1.8 * redundancy) - source_penalty
                if adjusted > best_adjusted:
                    best_adjusted = adjusted
                    best_doc = doc_id
            candidates.remove(best_doc)
            selected.append(best_doc)
            source_counts[self.chunks[best_doc].source] += 1

        return [
            SearchResult(chunk=self.chunks[doc_id], score=round(scores[doc_id], 4), rank=rank)
            for rank, doc_id in enumerate(selected, start=1)
        ]
