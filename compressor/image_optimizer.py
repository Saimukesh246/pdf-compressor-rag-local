import fitz
from PIL import Image
import io

def compress_images_in_pdf(input_pdf, output_pdf, image_quality=40, scale=0.6):
    doc = fitz.open(input_pdf)

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            img_pil = Image.open(io.BytesIO(image_bytes))

            # Resize image
            new_size = (
                int(img_pil.width * scale),
                int(img_pil.height * scale)
            )
            img_pil = img_pil.resize(new_size, Image.LANCZOS)

            # Recompress image
            buffer = io.BytesIO()
            img_pil.convert("RGB").save(
                buffer,
                format="JPEG",
                quality=image_quality,
                optimize=True
            )

            doc.update_stream(xref, buffer.getvalue())

    doc.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True
    )
    doc.close()
