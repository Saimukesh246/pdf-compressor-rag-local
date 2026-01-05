# 📄 PDF Compressor (Hybrid RAG + Ghostscript)

A fully offline PDF compression tool built with Python and Streamlit, using a
hybrid decision engine (rule-based + RAG fallback) and Ghostscript for safe,
high-quality compression — without black images or PDF corruption.

---

## 🚀 Features

- Fully offline (no APIs, no cloud)
- Fast rule-based decision engine
- RAG fallback for ambiguous PDFs
- Ghostscript-powered compression (industry standard)
- No black images or broken PDFs
- Up to 80% file size reduction
- Interactive Streamlit UI
- One-click PDF download

---

## 🧠 Why Hybrid (Rules + RAG)?

PDF compression itself is deterministic, but choosing the right compression
strategy is not.

This project uses:
- Rule-based heuristics for clear cases (fast)
- RAG (Retrieval-Augmented Generation) to retrieve the best strategy from a
  knowledge base when rules are uncertain

RAG is used only for decision-making, not for compressing file bytes.

---

## 🏗️ Architecture

PDF Upload  
↓  
PDF Analyzer  
↓  
Rule Engine ── confident? ── YES → Strategy  
        │  
        NO  
        ↓  
       RAG (Vector Search)  
           ↓  
       Strategy  
           ↓  
Safe PDF Cleanup (PyMuPDF)  
           ↓  
Ghostscript Compression  
           ↓  
Compressed PDF Download  

---

## 🧰 Tech Stack

- UI: Streamlit
- PDF Analysis: PyMuPDF
- Decision Engine: Rules + RAG
- Embeddings: sentence-transformers
- Vector Search: FAISS
- Compression Engine: Ghostscript
- Language: Python

---

## 📦 Project Structure

```text
pdf-compressor-rag-local/
│
├── streamlit_app.py
├── README.md
├── requirements.txt
│
├── analyzer/
│   └── pdf_analyzer.py
│
├── decision/
│   └── rule_engine.py
│
├── rag/
│   ├── embedder.py
│   ├── indexer.py
│   └── retriever.py
│
├── compressor/
│   └── pdf_optimizer.py
│
└── data/
    └── knowledge_base.txt
