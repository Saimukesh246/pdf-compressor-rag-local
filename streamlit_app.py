import streamlit as st
import os
import tempfile
import time
import zipfile
import io

from analyzer.pdf_analyzer import analyze_pdf
from decision.hybrid_decider import decide_strategy
from rag.indexer import build_index
from rag.pdf_rag import build_pdf_index, query_pdf_content
from rag.llm_synthesizer import synthesize_rag_answer
from compressor.pdf_optimizer import (
    find_ghostscript,
    compress_pdf,
    render_page_preview
)

# =========================================================
# Page Setup & Configuration
# =========================================================
st.set_page_config(
    page_title="PDF Compressor & RAG Assistant",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# Creative Glassmorphism & High-Tech Design System (CSS)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global Font & Background Styling */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
    background: #090d16 !important;
    color: #f1f5f9;
}

/* Ambient Animated Radial Background Glows */
.stApp::before {
    content: '';
    position: fixed;
    top: -10%;
    left: -10%;
    width: 65vw;
    height: 65vh;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.08) 40%, transparent 70%);
    z-index: 0;
    pointer-events: none;
    animation: floatGlow 14s ease-in-out infinite alternate;
}

.stApp::after {
    content: '';
    position: fixed;
    bottom: -10%;
    right: -10%;
    width: 65vw;
    height: 65vh;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, rgba(59, 130, 246, 0.08) 40%, transparent 70%);
    z-index: 0;
    pointer-events: none;
    animation: floatGlow 18s ease-in-out infinite alternate-reverse;
}

@keyframes floatGlow {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, 20px) scale(1.08); }
    100% { transform: translate(-20px, 40px) scale(0.95); }
}

/* Main Container Padding */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1250px !important;
}

/* Hero Header Banner */
.hero-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.hero-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #06b6d4, #10b981);
}

.hero-title {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem !important;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.hero-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.feature-pill {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    backdrop-filter: blur(8px);
}

.feature-pill.green {
    background: rgba(16, 185, 129, 0.12);
    border-color: rgba(16, 185, 129, 0.3);
    color: #6ee7b7;
}

/* Styled Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.6rem !important;
    background: rgba(15, 23, 42, 0.75) !important;
    padding: 0.5rem !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(16px) !important;
    margin-bottom: 1.8rem !important;
}

.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    white-space: pre !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    padding: 0 1.25rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #f8fafc !important;
    background: rgba(255, 255, 255, 0.06) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
}

.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Streamlit Metric Cards Styling */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8)) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.1rem 1.3rem !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    position: relative;
    overflow: hidden;
}

div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #06b6d4);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: #f8fafc !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Primary Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.5) !important;
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
}

div.stButton > button:active {
    transform: translateY(0) !important;
}

/* Custom Download Button Styling */
div.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.5) !important;
}

/* Upload Box Customization */
div[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 2px dashed rgba(99, 102, 241, 0.35) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
    background: rgba(99, 102, 241, 0.08) !important;
}

/* Select Box & Text Input Styling */
div[data-baseweb="select"] > div, input[type="text"], input[type="password"] {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}

/* Custom Expander Styling */
div[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(10px) !important;
}

