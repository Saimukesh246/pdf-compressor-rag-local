import fitz  # PyMuPDF
import io
import os
import zipfile
from PIL import Image

def pdf_to_images_zip(input_path: str, dpi: int = 150, password: str = None) -> bytes:
    """
    Converts all pages of a PDF document to PNG images and returns a ZIP archive as bytes.
    """
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if password and doc.authenticate(password):
            pass
        else:
            raise ValueError("Encrypted PDF requires a valid password.")

    zip_buffer = io.BytesIO()
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")
            zip_file.writestr(f"page_{idx}.png", img_bytes)

    doc.close()
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def images_to_pdf(image_bytes_list: list, output_path: str):
    """
    Combines a list of image byte buffers or file paths into a single PDF document.
    """
    doc = fitz.open()

    for item in image_bytes_list:
        if isinstance(item, str) and os.path.exists(item):
            img_doc = fitz.open(item)
        elif isinstance(item, (bytes, bytearray)):
            img_doc = fitz.open(stream=item, filetype="png")
        else:
            continue

        rect = img_doc[0].rect
        pdfbytes = img_doc.convert_to_pdf()
        img_doc.close()

        img_pdf = fitz.open("pdf", pdfbytes)
        page = doc.new_page(width=rect.width, height=rect.height)
        page.show_pdf_page(rect, img_pdf, 0)
        img_pdf.close()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return {
        "status": "success",
        "output_path": output_path
    }
