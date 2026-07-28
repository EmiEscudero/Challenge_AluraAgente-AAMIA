from __future__ import annotations

import unittest
from pathlib import Path

from eldercare_agent.ingestion import _is_summary_front_matter, _split_page


class IngestionTests(unittest.TestCase):
    def test_split_page_keeps_chunks_bounded(self) -> None:
        text = "\n\n".join(["Una recomendación clara para el cuidado diario. " * 20] * 6)
        chunks = _split_page(text, size=600, overlap=80)
        self.assertGreater(len(chunks), 3)
        self.assertTrue(all(40 <= len(chunk) <= 680 for chunk in chunks))

    def test_short_page_is_one_chunk(self) -> None:
        self.assertEqual(_split_page("Texto breve y suficiente.", 500, 50), ["Texto breve y suficiente."])

    def test_summary_front_matter_is_not_searchable(self) -> None:
        summary = Path("docs/resumenes/01_salud_integral.pdf")
        self.assertTrue(_is_summary_front_matter(summary, 1))
        self.assertTrue(_is_summary_front_matter(summary, 2))
        self.assertFalse(_is_summary_front_matter(summary, 3))
        self.assertFalse(_is_summary_front_matter(Path("docs/01_salud_integral.pdf"), 1))


if __name__ == "__main__":
    unittest.main()