/* Hide default Streamlit footer and hamburger menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# System Check: Ghostscript
# =========================================================
GS_PATH = find_ghostscript()

# =========================================================
# Load RAG Knowledge Base (cached)
# =========================================================
@st.cache_resource
def load_rag():
    kb_path = "data/knowledge_base.txt"
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            knowledge = [line.strip() for line in f if line.strip()]
    else:
        knowledge = [
            "Image-heavy PDF: Downscale images to 150 DPI and apply lossy compression.",
            "Text-heavy PDF: Remove unused font subsets and optimize stream objects.",
            "Scanned PDF: Downsample background images while preserving text."
        ]
    index, _ = build_index(knowledge)
    return knowledge, index

knowledge, rag_index = load_rag()

# =========================================================
# Streamlit Hero Header Banner
# =========================================================
gs_badge = f'<span class="feature-pill green">⚡ Ghostscript Active ({GS_PATH})</span>' if GS_PATH else '<span class="feature-pill red">❌ Ghostscript Missing</span>'

st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">
        <span>📄 PDF Compressor & RAG Assistant</span>
    </div>
    <div class="hero-subtitle">
        <span class="feature-pill">🎯 Hybrid Rule Engine</span>
        <span class="feature-pill">🧠 FAISS Vector RAG</span>
        <span class="feature-pill">💬 LLM Synthesis</span>
        <span class="feature-pill">📐 PSNR/SSIM Quality Engine</span>
        {gs_badge}
    </div>
</div>
""", unsafe_allow_html=True)

if not GS_PATH:
    st.error(
        "❌ Ghostscript not found on host system.\n\n"
        "Please install Ghostscript from: https://www.ghostscript.com/releases/gsdnld.html"
    )
    st.stop()

# =========================================================
# Navigation Tabs
# =========================================================
tab_single, tab_batch, tab_ask_pdf, tab_about = st.tabs([
    "📄 Single PDF Compression",
    "📁 Batch Compression",
    "💬 Ask PDF (RAG Assistant)",
    "ℹ️ Architecture & RAG Details"
])

# =========================================================
# TAB 1: Single PDF Compression
# =========================================================
with tab_single:
    col_settings, col_upload = st.columns([1, 2])

    with col_settings:
        st.subheader("⚙️ Settings")
        compression_level = st.selectbox(
            "Compression Profile",
            ["Medium (Recommended)", "Low (Best Quality)", "High (Smallest Size)"],
            index=0
        )
        
        level_key_map = {
            "Low (Best Quality)": "low",
            "Medium (Recommended)": "medium",
            "High (Smallest Size)": "high"
        }
        selected_level = level_key_map[compression_level]

        pdf_password = st.text_input("PDF Password (if encrypted)", type="password")
        strip_metadata_toggle = st.checkbox("Purge Metadata & Annotations", value=False)

        st.info(
            "• **Low**: Visually lossless print quality\n"
            "• **Medium**: Balanced quality & size (ebook)\n"
            "• **High**: Aggressive downsampling (screen)"
        )

    with col_upload:
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="single_pdf")
        
        active_file = uploaded_file
        if not active_file:
            file_param = st.query_params.get("file", None)
            if file_param and os.path.exists(file_param):
                try:
                    with open(file_param, "rb") as f:
                        class MockFile(io.BytesIO):
                            def __init__(self, name, data):
                                super().__init__(data)
                                self.name = name
                        active_file = MockFile(os.path.basename(file_param), f.read())
                        st.info(f"📁 Auto-loaded file from parameter: `{active_file.name}`")
                except Exception:
                    pass

    if active_file:
        st.divider()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.pdf")
            output_path = os.path.join(tmpdir, "compressed.pdf")

            if hasattr(active_file, "seek"):
                active_file.seek(0)
            with open(input_path, "wb") as f:
                f.write(active_file.read())

            pwd = pdf_password.strip() if pdf_password.strip() else None

            # -----------------------------------------------------
            # Analysis & Hybrid Decision Step
            # -----------------------------------------------------
            try:
                metrics = analyze_pdf(input_path, password=pwd)
                strategy, decision_mode, rag_details = decide_strategy(metrics, rag_index, knowledge)

                # Display Metrics & Strategy
                st.subheader("📊 Document Analysis & Decision Strategy")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Original Size", f"{metrics['file_size_kb']:.1f} KB")
                m2.metric("Page Count", metrics['page_count'])
                m3.metric("Image Count", metrics['image_count'])
                m4.metric("Text Chars", metrics['text_length'])
                m5.metric("Scanned Doc", "Yes" if metrics['is_scanned'] else "No")

                badge_color = "🟢" if decision_mode == "RULE-BASED" else "🧠"
                st.markdown(f"### {badge_color} Engine Mode: **{decision_mode}**")
                st.info(f"**Recommended Strategy**: {strategy}")

                # RAG Match Details Expander
                with st.expander("🔍 Inspect RAG Vector Search & Candidate Matches"):
                    st.write(f"**Decision Mode:** `{decision_mode}`")
                    if rag_details:
                        for idx, match in enumerate(rag_details, 1):
                            st.markdown(f"**Match [{idx}]**: {match.get('text', '')}")
                            if "similarity" in match:
                                st.progress(min(max(match["similarity"], 0.0), 1.0))
                                st.caption(f"Similarity Score: {match['similarity']*100:.1f}% | Distance: {match.get('distance', 0.0):.4f}")

                if st.button("🚀 Compress PDF", type="primary", use_container_width=True):
                    with st.spinner("Processing PDF compression pipeline..."):
                        start_t = time.time()
                        try:
                            stats = compress_pdf(input_path, output_path, level=selected_level, password=pwd, strip_metadata=strip_metadata_toggle)
                            elapsed = time.time() - start_t
                            
                            st.success(f"✅ Compression complete in {elapsed:.2f}s!")

                            # Metrics Results
                            res1, res2, res3, res4, res5 = st.columns(5)
                            res1.metric("Original Size", f"{stats['original_size_kb']:.1f} KB")
                            res2.metric("Compressed Size", f"{stats['compressed_size_kb']:.1f} KB")
                            res3.metric("Size Reduction", f"{stats['reduction_percent']:.1f}%")
                            res4.metric("PSNR Quality", f"{stats['psnr_db']} dB")
                            res5.metric("SSIM Similarity", f"{stats['ssim_percent']}%")

                            # Download Button
                            with open(output_path, "rb") as pdf_file:
                                pdf_bytes = pdf_file.read()
                                
                            st.download_button(
                                label="⬇️ Download Compressed PDF",
                                data=pdf_bytes,
                                file_name=f"compressed_{active_file.name}",
                                mime="application/pdf",
                                use_container_width=True
                            )

                            # Visual Preview
                            st.divider()
                            st.subheader("👁️ Visual Before vs. After Page Preview (Page 1)")
                            
                            orig_img = render_page_preview(input_path, page_num=0, password=pwd)
                            comp_img = render_page_preview(output_path, page_num=0)

                            if orig_img and comp_img:
                                prev_col1, prev_col2 = st.columns(2)
                                with prev_col1:
                                    st.caption("📷 Original Document (Page 1)")
                                    st.image(orig_img, use_column_width=True)
                                with prev_col2:
                                    st.caption("✨ Compressed Document (Page 1)")
                                    st.image(comp_img, use_column_width=True)

                        except Exception as e:
                            st.error(f"❌ Compression failed: {e}")
            except Exception as ex:
                st.error(f"❌ Failed to analyze PDF: {ex}")

# =========================================================
# TAB 2: Batch PDF Compression
# =========================================================
with tab_batch:
    st.subheader("📁 Batch PDF Compression")
    st.write("Upload multiple PDF files to compress them in batch and download a single ZIP archive.")

    batch_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="batch_pdf"
    )

    batch_level = st.selectbox(
        "Batch Compression Level",
        ["Medium (Recommended)", "Low (Best Quality)", "High (Smallest Size)"],
        key="batch_level"
    )
    b_level = level_key_map[batch_level]

    if batch_files and st.button("📦 Compress All PDFs", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        compressed_results = []
        zip_buffer = io.BytesIO()

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, file in enumerate(batch_files):
                    status_text.text(f"Processing ({idx+1}/{len(batch_files)}): {file.name}")
                    in_path = os.path.join(tmpdir, f"in_{idx}.pdf")
                    out_path = os.path.join(tmpdir, f"out_{idx}.pdf")

                    file.seek(0)
                    with open(in_path, "wb") as f:
                        f.write(file.read())

                    try:
                        stats = compress_pdf(in_path, out_path, level=b_level)
                        zip_file.write(out_path, arcname=f"compressed_{file.name}")
                        compressed_results.append({
                            "name": file.name,
                            "original_kb": stats["original_size_kb"],
                            "compressed_kb": stats["compressed_size_kb"],
                            "reduction": stats["reduction_percent"],
                            "ssim": stats["ssim_percent"]
                        })
                    except Exception as e:
                        st.error(f"Failed to compress {file.name}: {e}")

                    progress_bar.progress((idx + 1) / len(batch_files))

        status_text.text("✅ Batch compression complete!")
        st.success(f"Successfully processed {len(compressed_results)} PDF files!")
        st.table(compressed_results)

        zip_buffer.seek(0)
        st.download_button(
            label="⬇️ Download All Compressed PDFs (.zip)",
            data=zip_buffer,
            file_name="compressed_pdf_batch.zip",
            mime="application/zip",
            use_container_width=True
        )

# =========================================================
# TAB 3: 💬 Ask PDF (RAG Assistant)
# =========================================================
with tab_ask_pdf:
    st.subheader("💬 Ask PDF — Semantic RAG Assistant")
    st.write("Perform RAG vector search and natural language synthesis over the text content of any uploaded PDF.")

    rag_pdf_file = st.file_uploader("Upload a PDF to query", type=["pdf"], key="rag_pdf_uploader")
    target_pdf = rag_pdf_file if rag_pdf_file else active_file

    if target_pdf:
        st.info(f"📄 Target Document: `{target_pdf.name}`")
        user_query = st.text_input("Ask a question about the PDF contents:", placeholder="e.g., What is the summary of this document?")
        
        if user_query and st.button("🔍 Search PDF Content"):
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_pdf_path = os.path.join(tmpdir, "rag_target.pdf")
                if hasattr(target_pdf, "seek"):
                    target_pdf.seek(0)
                with open(tmp_pdf_path, "wb") as f:
                    f.write(target_pdf.read())

                with st.spinner("Building vector index and synthesizing answer..."):
                    results = query_pdf_content(tmp_pdf_path, user_query, top_k=4)
                    synthesized_answer = synthesize_rag_answer(user_query, results)

                if not results:
                    st.warning("⚠️ No relevant text passages found in this document.")
                else:
                    st.markdown("### 🧠 Synthesized RAG Answer")
                    st.success(synthesized_answer)

                    st.markdown("### 🔍 Evidence Passages")
                    for idx, match in enumerate(results, 1):
                        st.markdown(f"#### Match [{idx}] — Page {match['page']}")
                        st.progress(min(max(match["similarity"], 0.0), 1.0))
                        st.caption(f"Relevance Score: {match['similarity']*100:.1f}% | Vector Distance: {match['distance']:.4f}")
                        st.text_area(f"Passage Text (Page {match['page']})", value=match["text"], height=120, key=f"rag_res_{idx}")
    else:
        st.warning("Please upload a PDF file above to query its content.")

# =========================================================
# TAB 4: Architecture & RAG Details
# =========================================================
with tab_about:
    st.subheader("🏗️ Architecture & RAG System Overview")
    st.markdown("""
    This application features an enterprise-grade **Hybrid RAG System**:
    
    1. **PyMuPDF / Tesseract OCR Inspection**: Analyzes page density, image streams, font structures, and runs Tesseract OCR fallback for scanned pages.
    2. **Deterministic Rule Engine**: Instantly matches confident heuristics for clear document cases.
    3. **Strategy RAG Engine**: Vector semantic search against a FAISS index of PDF optimization strategies.
    4. **LLM RAG Synthesizer**: Page-level windowed chunking, FAISS vector indexing, and synthesized answer generation.
    5. **Visual Quality Metrics Engine**: Calculates PSNR (dB) and SSIM (%) quality retention scores.
    6. **Safe Rebuild Pipeline**: PyMuPDF stream deflating paired with Ghostscript binary downsampling.
    """)
