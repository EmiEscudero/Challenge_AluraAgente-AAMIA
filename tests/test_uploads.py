from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from eldercare_agent.config import Settings
from eldercare_agent.uploads import (
    MAX_UPLOAD_BYTES,
    MAX_UPLOAD_FILES,
    UploadedPDF,
    UploadValidationError,
    build_session_corpus,
    validate_uploads,
)


class UploadValidationTests(unittest.TestCase):
    def test_rejects_too_many_files(self) -> None:
        files = [UploadedPDF(f"manual-{index}.pdf", b"%PDF-1.4") for index in range(MAX_UPLOAD_FILES + 1)]
        with self.assertRaisesRegex(UploadValidationError, "máximo"):
            validate_uploads(files)

    def test_rejects_oversized_file(self) -> None:
        with self.assertRaisesRegex(UploadValidationError, "límite"):
            validate_uploads([UploadedPDF("manual.pdf", b"%PDF-" + bytes(MAX_UPLOAD_BYTES))])

    def test_rejects_path_traversal_and_non_pdf_content(self) -> None:
        with self.assertRaisesRegex(UploadValidationError, "nombre no permitido"):
            validate_uploads([UploadedPDF("../manual.pdf", b"%PDF-1.4")])
        with self.assertRaisesRegex(UploadValidationError, "PDF válido"):
            validate_uploads([UploadedPDF("manual.pdf", b"contenido de texto")])


class SessionCorpusTests(unittest.TestCase):
    def test_builds_isolated_searchable_corpus_and_cleans_it(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = root / "docs" / "AAMIA_guia_abierta_para_el_cuidado.pdf"
        with tempfile.TemporaryDirectory() as base_directory:
            base = Path(base_directory)
            settings = Settings(
                root_dir=base,
                docs_dir=base / "docs",
                index_dir=base / "index",
                logs_dir=base / "logs",
                retrieval_threshold=0.1,
            )
            corpus = build_session_corpus([UploadedPDF(source.name, source.read_bytes())], settings)
            session_root = corpus.agent.settings.root_dir

            self.assertNotEqual(session_root, settings.root_dir)
            self.assertEqual(corpus.documents, (source.name,))
            self.assertGreater(corpus.agent.stats["pages"], 0)
            response = corpus.agent.ask("¿Cómo prevenir caídas en casa?", session_id="upload-test")
            self.assertTrue(response.sources)
            self.assertEqual(response.sources[0].chunk.source, source.name)

            corpus.close()
            self.assertFalse(session_root.exists())


if __name__ == "__main__":
    unittest.main()
