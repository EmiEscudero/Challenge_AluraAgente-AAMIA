from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eldercare_agent.config import Settings
from eldercare_agent.retriever import BM25Retriever


def main() -> int:
    settings = Settings.from_env(ROOT)
    retriever = BM25Retriever.build(settings)
    target = retriever.save(settings.index_dir)
    print(json.dumps({
        "index": str(target),
        "report": retriever.report.to_dict(),
    }, ensure_ascii=False, indent=2))
    return 1 if not retriever.chunks else 0


if __name__ == "__main__":
    raise SystemExit(main())
