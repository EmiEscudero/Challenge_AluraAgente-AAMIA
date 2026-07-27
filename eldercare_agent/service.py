from __future__ import annotations

import time
import uuid

from .audit import write_audit_event
from .config import Settings
from .llm import ExtractiveGenerator, make_generator
from .models import AgentResponse, SearchResult
from .retriever import BM25Retriever
from .safety import emergency_notice, is_domain_query


class ElderCareAgent:
    def __init__(self, settings: Settings, retriever: BM25Retriever) -> None:
        self.settings = settings
        self.retriever = retriever
        self.generator = make_generator(settings)
        self.extractive_fallback = ExtractiveGenerator()

    @classmethod
    def create(cls, settings: Settings | None = None, force_rebuild: bool = False) -> tuple[ElderCareAgent, bool]:
        active_settings = settings or Settings.from_env()
        errors = active_settings.validate()
        if errors:
            raise ValueError(" ".join(errors))
        retriever, rebuilt = BM25Retriever.load_or_build(active_settings, force=force_rebuild)
        return cls(active_settings, retriever), rebuilt

    @property
    def stats(self) -> dict[str, int]:
        report = self.retriever.report
        return {
            "documents": report.pdf_files,
            "pages": report.pages_indexed,
            "chunks": report.chunks,
            "skipped_pages": report.pages_skipped,
            "errors": len(report.errors),
        }

    def ask(self, question: str, session_id: str | None = None) -> AgentResponse:
        clean_question = question.strip()[:2_000]
        if len(clean_question) < 3:
            return AgentResponse(answer="Escribe una pregunta un poco más específica.", confidence="baja")

        started = time.perf_counter()
        notice = emergency_notice(clean_question)
        if not is_domain_query(clean_question):
            answer = (
                "La pregunta parece estar fuera del alcance de esta biblioteca, que se concentra en "
                "cuidados, alimentación, actividad física y bienestar de personas adultas mayores."
            )
            return self._finish(
                question=clean_question,
                answer=answer,
                sources=[],
                provider="none",
                started=started,
                confidence="baja",
                notice=notice,
                session_id=session_id,
            )
        sources = self.retriever.search(
            clean_question,
            top_k=self.settings.top_k,
            candidate_k=self.settings.candidate_k,
        )
        if not sources or sources[0].score < self.settings.retrieval_threshold:
            answer = (
                "No encontré información suficiente en los documentos disponibles para responder "
                "con seguridad. Intenta reformular la pregunta o consulta a un profesional de salud."
            )
            return self._finish(
                question=clean_question,
                answer=answer,
                sources=[],
                provider="none",
                started=started,
                confidence="baja",
                notice=notice,
                session_id=session_id,
            )

        provider = self.generator.name
        fallback_used = False
        error: str | None = None
        try:
            answer = self.generator.generate(clean_question, sources)
        except Exception as exc:  # noqa: BLE001 - every provider failure uses the safe local fallback
            error = f"{type(exc).__name__}: {exc}"
            answer = self.extractive_fallback.generate(clean_question, sources)
            provider = "extractive"
            fallback_used = True

        top_score = sources[0].score
        confidence = "alta" if top_score >= 8 else "media" if top_score >= 3 else "baja"
        return self._finish(
            question=clean_question,
            answer=answer,
            sources=sources,
            provider=provider,
            started=started,
            confidence=confidence,
            notice=notice,
            session_id=session_id,
            fallback_used=fallback_used,
            error=error,
        )

    def _finish(
        self,
        *,
        question: str,
        answer: str,
        sources: list[SearchResult],
        provider: str,
        started: float,
        confidence: str,
        notice: str | None,
        session_id: str | None,
        fallback_used: bool = False,
        error: str | None = None,
    ) -> AgentResponse:
        latency_ms = round((time.perf_counter() - started) * 1_000)
        response = AgentResponse(
            answer=answer,
            sources=sources,
            provider=provider,
            latency_ms=latency_ms,
            confidence=confidence,
            emergency_notice=notice,
            fallback_used=fallback_used,
            error=error,
        )
        source_events = [
            {
                "document": result.chunk.source,
                "page": result.chunk.page,
                "score": result.score,
                "chunk_id": result.chunk.chunk_id,
            }
            for result in sources
        ]
        write_audit_event(
            self.settings.logs_dir,
            session_id=session_id or str(uuid.uuid4()),
            question=question,
            answer=answer,
            sources=source_events,
            provider=provider,
            latency_ms=latency_ms,
            confidence=confidence,
            log_content=self.settings.log_content,
            error=error,
        )
        return response
