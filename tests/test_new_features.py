import unittest
import os
import fitz
import tempfile
from fastapi.testclient import TestClient

from api.index import app
from compressor.pdf_watermark import add_watermark_to_pdf
from compressor.pdf_security import encrypt_pdf, decrypt_pdf
from compressor.pdf_converter import pdf_to_images_zip, images_to_pdf
from analyzer.pii_redactor import redact_pii_from_pdf
from rag.pdf_exporter import export_pdf_to_markdown

class TestEnterpriseFeatures(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.tmp_dir.name, "enterprise_sample.pdf")
        self.watermarked_pdf = os.path.join(self.tmp_dir.name, "watermarked.pdf")
        self.encrypted_pdf = os.path.join(self.tmp_dir.name, "encrypted.pdf")
        self.decrypted_pdf = os.path.join(self.tmp_dir.name, "decrypted.pdf")
        self.redacted_pdf = os.path.join(self.tmp_dir.name, "redacted.pdf")
        self.img_pdf = os.path.join(self.tmp_dir.name, "img_pdf.pdf")
        
        # Create a sample PDF with text and PII data
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Enterprise Security Document.")
        page.insert_text((50, 100), "Contact email: admin@enterprise.com")
        page.insert_text((50, 150), "Phone: (555) 123-4567")
        doc.save(self.sample_pdf)
        doc.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_watermark(self):
        res = add_watermark_to_pdf(self.sample_pdf, self.watermarked_pdf, text="CONFIDENTIAL")
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(self.watermarked_pdf))

    def test_encrypt_decrypt(self):
        # Encrypt
        enc_res = encrypt_pdf(self.sample_pdf, self.encrypted_pdf, user_password="pass123")
        self.assertEqual(enc_res["status"], "encrypted")
        
        # Verify encryption
        doc = fitz.open(self.encrypted_pdf)
        self.assertTrue(doc.is_encrypted)
        doc.close()

        # Decrypt
        dec_res = decrypt_pdf(self.encrypted_pdf, self.decrypted_pdf, password="pass123")
        self.assertEqual(dec_res["status"], "decrypted")

    def test_pdf_converter(self):
        zip_bytes = pdf_to_images_zip(self.sample_pdf, dpi=72)
        self.assertGreater(len(zip_bytes), 0)

        # Convert back
        images_to_pdf([zip_bytes], self.img_pdf)
        self.assertTrue(os.path.exists(self.img_pdf))

    def test_pii_redaction(self):
        red_res = redact_pii_from_pdf(self.sample_pdf, self.redacted_pdf, redact_email=True, redact_phone=True)
        self.assertGreater(red_res["total_redactions"], 0)

    def test_export_markdown(self):
        exp_res = export_pdf_to_markdown(self.sample_pdf)
        self.assertEqual(exp_res["status"], "success")
        self.assertIn("Enterprise Security Document", exp_res["markdown_text"])

    def test_watermark_api_endpoint(self):
        with open(self.sample_pdf, "rb") as f:
            response = self.client.post(
                "/api/watermark",
                files={"file": ("sample.pdf", f, "application/pdf")},
                data={"text": "DRAFT"}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("file_b64", data)

    def test_export_markdown_api_endpoint(self):
        with open(self.sample_pdf, "rb") as f:
            response = self.client.post(
                "/api/export-markdown",
                files={"file": ("sample.pdf", f, "application/pdf")}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("markdown_text", data)

if __name__ == "__main__":
    unittest.main()
