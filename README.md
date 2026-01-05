# 📄 PDF Compressor (Hybrid RAG + Ghostscript)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)]()
[![Ghostscript](https://img.shields.io/badge/Ghostscript-Required-blueviolet)](https://www.ghostscript.com/)

A **fully offline PDF compression tool** built with **Python** and **Streamlit**.  
It uses a hybrid (Rules + RAG) decision engine to choose the best compression
strategy, and **Ghostscript** for safe, high-quality PDF rebuilding —  
no cloud, no API calls, and no black images or file corruption.

---

## 🚀 Key Features

✅ 100% offline (no local or remote APIs)  
⚡ Fast rule-based decision engine  
🧠 RAG fallback for ambiguous PDFs  
🌀 Ghostscript-powered compression (industry standard)  
🧩 Up to 80% file size reduction  
💾 One-click PDF download via Streamlit UI  
🖼️ No corrupted images or broken transparency  

---

## 🧠 Why Hybrid (Rules + RAG)?

PDF compression is deterministic, but **selecting the right strategy isn’t**.

This project blends:
- **Rule-based heuristics** → for clear, predictable cases.
- **RAG (Retrieval-Augmented Generation)** → for uncertain cases, using vector search to retrieve the best past strategy.

> 🧩 Note: RAG is *only* used for decision-making, not compression itself.

---

## 🏗️ System Architecture

```text
PDF Upload  
   │  
   ▼  
PDF Analyzer (PyMuPDF)  
   │  
   ▼  
Rule Engine ── confident? ── YES → Strategy  
       │  
       NO  
       ▼  
     RAG Search (FAISS + embeddings)  
       │  
       ▼  
Compression Strategy  
       │  
       ▼  
Safe PDF Rebuild (Ghostscript)  
       │  
       ▼  
Compressed PDF Download
```

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| UI | Streamlit |
| PDF Analyzer | PyMuPDF |
| Decision Engine | Rules + RAG |
| Embeddings | Sentence-Transformers |
| Vector Search | FAISS |
| Compression Engine | Ghostscript |
| Language | Python |

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
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/pdf-compressor-rag-local.git
cd pdf-compressor-rag-local
```

### 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Install Ghostscript
Ghostscript handles PDF rebuilding.

**Windows**  
Download: [https://www.ghostscript.com/releases/gsdnld.html](https://www.ghostscript.com/releases/gsdnld.html)  
Then verify:
```bash
gswin64c --version
```

**Linux**
```bash
sudo apt install ghostscript
```

**macOS (Homebrew)**
```bash
brew install ghostscript
```

---

## ▶️ Run the Application

```bash
streamlit run streamlit_app.py
```

Open your browser and navigate to:  
👉 [http://localhost:8501](http://localhost:8501)

---

## 🖥️ How to Use

1. Upload a PDF file.  
2. Select **compression level**:  
   - 🟢 Low → Best quality  
   - 🟡 Medium → Balanced (recommended)  
   - 🔴 High → Smallest size (lossy)  
3. Click **Compress PDF**.  
4. Download and compare results.

---

## 📊 Compression Levels

| Level | Description |
|--------|--------------|
| Low | Minimal compression, visually lossless |
| Medium | Balanced compression (recommended) |
| High | Maximum compression, some image loss |

⚠️ *High compression mode may slightly reduce image quality.*

---

## 🧪 Expected Results

| PDF Type | Typical Reduction |
|-----------|-------------------|
| Text-heavy | 30–50% |
| Image-heavy | 60–85% |
| Scanned PDFs | 70–90% |

> 📉 Actual results depend on input quality and image density.

---

## 🛡️ Why Ghostscript?

Low-level image compression often breaks PDFs (e.g., black images, lost transparency).  
Ghostscript rebuilds the PDF safely, ensuring:
- ✅ Color profile preservation  
- ✅ Transparency accuracy  
- ✅ Proper masking and rendering  
- ✅ Reliable file integrity  

> The same approach is used by many professional, paid PDF compressors.

---

## 🧠 Resume-Ready Summary

> Built an **offline, AI-assisted PDF compression system** using Python, Streamlit, and Ghostscript.  
> Combined **rule-based heuristics** with a **RAG (Retrieval-Augmented Generation)** decision system to safely reduce PDF file sizes by up to **80%** — without image corruption or PDF failure.

---

## 🔮 Future Enhancements

- 🗂️ Batch PDF compression  
- 👁️ Before/after visual preview  
- 🔤 OCR support for scanned PDFs  
- 💻 CLI mode (pure terminal)  
- 🐳 Dockerized deployment  

---

⭐ **If you find this project useful, please consider giving it a star!**

---

💬 *Maintained by [Sai mukesh](https://github.com/Saimukesh246)*  
📧 *For suggestions and contributions, feel free to open a pull request or issue.*
