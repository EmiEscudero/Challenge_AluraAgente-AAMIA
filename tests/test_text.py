from __future__ import annotations

import unittest

from eldercare_agent.text import normalize_text, strip_accents, tokenize


class TextTests(unittest.TestCase):
    def test_strip_accents(self) -> None:
        self.assertEqual(strip_accents("Alimentación y caída"), "Alimentacion y caida")

    def test_query_expansion(self) -> None:
        tokens = tokenize("¿Qué ejercicio puede hacer?", expand=True)
        self.assertIn("actividad", tokens)
        self.assertIn("movilidad", tokens)

    def test_normalizes_pdf_line_break_hyphen(self) -> None:
        self.assertEqual(normalize_text("ali-\n mentación"), "alimentación")


if __name__ == "__main__":
    unittest.main()
