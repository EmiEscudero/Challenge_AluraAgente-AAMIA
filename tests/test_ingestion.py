from __future__ import annotations

import unittest

from eldercare_agent.ingestion import _split_page


class IngestionTests(unittest.TestCase):
    def test_split_page_keeps_chunks_bounded(self) -> None:
        text = "\n\n".join(["Una recomendación clara para el cuidado diario. " * 20] * 6)
        chunks = _split_page(text, size=600, overlap=80)
        self.assertGreater(len(chunks), 3)
        self.assertTrue(all(40 <= len(chunk) <= 680 for chunk in chunks))

    def test_short_page_is_one_chunk(self) -> None:
        self.assertEqual(_split_page("Texto breve y suficiente.", 500, 50), ["Texto breve y suficiente."])


if __name__ == "__main__":
    unittest.main()
