import fitz  # PyMuPDF
from PIL import Image
import io


def compress_images_in_pdf(
    input_pdf: str,
    output_pdf: str,
    image_quality: int = 40,
    scale: float = 0.6
):
    """
    Safely compress images inside a PDF without black image issues.
    """

    doc = fitz.open(input_pdf)

    for page in doc:
        image_list = page.get_images(full=True)

        for img in image_list:
            xref = img[0]

            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            img_pil = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB safely
            if img_pil.mode not in ("RGB", "L"):
                img_pil = img_pil.convert("RGB")

            # Resize
            new_size = (
                int(img_pil.width * scale),
                int(img_pil.height * scale)
            )
            img_pil = img_pil.resize(new_size, Image.LANCZOS)

            # Save to JPEG
            buffer = io.BytesIO()
            img_pil.save(
                buffer,
                format="JPEG",
                quality=image_quality,
                optimize=True
            )

            # 🔥 SAFE replacement (updates metadata)
            page.replace_image(xref, stream=buffer.getvalue())

    doc.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True
    )
    doc.close()
