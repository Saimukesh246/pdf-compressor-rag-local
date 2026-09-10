import unittest
import os
import io
import fitz
import tempfile
from fastapi.testclient import TestClient

from api.index import app

class TestFastAPIBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.tmp_dir.name, "api_sample.pdf")
        
        # Create a sample PDF for API testing
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "FastAPI Serverless PDF Compressor API Test Document.")
        doc.save(self.sample_pdf)
        doc.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("ghostscript_available", data)

    def test_compress_endpoint(self):
        with open(self.sample_pdf, "rb") as f:
            response = self.client.post(
                "/api/compress",
                files={"file": ("api_sample.pdf", f, "application/pdf")},
                data={"level": "medium"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "api_sample.pdf")
        self.assertIn("metrics", data)
        self.assertIn("stats", data)
        self.assertIn("compressed_file_b64", data)

    def test_ask_endpoint(self):
        with open(self.sample_pdf, "rb") as f:
            response = self.client.post(
                "/api/ask",
                files={"file": ("api_sample.pdf", f, "application/pdf")},
                data={"query": "FastAPI Serverless"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "api_sample.pdf")
        self.assertGreater(data["matches_count"], 0)

if __name__ == "__main__":
    unittest.main()
