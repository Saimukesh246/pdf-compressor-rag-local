import os
import fitz

def analyze_pdf(path):
    """
    Analyzes a PDF file to extract structural and content metrics.
    
    Returns:
        dict: Summary metrics including page count, file size, image count, text length,
              scanned status, and average content density.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found: {path}")

    file_size_kb = os.path.getsize(path) / 1024.0
    doc = fitz.open(path)
    page_count = len(doc)

    image_count = 0
    text_length = 0

    for page in doc:
        image_count += len(page.get_images())
        text_length += len(page.get_text())

    doc.close()

    is_scanned = (image_count > 0 and text_length < 50) or (text_length == 0 and page_count > 0)
    avg_images_per_page = image_count / page_count if page_count > 0 else 0
    avg_text_per_page = text_length / page_count if page_count > 0 else 0

    return {
        "file_size_kb": file_size_kb,
        "page_count": page_count,
        "image_count": image_count,
        "text_length": text_length,
        "is_scanned": is_scanned,
        "avg_images_per_page": avg_images_per_page,
        "avg_text_per_page": avg_text_per_page
    }
