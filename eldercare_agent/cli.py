from __future__ import annotations

import argparse
import json

from .config import Settings
from .service import ElderCareAgent


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta AAMIA desde la terminal.")
    parser.add_argument("question", nargs="?", help="Pregunta en lenguaje natural")
    parser.add_argument("--rebuild", action="store_true", help="Reconstruir el índice antes de consultar")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas de la biblioteca")
    args = parser.parse_args()

    agent, rebuilt = ElderCareAgent.create(Settings.from_env(), force_rebuild=args.rebuild)
    if args.stats:
        print(json.dumps({**agent.stats, "rebuilt": rebuilt}, ensure_ascii=False, indent=2))
        return 0
    if not args.question:
        parser.error("Indica una pregunta o utiliza --stats.")
    response = agent.ask(args.question, session_id="cli")
    print(response.answer)
    if response.sources:
        print("\nFuentes:")
        for result in response.sources:
            print(f"- [{result.rank}] {result.chunk.source}, página {result.chunk.page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
