import unittest
import os
import fitz
import tempfile

from analyzer.pdf_analyzer import analyze_pdf
from decision.rule_engine import rule_based_strategy
from decision.hybrid_decider import decide_strategy
from rag.indexer import build_index
from compressor.pdf_optimizer import find_ghostscript, compress_pdf

class TestPDFCompressor(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.tmp_dir.name, "sample.pdf")
        self.output_pdf = os.path.join(self.tmp_dir.name, "compressed.pdf")
        
        # Create a simple PDF for testing
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Hello PDF Compressor World! This is a test document for unit testing.")
        doc.save(self.sample_pdf)
        doc.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_analyzer(self):
        metrics = analyze_pdf(self.sample_pdf)
        self.assertIn("file_size_kb", metrics)
        self.assertEqual(metrics["page_count"], 1)
        self.assertGreater(metrics["text_length"], 0)
        self.assertFalse(metrics["is_scanned"])

    def test_rule_engine(self):
        # Scanned PDF test
        strat, conf = rule_based_strategy(image_count=5, text_length=10, is_scanned=True)
        self.assertEqual(strat, "Scanned PDF")
        self.assertGreaterEqual(conf, 0.9)

        # Image-heavy PDF test
        strat, conf = rule_based_strategy(image_count=20, text_length=500)
        self.assertEqual(strat, "Image-heavy PDF")

        # Text-heavy PDF test
        strat, conf = rule_based_strategy(image_count=1, text_length=10000)
        self.assertEqual(strat, "Text-heavy PDF")

    def test_hybrid_decider(self):
        knowledge = [
            "Image-heavy PDF: Downscale images to 150 DPI.",
            "Text-heavy PDF: Optimize font streams and remove unused subsets."
        ]
        index, _ = build_index(knowledge)

        metrics = {
            "image_count": 0,
            "text_length": 10000,
            "is_scanned": False,
            "page_count": 1
        }
        strat, mode, details = decide_strategy(metrics, index, knowledge)
        self.assertEqual(mode, "RULE-BASED")
        self.assertEqual(strat, "Text-heavy PDF")
        self.assertIsNotNone(details)

    def test_ghostscript_detection(self):
        gs_path = find_ghostscript()
        self.assertIsNotNone(gs_path, "Ghostscript executable should be detected on the system.")

    def test_compress_pdf(self):
        gs_path = find_ghostscript()
        if gs_path:
            stats = compress_pdf(self.sample_pdf, self.output_pdf, level="medium")
            self.assertIn("original_size_kb", stats)
            self.assertIn("compressed_size_kb", stats)
            self.assertTrue(os.path.exists(self.output_pdf))

if __name__ == "__main__":
    unittest.main()
