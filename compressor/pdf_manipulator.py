import os
import fitz

def merge_pdfs(input_pdf_paths, output_pdf_path):
    """
    Merges multiple PDF files into a single output PDF.
    
    Args:
        input_pdf_paths (list of str): List of input PDF file paths
        output_pdf_path (str): Destination PDF file path
        
    Returns:
        dict: Summary containing total pages and output size (KB).
    """
    if not input_pdf_paths:
        raise ValueError("No input PDF files provided for merging.")

    merged_doc = fitz.open()

    for pdf_path in input_pdf_paths:
        if not os.path.exists(pdf_path):
            continue
        doc = fitz.open(pdf_path)
        merged_doc.insert_pdf(doc)
        doc.close()

    if len(merged_doc) == 0:
        merged_doc.close()
        raise ValueError("All input PDF files were empty or invalid.")

    merged_doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
    total_pages = len(merged_doc)
    merged_doc.close()

    output_size_kb = os.path.getsize(output_pdf_path) / 1024.0

    return {
        "output_path": output_pdf_path,
        "total_pages": total_pages,
        "file_size_kb": round(output_size_kb, 2)
    }


def parse_page_range(range_str, total_pages):
    """
    Parses a page range string (e.g. '1-3, 5, 7-10') into a list of 0-based page indices.
    """
    pages = set()
    parts = [p.strip() for p in range_str.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            try:
                start, end = part.split("-")
                s = max(1, int(start))
                e = min(total_pages, int(end))
                for p in range(s, e + 1):
                    pages.add(p - 1)
            except Exception:
                pass
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p - 1)
            except Exception:
                pass

    return sorted(list(pages))


def split_pdf(input_pdf_path, output_dir, range_str="1-1"):
    """
    Extracts a subset of pages from a PDF file into a new output PDF.
    
    Args:
        input_pdf_path (str): Source PDF file path
        output_dir (str): Directory to save split PDF
        range_str (str): Page selection string (e.g., '1-3', '2, 5', '1-5')
        
    Returns:
        dict: Output file details and total pages extracted.
    """
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"Input file not found: {input_pdf_path}")

    doc = fitz.open(input_pdf_path)
    total_pages = len(doc)

    selected_indices = parse_page_range(range_str, total_pages)
    if not selected_indices:
        selected_indices = list(range(total_pages))

    output_filename = f"split_{os.path.basename(input_pdf_path)}"
    output_path = os.path.join(output_dir, output_filename)

    split_doc = fitz.open()
    for idx in selected_indices:
        split_doc.insert_pdf(doc, from_page=idx, to_page=idx)

    doc.close()
    split_doc.save(output_path, garbage=4, deflate=True, clean=True)
    extracted_count = len(split_doc)
    split_doc.close()

    output_size_kb = os.path.getsize(output_path) / 1024.0

    return {
        "output_path": output_path,
        "extracted_pages": extracted_count,
        "file_size_kb": round(output_size_kb, 2)
    }
