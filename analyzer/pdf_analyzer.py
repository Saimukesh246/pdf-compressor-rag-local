import fitz

def analyze_pdf(path):
    doc = fitz.open(path)

    image_count = 0
    text_length = 0

    for page in doc:
        image_count += len(page.get_images())
        text_length += len(page.get_text())

    doc.close()

    return {
        "image_count": image_count,
        "text_length": text_length
    }
