import os
import fitz
from PIL import Image
import io

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

def extract_pdf_ocr_text(pdf_path, max_pages=5):
    """
    Extracts text from a PDF file, falling back to Tesseract OCR for scanned/image pages if available.
    
    Args:
        pdf_path (str): Path to the PDF file
        max_pages (int): Maximum pages to inspect for OCR extraction
        
    Returns:
        dict: Containing 'text', 'is_scanned', and 'pages_processed'.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_to_process = min(total_pages, max_pages)

    extracted_text_blocks = []
    scanned_page_count = 0

    for page_num in range(pages_to_process):
        page = doc[page_num]
        standard_text = page.get_text().strip()

        if standard_text:
            extracted_text_blocks.append(f"--- Page {page_num+1} ---\n{standard_text}")
        else:
            # Page has no standard text layer; check if it has images
            images = page.get_images()
            if len(images) > 0:
                scanned_page_count += 1
                if HAS_PYTESSERACT:
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img).strip()
                        if ocr_text:
                            extracted_text_blocks.append(f"--- Page {page_num+1} (OCR) ---\n{ocr_text}")
                    except Exception:
                        pass

    doc.close()

    full_text = "\n\n".join(extracted_text_blocks)
    is_scanned = scanned_page_count > 0 or len(full_text.strip()) == 0

    return {
        "text": full_text,
        "is_scanned": is_scanned,
        "pages_processed": pages_to_process,
        "scanned_pages": scanned_page_count
    }
