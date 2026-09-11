# 📄 PDF Enterprise Studio & RAG Assistant Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Serverless-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange)](https://github.com/facebookresearch/faiss)
[![Vercel](https://img.shields.io/badge/Vercel-Deployable-black?logo=vercel)](https://vercel.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, offline-first **PDF Compression, Security, Security Redaction, Conversion & RAG Assistant Platform**.  
It blends a **hybrid decision engine** (Deterministic Rules + FAISS Vector RAG) with **PyMuPDF object cleaning**, **Ghostscript rebuilding**, **Tesseract OCR**, **AES-256 Encryption**, **Diagonal Watermarking**, **PII Auto-Redaction**, **PDF ↔ PNG Converter**, and **SSIM/PSNR visual quality verification**.

Deployable on **FastAPI** (FastAPI backend + Glassmorphism Web UI), **Vercel Serverless**, or **Docker** containers.

---

## 🚀 Key Features

- ✅ **Hybrid Decision Engine**: Rules fast-path + FAISS Vector RAG fallback for strategy selection.
- 💬 **Ask PDF (RAG Assistant)**: Page-level windowed chunking and in-memory FAISS semantic Q&A over PDF content.
- 🧠 **Executive Mindmap Generator**: Automatic Mermaid mindmap generation and document summary synthesis.
- 🏷️ **PDF Watermarking Engine**: Apply custom diagonal text watermarks (e.g. `CONFIDENTIAL`, `DRAFT`) with opacity and angle controls.
- 🛡️ **Automated PII Redaction**: Detect and permanently black-box sensitive PII (Emails, Phone numbers, Credit Cards, SSNs).
- 🔒 **AES-256 PDF Security**: Password-encrypt unprotected PDFs or decrypt unlocked files.
- 🖼️ **PDF ↔ Image Converter**: Render PDF pages to high-DPI PNG ZIP archives or merge image collections into a PDF.
- 📝 **Structured Markdown Exporter**: Export clean Markdown text and JSON page representations for LLM dataset ingestion.
- 📐 **Visual Quality Metrics**: Calculates real-time **PSNR** (dB) and **SSIM** (%) visual retention scores.
- 🔤 **OCR Engine**: Tesseract OCR fallback for text extraction from scanned/image-only PDFs.
- 👁️ **Before / After Visual Page Preview**: Side-by-side Page 1 rendered image comparison.
- 📁 **Batch Processing**: Process multiple PDFs in parallel and export ZIP archives.
- ⚡ **Multi-Platform Deployment**: Vercel Serverless API, FastAPI Web Server, CLI tool, or Docker container.

---

## 🏗️ System Architecture

```text
PDF Upload / Input
       │
       ▼
PDF Inspection (PyMuPDF / Tesseract OCR / PII Inspector)
       │
       ▼
Rule Engine ── Confident? ── YES ──► Selected Strategy
       │
       NO
       ▼
RAG Vector Search (FAISS + sentence-transformers) ──► Selected Strategy
       │
       ▼
Security & Transformations (AES-256 / Watermark / Redact / Image Convert / Exporter)
       │
       ▼
PyMuPDF Safe Stream Clean (garbage=4, deflate=True)
       │
       ▼
Ghostscript PDF Rebuild & Downsampling (pdfwrite)
       │
       ▼
Quality Metrics (PSNR / SSIM) & Output Download
```

---

## 📂 Project Structure

```text
pdf-compressor-rag-local/
├── api/
│   └── index.py            # FastAPI Server Backend & REST Endpoints
├── analyzer/
│   ├── pdf_analyzer.py     # PDF Structural & Density Inspector
│   └── pii_redactor.py     # Regex Automated PII Redaction Engine
├── decision/
│   ├── rule_engine.py      # Deterministic Rule Heuristics
│   └── hybrid_decider.py   # Hybrid Rules + RAG Strategy Decider
├── compressor/
│   ├── pdf_optimizer.py    # PyMuPDF + Ghostscript Compressor & SSIM/PSNR Engine
│   ├── pdf_manipulator.py  # PDF Page Range Splitter & Multi-Document Merger
│   ├── pdf_watermark.py    # Diagonal Vector Watermarking Engine
│   ├── pdf_security.py     # AES-256 PDF Encryption & Decryption
│   └── pdf_converter.py    # PDF ↔ Images (PNG ZIP) Conversion Engine
├── rag/
│   ├── embedder.py         # SentenceTransformer Embeddings
│   ├── indexer.py          # FAISS Knowledge Base Indexer
│   ├── retriever.py        # Top-K Strategy Scored Retriever
│   ├── pdf_rag.py          # PDF Document Content Chunking & Vector Search
│   ├── llm_synthesizer.py  # Q&A Synthesizer & Mermaid Mindmap Generator
│   └── pdf_exporter.py     # Structured Markdown & JSON Page Exporter
├── ocr/
│   └── ocr_engine.py       # Tesseract OCR Extraction Engine
├── public/
│   ├── index.html          # Dark Mode Glassmorphism HTML5 Web UI
│   ├── style.css           # SaaS CSS Design System
│   └── app.js             # Client JS & Toast Notification Manager
├── tests/
│   ├── test_compressor.py  # Unit Tests for Analyzer & Compressor
│   ├── test_rag.py         # Unit Tests for RAG & FAISS Search
│   ├── test_api.py         # Unit Tests for FastAPI Endpoints
│   ├── test_manipulator.py# Unit Tests for Splitter & Merger
│   ├── test_bonus_features.py # Unit Tests for Encrypted PDFs & Metadata
│   └── test_new_features.py # Unit Tests for Watermark, Redact, Security & Exporter
├── data/
│   └── knowledge_base.txt  # RAG Strategy Knowledge Items
├── app.py                  # CLI Interface (--ask & --batch)
├── pytest.ini              # Pytest Configuration
├── vercel.json             # Vercel Deployment Config
├── Dockerfile              # Container Build File
├── docker-compose.yml      # Docker Compose Config
└── requirements.txt        # Python Dependencies
```

---

## 💻 Quick Start & Usage

### 1. Command Line Interface (CLI)
```powershell
# Compress a single PDF
python app.py -i document.pdf -o compressed.pdf -l medium

# Batch compress an entire folder
python app.py -i ./pdf_folder -o ./output_folder -l high --batch

# Ask a semantic RAG question about any PDF document
python app.py -i document.pdf --ask "What are the main findings in this report?"
```

### 2. FastAPI Web Application Server
```powershell
python -m uvicorn api.index:app --reload --port 8000
```
Navigate to `http://localhost:8000`.

---

## 🚀 Deployment Instructions

### A. Deploying via Docker
```bash
docker compose up --build
```
- FastAPI REST server & Web Interface run at `http://localhost:8000`.

### B. Deploying to Vercel
1. Install Vercel CLI or connect your GitHub repository to Vercel.
2. Run `vercel --prod` or click **Deploy** on Vercel.
3. Vercel automatically detects `vercel.json`, builds serverless functions in `api/index.py`, and hosts the static web interface in `public/`.

---

## 🧪 Running Automated Tests

Run the complete test suite (25 unit tests):
```powershell
pytest
```

---

## 🧠 Resume-Ready Summary

> Built an **enterprise-grade, offline-first PDF Suite & RAG Assistant Platform** in Python using PyMuPDF, Ghostscript, FAISS vector search, and FastAPI. Implemented a **hybrid decision engine** (Rules + Vector RAG), **Tesseract OCR**, **AES-256 Encryption**, **Automated PII Redaction**, **Diagonal Watermarking**, **PDF ↔ Image Conversion**, **PSNR/SSIM visual quality verification**, and deployed on **FastAPI & Docker** with a production dark glassmorphism web interface.

---

## 📜 License

Distributed under the [MIT License](LICENSE).
