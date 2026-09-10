import unittest
import os
import fitz
import tempfile

from rag.pdf_rag import extract_pdf_chunks, build_pdf_index, query_pdf_content
from rag.retriever import retrieve
from rag.indexer import build_index

class TestRAGCapabilities(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.tmp_dir.name, "rag_sample.pdf")
        
        # Create a sample PDF with rich multi-page content for RAG testing
        doc = fitz.open()
        
        page1 = doc.new_page()
        page1.insert_text((50, 50), "Artificial Intelligence and Machine Learning are transforming PDF document compression workflows.")
        
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Ghostscript provides high-fidelity vector PDF rebuilding and image downsampling capabilities.")
        
        doc.save(self.sample_pdf)
        doc.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_pdf_chunk_extraction(self):
        chunks = extract_pdf_chunks(self.sample_pdf)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["page"], 1)
        self.assertIn("Artificial Intelligence", chunks[0]["text"])

    def test_pdf_indexing_and_query(self):
        index, chunks = build_pdf_index(self.sample_pdf)
        self.assertIsNotNone(index)
        self.assertEqual(len(chunks), 2)

        # Query for Machine Learning
        results = query_pdf_content((index, chunks), "Machine Learning", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["page"], 1)
        self.assertIn("Artificial Intelligence", results[0]["text"])
        self.assertIn("similarity", results[0])

        # Query for Ghostscript
        results_gs = query_pdf_content((index, chunks), "Ghostscript image downsampling", top_k=2)
        self.assertGreaterEqual(len(results_gs), 1)
        self.assertEqual(results_gs[0]["page"], 2)
        self.assertIn("Ghostscript", results_gs[0]["text"])

    def test_top_k_strategy_retriever(self):
        knowledge = [
            "Image-heavy PDF: Downscale images to 150 DPI.",
            "Text-heavy PDF: Optimize font streams and remove unused subsets.",
            "Scanned PDF: Apply OCR and compress extracted image masks."
        ]
        index, _ = build_index(knowledge)

        results = retrieve("OCR scanned document", index, knowledge, top_k=2, return_details=True)
        self.assertEqual(len(results), 2)
        self.assertIn("Scanned PDF", results[0]["text"])
        self.assertGreater(results[0]["similarity"], 0.0)

if __name__ == "__main__":
    unittest.main()
