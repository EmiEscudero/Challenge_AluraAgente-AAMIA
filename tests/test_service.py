from __future__ import annotations

import tempfile
import unittest
from collections import Counter
from pathlib import Path

from eldercare_agent.config import Settings
from eldercare_agent.models import DocumentChunk, IngestionReport
from eldercare_agent.retriever import BM25Retriever
from eldercare_agent.service import ElderCareAgent
from eldercare_agent.text import tokenize


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.settings = Settings(
            root_dir=root,
            docs_dir=root / "docs",
            index_dir=root / "index",
            logs_dir=root / "logs",
            retrieval_threshold=0.1,
        )
        chunks = [
            DocumentChunk(
                "falls",
                "Para prevenir caídas conviene mantener buena iluminación y retirar obstáculos del paso.",
                "manual.pdf",
                12,
                1,
            )
        ]
        frequencies = Counter(tokenize(chunks[0].text))
        postings = {token: [[0, frequency]] for token, frequency in frequencies.items()}
        retriever = BM25Retriever(chunks, postings, [sum(frequencies.values())], IngestionReport(1, 1, 1, 0, 1))
        self.agent = ElderCareAgent(self.settings, retriever)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_grounded_answer_contains_citation(self) -> None:
        response = self.agent.ask("¿Cómo prevenir caídas?", session_id="test")
        self.assertTrue(response.sources)
        self.assertIn("[Fuente 1]", response.answer)
        self.assertTrue((self.settings.logs_dir / "agent-events.jsonl").exists())

    def test_out_of_scope_has_no_sources(self) -> None:
        response = self.agent.ask("¿Cuál es la capital de Francia?", session_id="test")
        self.assertFalse(response.sources)
        self.assertIn("fuera del alcance", response.answer)

    def test_emergency_notice(self) -> None:
        response = self.agent.ask("Está inconsciente y no respira", session_id="test")
        self.assertIsNotNone(response.emergency_notice)


if __name__ == "__main__":
    unittest.main()
