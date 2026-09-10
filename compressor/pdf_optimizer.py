import os
import shutil
import subprocess
import fitz
import numpy as np
from PIL import Image
import io

GS_LEVEL_MAP = {
    "low": "printer",
    "medium": "ebook",
    "high": "screen",
    "printer": "printer",
    "ebook": "ebook",
    "screen": "screen"
}

def find_ghostscript():
    """
    Locates the Ghostscript executable on Windows, Linux, or macOS.
    
    Returns:
        str or None: Path to Ghostscript executable if found, else None.
    """
    for exe in ["gswin64c.exe", "gswin32c.exe", "gs.exe", "gs"]:
        path = shutil.which(exe)
        if path:
            return path

    common_dirs = [
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs",
        "/usr/bin",
        "/usr/local/bin",
        "/opt/homebrew/bin"
    ]

    for base in common_dirs:
        if os.path.exists(base):
            if os.path.isfile(base) and os.access(base, os.X_OK):
                return base
            for root, dirs, files in os.walk(base):
                for file in files:
                    if file.lower() in ["gswin64c.exe", "gswin32c.exe", "gs.exe", "gs"]:
                        return os.path.join(root, file)

    return None


def safe_optimize_pdf(input_pdf, output_pdf, password=None, strip_metadata=False):
    """
    Performs initial safe PDF cleanup, decryption, and structure optimization using PyMuPDF.
    
    Args:
        input_pdf (str): Source PDF path
        output_pdf (str): Destination PDF path
        password (str, optional): Password for encrypted PDF
        strip_metadata (bool): If True, purges PDF author, title, creation date, and annotations.
    """
    doc = fitz.open(input_pdf)
    if doc.is_encrypted:
        if password:
            if not doc.authenticate(password):
                doc.close()
                raise ValueError("Incorrect password for encrypted PDF.")
        else:
            doc.close()
            raise ValueError("PDF is encrypted. Password required.")

    if strip_metadata:
        doc.set_metadata({})
        for page in doc:
            for annot in page.annots():
                page.delete_annot(annot)

    doc.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True
    )
    doc.close()


def compress_with_ghostscript(input_pdf, output_pdf, level="medium"):
    """
    Compresses a PDF file using Ghostscript.
    """
    gs_path = find_ghostscript()
    if not gs_path:
        raise RuntimeError("Ghostscript executable not found. Please install Ghostscript.")

    gs_setting = GS_LEVEL_MAP.get(level.lower(), "ebook")

    cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{gs_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ghostscript execution failed: {result.stderr}")


def calculate_quality_metrics(orig_img, comp_img):
    """
    Computes PSNR (Peak Signal-to-Noise Ratio) and SSIM (Structural Similarity Index).
    """
    if not orig_img or not comp_img:
        return {"psnr_db": 0.0, "ssim_percent": 100.0}

    orig = orig_img.convert("L")
    comp = comp_img.convert("L")

    if orig.size != comp.size:
        comp = comp.resize(orig.size, Image.Resampling.BILINEAR)

    arr1 = np.array(orig, dtype=np.float64)
    arr2 = np.array(comp, dtype=np.float64)

    mse = np.mean((arr1 - arr2) ** 2)
    if mse == 0:
        psnr = 100.0
    else:
        psnr = float(20.0 * np.log10(255.0 / np.sqrt(mse)))

    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    mu1 = np.mean(arr1)
    mu2 = np.mean(arr2)
    var1 = np.var(arr1)
    var2 = np.var(arr2)
    cov12 = np.cov(arr1.flatten(), arr2.flatten())[0, 1]

    ssim_val = ((2 * mu1 * mu2 + c1) * (2 * cov12 + c2)) / ((mu1**2 + mu2**2 + c1) * (var1 + var2 + c2))
    ssim_percent = float(np.clip(ssim_val * 100.0, 0.0, 100.0))

    return {
        "psnr_db": round(psnr, 2),
        "ssim_percent": round(ssim_percent, 2)
    }


def compress_pdf(input_pdf, output_pdf, level="medium", password=None, strip_metadata=False):
    """
    Executes the full compression pipeline with password decryption and metadata stripping options.
    """
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input file not found: {input_pdf}")

    original_size = os.path.getsize(input_pdf) / 1024.0
    intermediate_pdf = output_pdf + ".tmp.pdf"

    try:
        safe_optimize_pdf(input_pdf, intermediate_pdf, password=password, strip_metadata=strip_metadata)
        compress_with_ghostscript(intermediate_pdf, output_pdf, level=level)
    finally:
        if os.path.exists(intermediate_pdf):
            try:
                os.remove(intermediate_pdf)
            except Exception:
                pass

    compressed_size = os.path.getsize(output_pdf) / 1024.0
    reduction = ((original_size - compressed_size) / original_size * 100.0) if original_size > 0 else 0.0

    orig_img = render_page_preview(input_pdf, page_num=0, password=password)
    comp_img = render_page_preview(output_pdf, page_num=0)
    q_metrics = calculate_quality_metrics(orig_img, comp_img)

    return {
        "original_size_kb": round(original_size, 2),
        "compressed_size_kb": round(compressed_size, 2),
        "reduction_percent": round(reduction, 2),
        "psnr_db": q_metrics["psnr_db"],
        "ssim_percent": q_metrics["ssim_percent"]
    }


def render_page_preview(pdf_path, page_num=0, dpi=100, password=None):
    """
    Renders a single page of a PDF file to a PIL Image.
    """
    if not os.path.exists(pdf_path):
        return None
    try:
        doc = fitz.open(pdf_path)
        if doc.is_encrypted and password:
            doc.authenticate(password)
        if len(doc) <= page_num:
            page_num = 0
        page = doc[page_num]
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        doc.close()
        return Image.open(io.BytesIO(img_bytes))
    except Exception:
        return None
