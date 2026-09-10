import unittest
import os
import fitz
import tempfile

from compressor.pdf_manipulator import merge_pdfs, split_pdf
from rag.llm_synthesizer import generate_pdf_mindmap
from compressor.pdf_optimizer import find_ghostscript, compress_pdf

class TestPDFManipulator(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pdf1 = os.path.join(self.tmp_dir.name, "doc1.pdf")
        self.pdf2 = os.path.join(self.tmp_dir.name, "doc2.pdf")
        self.merged_pdf = os.path.join(self.tmp_dir.name, "merged_out.pdf")

        # Doc 1: 2 pages
        d1 = fitz.open()
        p1 = d1.new_page()
        p1.insert_text((50, 50), "Document 1 Page 1 Text.")
        p2 = d1.new_page()
        p2.insert_text((50, 50), "Document 1 Page 2 Text.")
        d1.save(self.pdf1)
        d1.close()

        # Doc 2: 1 page
        d2 = fitz.open()
        p3 = d2.new_page()
        p3.insert_text((50, 50), "Document 2 Page 1 Text.")
        d2.save(self.pdf2)
        d2.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_merge_pdfs(self):
        res = merge_pdfs([self.pdf1, self.pdf2], self.merged_pdf)
        self.assertEqual(res["total_pages"], 3)
        self.assertTrue(os.path.exists(self.merged_pdf))

    def test_split_pdf(self):
        res = split_pdf(self.pdf1, self.tmp_dir.name, range_str="1-1")
        self.assertEqual(res["extracted_pages"], 1)
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_generate_pdf_mindmap(self):
        res = generate_pdf_mindmap(self.pdf1)
        self.assertIn("summary_text", res)
        self.assertIn("mermaid_code", res)
        self.assertIn("mindmap", res["mermaid_code"])

    def test_grayscale_compression(self):
        gs_path = find_ghostscript()
        if gs_path:
            out_mono = os.path.join(self.tmp_dir.name, "mono.pdf")
            stats = compress_pdf(self.pdf1, out_mono, level="medium", grayscale=True)
            self.assertTrue(os.path.exists(out_mono))
            self.assertIn("original_size_kb", stats)

if __name__ == "__main__":
    unittest.main()
