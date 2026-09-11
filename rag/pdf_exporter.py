import fitz  # PyMuPDF

def export_pdf_to_markdown(input_path: str, password: str = None) -> dict:
    """
    Extracts text, page titles, and structure from a PDF document into a clean Markdown string.
    """
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if password and doc.authenticate(password):
            pass
        else:
            raise ValueError("Encrypted PDF requires a valid password.")

    markdown_lines = []
    markdown_lines.append(f"# 📄 PDF Document Export: {doc.name if hasattr(doc, 'name') else 'Document'}\n")
    markdown_lines.append(f"**Total Pages:** {len(doc)}  \n---\n")

    pages_data = []

    for idx, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        markdown_lines.append(f"## Page {idx}\n")
        if text:
            markdown_lines.append(text + "\n")
        else:
            markdown_lines.append("*[No text layer found on this page. Document may be a scanned image.]*\n")
        
        markdown_lines.append("\n---\n")
        pages_data.append({
            "page": idx,
            "text": text
        })

    doc.close()
    full_markdown = "\n".join(markdown_lines)

    return {
        "status": "success",
        "markdown_text": full_markdown,
        "page_count": len(pages_data),
        "pages": pages_data
    }
