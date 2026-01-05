import fitz

def safe_optimize_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    doc.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True
    )
    doc.close()
