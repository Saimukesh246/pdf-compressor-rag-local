import fitz  # PyMuPDF
import math

def add_watermark_to_pdf(
    input_path: str,
    output_path: str,
    text: str = "CONFIDENTIAL",
    opacity: float = 0.3,
    fontsize: int = 40,
    color: tuple = (0.5, 0.5, 0.5),
    rotation: int = 45,
    password: str = None
):
    """
    Applies a diagonal text watermark to every page of a PDF document.
    """
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if password and doc.authenticate(password):
            pass
        else:
            raise ValueError("Encrypted PDF requires a valid password.")

    for page in doc:
        rect = page.rect
        center_x = rect.width / 2.0
        center_y = rect.height / 2.0

        # Create shape for vector overlay
        shape = page.new_shape()
        
        # Calculate text point
        text_pt = fitz.Point(center_x - (len(text) * fontsize * 0.25), center_y)

        # Insert diagonal watermarking text
        shape.insert_text(
            text_pt,
            text,
            fontsize=fontsize,
            color=color,
            morph=(fitz.Point(center_x, center_y), fitz.Matrix(rotation))
        )
        
        shape.finish(fill_opacity=opacity, stroke_opacity=opacity)
        shape.commit()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return {
        "status": "success",
        "output_path": output_path,
        "watermark_text": text
    }
