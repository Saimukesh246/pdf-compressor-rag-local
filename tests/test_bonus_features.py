import unittest
import os
import fitz
import tempfile

from rag.llm_synthesizer import synthesize_rag_answer
from analyzer.pdf_analyzer import analyze_pdf
from compressor.pdf_optimizer import safe_optimize_pdf, compress_pdf

class TestBonusFeatures(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.tmp_dir.name, "bonus_sample.pdf")
        self.encrypted_pdf = os.path.join(self.tmp_dir.name, "encrypted_sample.pdf")
        self.output_pdf = os.path.join(self.tmp_dir.name, "bonus_output.pdf")
        
        # Create standard test PDF with metadata
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Testing Bonus Features for PDF Compressor.")
        doc.set_metadata({"title": "Test Title", "author": "Test Author"})
        doc.save(self.sample_pdf)
        doc.close()

        # Create encrypted PDF with password
        doc_enc = fitz.open()
        page_enc = doc_enc.new_page()
        page_enc.insert_text((50, 50), "Secret encrypted content.")
        doc_enc.save(self.encrypted_pdf, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="secret123", user_pw="secret123")
        doc_enc.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_llm_synthesizer_structured_fallback(self):
        passages = [
            {"page": 1, "text": "Ghostscript downsamples vector graphics.", "similarity": 0.85},
            {"page": 2, "text": "FAISS vector RAG retrieves page chunks.", "similarity": 0.72}
        ]
        synthesis = synthesize_rag_answer("How does compression work?", passages)
        self.assertIn("Page 1", synthesis)
        self.assertIn("Ghostscript", synthesis)

    def test_encrypted_pdf_handling(self):
        # Without password -> should raise error
        with self.assertRaises(ValueError):
            analyze_pdf(self.encrypted_pdf)

        # With correct password -> should succeed
        metrics = analyze_pdf(self.encrypted_pdf, password="secret123")
        self.assertEqual(metrics["page_count"], 1)

    def test_metadata_stripping(self):
        safe_optimize_pdf(self.sample_pdf, self.output_pdf, strip_metadata=True)
        doc = fitz.open(self.output_pdf)
        meta = doc.metadata
        self.assertEqual(meta.get("author", ""), "")
        doc.close()

if __name__ == "__main__":
    unittest.main()
