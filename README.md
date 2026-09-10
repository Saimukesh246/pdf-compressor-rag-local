# 📄 PDF Compressor & RAG Engine (Hybrid Rules + FAISS + Ghostscript + Vercel)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Serverless-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployable-black?logo=vercel)](https://vercel.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, offline-first **PDF Compression and RAG Semantic Assistant System**.  
It blends a **hybrid decision engine** (Deterministic Rules + FAISS Vector RAG) with **PyMuPDF object cleaning**, **Ghostscript rebuilding**, **Tesseract OCR**, and **SSIM/PSNR visual quality verification**.

Deployable on **Vercel** (FastAPI serverless backend + Glassmorphism Web UI), **Streamlit Community Cloud**, or **Docker** containers.

---

## 🚀 Key Features

- ✅ **Hybrid Decision Engine**: Rules fast-path + FAISS Vector RAG fallback for strategy selection.
- 💬 **Ask PDF (RAG Assistant)**: Page-level windowed chunking and in-memory FAISS semantic Q&A over PDF content.
- 🛡️ **Ghostscript + PyMuPDF Safe Rebuild**: Up to 85% file size reduction without black images or lost transparency.
- 📐 **Visual Quality Metrics**: Calculates real-time **PSNR** (dB) and **SSIM** (%) visual retention scores.
- 🔤 **OCR Engine**: Tesseract OCR fallback for text extraction from scanned/image-only PDFs.
- 👁️ **Before / After Visual Page Preview**: Side-by-side Page 1 rendered image comparison.
- 📁 **Batch Compression**: Process multiple PDFs in parallel and export ZIP archives.
- ⚡ **Multi-Platform Deployment**: Vercel Serverless API, Streamlit Web App, CLI tool, or Docker container.

---

## 🏗️ System Architecture

```text
PDF Upload / Input
       │
       ▼
PDF Content & Structure Inspection (PyMuPDF / Tesseract OCR)
       │
       ▼
Rule Engine ── Confident? ── YES ──► Selected Strategy
       │
       NO
       ▼
RAG Vector Search (FAISS + sentence-transformers) ──► Selected Strategy
       │
       ▼
PyMuPDF Safe Stream Clean (garbage=4, deflate=True)
       │
       ▼
Ghostscript PDF Rebuild & Downsampling (pdfwrite)
       │
       ▼
Quality Metrics (PSNR / SSIM) & Compressed PDF Download
```

---

## 📂 Project Structure

```text
pdf-compressor-rag-local/
├── api/
│   └── index.py            # FastAPI Serverless Backend for Vercel
├── analyzer/
│   └── pdf_analyzer.py     # PDF Structural & Density Inspector
├── decision/
│   ├── rule_engine.py      # Deterministic Rule Heuristics
│   └── hybrid_decider.py   # Hybrid Rules + RAG Strategy Decider
├── compressor/
│   └── pdf_optimizer.py    # PyMuPDF + Ghostscript Compressor & SSIM/PSNR Engine
├── rag/
│   ├── embedder.py         # SentenceTransformer Embeddings
│   ├── indexer.py          # FAISS Knowledge Base Indexer
│   ├── retriever.py        # Top-K Strategy Scored Retriever
│   └── pdf_rag.py          # PDF Document Content Chunking & Vector Search
├── ocr/
│   └── ocr_engine.py       # Tesseract OCR Extraction Engine
├── public/
│   ├── index.html          # Glassmorphism HTML5 Web UI
│   ├── style.css           # Dark Mode CSS Design System
│   └── app.js             # Client JS connecting REST endpoints
├── tests/
│   ├── test_compressor.py  # Unit Tests for Analyzer & Compressor
│   ├── test_rag.py         # Unit Tests for RAG & FAISS Search
│   └── test_api.py         # Unit Tests for FastAPI Endpoints
├── data/
│   └── knowledge_base.txt  # RAG Strategy Knowledge Items
├── app.py                  # CLI Interface (--ask & --batch)
├── streamlit_app.py        # Streamlit Interactive Web App
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

### 2. Streamlit Web Application
```powershell
streamlit run streamlit_app.py
```
Navigate to `http://localhost:8501`.

### 3. FastAPI Local Web Server (Vercel Mode)
```powershell
python -m uvicorn api.index:app --reload --port 8000
```
Navigate to `http://localhost:8000`.

---

## 🚀 Deployment Instructions

### A. Deploying to Vercel
1. Install Vercel CLI or connect your GitHub repository to Vercel.
2. Run `vercel --prod` or click **Deploy** on Vercel.
3. Vercel automatically detects `vercel.json`, builds serverless functions in `api/index.py`, and hosts the static web interface in `public/`.

### B. Deploying via Docker
```bash
docker compose up --build
```
- FastAPI REST server runs at `http://localhost:8000`.
- Streamlit Web App runs at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the complete test suite (11 unit tests):
```powershell
python -m unittest discover tests
```

---

## 🧠 Resume-Ready Summary

> Built an **enterprise-grade, offline-first PDF Compression & RAG Assistant Platform** in Python using PyMuPDF, Ghostscript, FAISS vector search, and FastAPI. Implemented a **hybrid decision engine** (Rules + Vector RAG), **Tesseract OCR**, **PSNR/SSIM visual quality verification**, and deployed serverless on **Vercel** with a glassmorphism web interface.

---

## 📜 License

Distributed under the [MIT License](LICENSE).
