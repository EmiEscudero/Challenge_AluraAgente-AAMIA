from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eldercare_agent.config import Settings
from eldercare_agent.service import ElderCareAgent

QUESTIONS = (
    "¿Cómo puedo prevenir caídas en casa?",
    "¿Qué recomendaciones hay sobre alimentación del adulto mayor?",
    "¿Cómo debe organizarse una sesión de actividad física?",
    "¿Qué actividades ayudan a estimular la memoria?",
    "¿Cuál es la capital de Francia?",
)


def main() -> int:
    settings = Settings.from_env(ROOT)
    agent, rebuilt = ElderCareAgent.create(settings)
    results = []
    for question in QUESTIONS:
        response = agent.ask(question, session_id="smoke-test")
        results.append({
            "question": question,
            "answer": response.answer,
            "provider": response.provider,
            "confidence": response.confidence,
            "sources": [
                {"document": item.chunk.source, "page": item.chunk.page, "score": item.score}
                for item in response.sources
            ],
        })
    print(json.dumps({"rebuilt": rebuilt, "stats": agent.stats, "results": results}, ensure_ascii=False, indent=2))
    return 0 if agent.stats["documents"] > 0 and agent.stats["chunks"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
