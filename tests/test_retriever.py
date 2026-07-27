from __future__ import annotations

import unittest
from collections import Counter, defaultdict

from eldercare_agent.models import DocumentChunk, IngestionReport
from eldercare_agent.retriever import BM25Retriever
from eldercare_agent.text import tokenize


def make_retriever() -> BM25Retriever:
    chunks = [
        DocumentChunk("a", "La actividad física debe iniciar con calentamiento y movilidad progresiva.", "ejercicio.pdf", 10, 1),
        DocumentChunk("b", "Una dieta equilibrada incluye agua, fibra y alimentos variados.", "nutricion.pdf", 5, 1),
        DocumentChunk("c", "Para prevenir caídas se debe revisar la iluminación y retirar obstáculos.", "cuidados.pdf", 8, 1),
    ]
    postings: dict[str, list[list[int]]] = defaultdict(list)
    lengths = []
    for doc_id, chunk in enumerate(chunks):
        frequencies = Counter(tokenize(chunk.text))
        lengths.append(sum(frequencies.values()))
        for token, frequency in frequencies.items():
            postings[token].append([doc_id, frequency])
    report = IngestionReport(3, 3, 3, 0, 3)
    return BM25Retriever(chunks, dict(postings), lengths, report)


class RetrieverTests(unittest.TestCase):
    def test_finds_expanded_exercise_query(self) -> None:
        results = make_retriever().search("¿Cómo iniciar una rutina de ejercicio?", top_k=2)
        self.assertEqual(results[0].chunk.source, "ejercicio.pdf")
        self.assertGreater(results[0].score, 0)

    def test_returns_empty_for_unrelated_query(self) -> None:
        results = make_retriever().search("capital francia océano atlántico")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
