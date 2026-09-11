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

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.pdf_analyzer import analyze_pdf
from decision.hybrid_decider import decide_strategy
from rag.indexer import build_index
from rag.pdf_rag import query_pdf_content
from rag.llm_synthesizer import synthesize_rag_answer, generate_pdf_mindmap
from compressor.pdf_optimizer import (
    find_ghostscript,
    compress_pdf,
    safe_optimize_pdf,
    render_page_preview
)
from compressor.pdf_manipulator import merge_pdfs, split_pdf

app = FastAPI(
    title="PDF Compressor & RAG Assistant API",
    description="Vercel Serverless API for PDF Compression, Manipulation, and RAG Q&A",
    version="1.2.0"
)

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
    level: str = Form("medium"),
    password: Optional[str] = Form(None),
    strip_metadata: bool = Form(False),
    grayscale: bool = Form(False)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        output_path = os.path.join(tmpdir, "compressed.pdf")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        try:
            metrics = analyze_pdf(input_path, password=password)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to analyze PDF: {e}")

        rag_idx = get_rag_index()
        strategy, decision_mode, rag_details = decide_strategy(metrics, rag_idx, KNOWLEDGE_BASE)

        gs_path = find_ghostscript()
        if gs_path:
            stats = compress_pdf(input_path, output_path, level=level, password=password, strip_metadata=strip_metadata, grayscale=grayscale)
        else:
            safe_optimize_pdf(input_path, output_path, password=password, strip_metadata=strip_metadata)
            orig_kb = len(contents) / 1024.0
            comp_kb = os.path.getsize(output_path) / 1024.0
            reduction = ((orig_kb - comp_kb) / orig_kb * 100.0) if orig_kb > 0 else 0.0
            stats = {
                "original_size_kb": orig_kb,
                "compressed_size_kb": comp_kb,
                "reduction_percent": reduction,
                "psnr_db": 0.0,
                "ssim_percent": 100.0
            }

        orig_img = render_page_preview(input_path, page_num=0, password=password)
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

@app.post("/api/batch")
async def batch_compress_endpoint(
    files: list[UploadFile] = File(...),
    level: str = Form("medium")
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch compression.")

    results = []
    zip_buffer = io.BytesIO()

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, file in enumerate(files):
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
                        "reduction_percent": reduction,
                        "psnr_db": 0.0,
                        "ssim_percent": 100.0
                    }

                zip_file.write(out_path, arcname=f"compressed_{file.filename}")
                results.append({
                    "filename": file.filename,
                    "stats": stats
                })

    zip_buffer.seek(0)
    zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode("utf-8")

    return JSONResponse(content={
        "processed_count": len(results),
        "results": results,
        "zip_b64": zip_b64
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
        synthesized_answer = synthesize_rag_answer(query, results)

        return {
            "filename": file.filename,
            "query": query,
            "matches_count": len(results),
            "synthesized_answer": synthesized_answer,
            "results": results
        }

@app.post("/api/mindmap")
async def mindmap_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "target.pdf")
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        res = generate_pdf_mindmap(input_path)
        return {
            "filename": file.filename,
            "summary_text": res["summary_text"],
            "mermaid_code": res["mermaid_code"]
        }

@app.post("/api/merge")
async def merge_pdfs_endpoint(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least two PDF files are required for merging.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_paths = []
        for idx, file in enumerate(files):
            in_path = os.path.join(tmpdir, f"in_{idx}.pdf")
            contents = await file.read()
            with open(in_path, "wb") as f:
                f.write(contents)
            input_paths.append(in_path)

        out_path = os.path.join(tmpdir, "merged.pdf")
        res = merge_pdfs(input_paths, out_path)

        with open(out_path, "rb") as f:
            merged_bytes = f.read()

        return JSONResponse(content={
            "filename": "merged.pdf",
            "total_pages": res["total_pages"],
            "file_size_kb": res["file_size_kb"],
            "merged_file_b64": base64.b64encode(merged_bytes).decode("utf-8")
        })

@app.post("/api/split")
async def split_pdf_endpoint(
    file: UploadFile = File(...),
    range_str: str = Form("1-1")
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        res = split_pdf(input_path, tmpdir, range_str=range_str)
        output_path = res["output_path"]

        with open(output_path, "rb") as f:
            split_bytes = f.read()

        return JSONResponse(content={
            "filename": f"split_{file.filename}",
            "extracted_pages": res["extracted_pages"],
            "file_size_kb": res["file_size_kb"],
            "split_file_b64": base64.b64encode(split_bytes).decode("utf-8")
        })

public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
