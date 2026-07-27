from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def write_audit_event(
    logs_dir: Path,
    *,
    session_id: str,
    question: str,
    answer: str,
    sources: list[dict[str, Any]],
    provider: str,
    latency_ms: int,
    confidence: str,
    log_content: bool,
    error: str | None = None,
) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    event: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_hash": _digest(session_id),
        "question_hash": _digest(question),
        "question_chars": len(question),
        "answer_chars": len(answer),
        "provider": provider,
        "latency_ms": latency_ms,
        "confidence": confidence,
        "sources": sources,
        "error": error,
    }
    if log_content:
        event["question"] = question
        event["answer"] = answer
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    target = logs_dir / "agent-events.jsonl"
    with _LOCK, target.open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")


def write_feedback(logs_dir: Path, session_id: str, message_id: str, value: str) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "feedback",
        "session_hash": _digest(session_id),
        "message_id": message_id,
        "value": value,
    }
    with _LOCK, (logs_dir / "feedback.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
