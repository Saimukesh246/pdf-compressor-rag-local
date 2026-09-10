import os
import sys
import tempfile
import zipfile
import base64
import io
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path for Vercel serverless imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.pdf_analyzer import analyze_pdf
from decision.hybrid_decider import decide_strategy
from rag.indexer import build_index
from rag.pdf_rag import query_pdf_content
from compressor.pdf_optimizer import (
    find_ghostscript,
    compress_pdf,
    safe_optimize_pdf,
    render_page_preview
)

app = FastAPI(
    title="PDF Compressor & RAG Assistant API",
    description="Vercel Serverless API for PDF Compression and RAG Semantic Search",
    version="1.0.0"
)

# Global RAG Knowledge Base Initialization
KB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge_base.txt")
if os.path.exists(KB_PATH):
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = [line.strip() for line in f if line.strip()]
else:
    KNOWLEDGE_BASE = [
        "Image-heavy PDF: Downscale images to 150 DPI and apply lossy JPEG compression.",
        "Text-heavy PDF: Remove unused font subsets and optimize object streams.",
        "Scanned PDF: Downsample background images and retain text layers."
    ]

# Lazy-loaded FAISS index
RAG_INDEX = None

def get_rag_index():
    global RAG_INDEX
    if RAG_INDEX is None:
        index, _ = build_index(KNOWLEDGE_BASE)
        RAG_INDEX = index
    return RAG_INDEX

@app.get("/api/health")
def health_check():
    gs_path = find_ghostscript()
    return {
        "status": "healthy",
        "ghostscript_available": gs_path is not None,
        "ghostscript_path": gs_path,
        "rag_knowledge_items": len(KNOWLEDGE_BASE)
    }

@app.post("/api/compress")
async def compress_pdf_endpoint(
    file: UploadFile = File(...),
    level: str = Form("medium")
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        output_path = os.path.join(tmpdir, "compressed.pdf")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # 1. Analyze PDF
        try:
            metrics = analyze_pdf(input_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to analyze PDF: {e}")

        # 2. Decision Engine Strategy
        rag_idx = get_rag_index()
        strategy, decision_mode, rag_details = decide_strategy(metrics, rag_idx, KNOWLEDGE_BASE)

        # 3. Compression Execution
        gs_path = find_ghostscript()
        if gs_path:
            stats = compress_pdf(input_path, output_path, level=level)
        else:
            # Fallback for pure Python Vercel serverless environment using PyMuPDF
            safe_optimize_pdf(input_path, output_path)
            orig_kb = len(contents) / 1024.0
            comp_kb = os.path.getsize(output_path) / 1024.0
            reduction = ((orig_kb - comp_kb) / orig_kb * 100.0) if orig_kb > 0 else 0.0
            stats = {
                "original_size_kb": orig_kb,
                "compressed_size_kb": comp_kb,
                "reduction_percent": reduction
            }

        # 4. Render Page 1 Preview Thumbnails (base64)
        orig_img = render_page_preview(input_path, page_num=0)
        comp_img = render_page_preview(output_path, page_num=0)

        orig_b64 = None
        comp_b64 = None

        if orig_img:
            buf = io.BytesIO()
            orig_img.save(buf, format="PNG")
            orig_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        if comp_img:
            buf = io.BytesIO()
            comp_img.save(buf, format="PNG")
            comp_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Read compressed file bytes
        with open(output_path, "rb") as f:
            compressed_bytes = f.read()

        compressed_b64 = base64.b64encode(compressed_bytes).decode("utf-8")

        return JSONResponse(content={
            "filename": file.filename,
            "metrics": metrics,
            "decision_mode": decision_mode,
            "strategy": strategy,
            "rag_details": rag_details,
            "stats": stats,
            "compressed_file_b64": compressed_b64,
            "preview_original_b64": orig_b64,
            "preview_compressed_b64": comp_b64
        })

@app.post("/api/ask")
async def ask_pdf_endpoint(
    file: UploadFile = File(...),
    query: str = Form(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "target.pdf")
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        results = query_pdf_content(input_path, query, top_k=4)
        return {
            "filename": file.filename,
            "query": query,
            "matches_count": len(results),
            "results": results
        }

@app.post("/api/batch")
async def batch_compress_endpoint(
    files: list[UploadFile] = File(...),
    level: str = Form("medium")
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    zip_buffer = io.BytesIO()
    results_summary = []

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, file in enumerate(files):
                if not file.filename.lower().endswith(".pdf"):
                    continue

                in_path = os.path.join(tmpdir, f"in_{idx}.pdf")
                out_path = os.path.join(tmpdir, f"out_{idx}.pdf")

                contents = await file.read()
                with open(in_path, "wb") as f:
                    f.write(contents)

                gs_path = find_ghostscript()
                if gs_path:
                    stats = compress_pdf(in_path, out_path, level=level)
                else:
                    safe_optimize_pdf(in_path, out_path)
                    orig_kb = len(contents) / 1024.0
                    comp_kb = os.path.getsize(out_path) / 1024.0
                    reduction = ((orig_kb - comp_kb) / orig_kb * 100.0) if orig_kb > 0 else 0.0
                    stats = {
                        "original_size_kb": orig_kb,
                        "compressed_size_kb": comp_kb,
                        "reduction_percent": reduction
                    }

                zip_file.write(out_path, arcname=f"compressed_{file.filename}")
                results_summary.append({
                    "filename": file.filename,
                    "stats": stats
                })

    zip_buffer.seek(0)
    zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode("utf-8")

    return {
        "files_processed": len(results_summary),
        "results": results_summary,
        "zip_b64": zip_b64
    }

# Mount static frontend directory if present
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
