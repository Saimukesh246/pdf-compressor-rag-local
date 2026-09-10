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
    page_icon="📄",
    layout="wide"
)

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
# Streamlit Header
# =========================================================
st.title("📄 PDF Compressor & RAG Assistant")
st.caption("⚡ Rule Engine → 🧠 Vector RAG Fallback → 💬 PDF Semantic RAG Chat → 🛡️ Ghostscript Safe Rebuild")

if not GS_PATH:
    st.error(
        "❌ Ghostscript not found on host system.\n\n"
        "Please install Ghostscript from: https://www.ghostscript.com/releases/gsdnld.html"
    )
    st.stop()

st.success(f"✅ Ghostscript Engine Active: `{GS_PATH}`")

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

            # -----------------------------------------------------
            # Analysis & Hybrid Decision Step
            # -----------------------------------------------------
            metrics = analyze_pdf(input_path)
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
                        stats = compress_pdf(input_path, output_path, level=selected_level)
                        elapsed = time.time() - start_t
                        
                        st.success(f"✅ Compression complete in {elapsed:.2f}s!")

                        # Metrics Results
                        res1, res2, res3 = st.columns(3)
                        res1.metric("Original Size", f"{stats['original_size_kb']:.2f} KB")
                        res2.metric("Compressed Size", f"{stats['compressed_size_kb']:.2f} KB")
                        res3.metric("Size Reduction", f"{stats['reduction_percent']:.2f}%")

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

                        # Save persistent output copy
                        try:
                            with open("compressed_output.pdf", "wb") as pf:
                                pf.write(pdf_bytes)
                        except Exception:
                            pass

                        # -----------------------------------------------------
                        # Visual Before vs. After Page Preview
                        # -----------------------------------------------------
                        st.divider()
                        st.subheader("👁️ Visual Before vs. After Page Preview")
                        
                        orig_img = render_page_preview(input_path, page_num=0)
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
                            "reduction": stats["reduction_percent"]
                        })
                    except Exception as e:
                        st.error(f"Failed to compress {file.name}: {e}")

                    progress_bar.progress((idx + 1) / len(batch_files))

        status_text.text("✅ Batch compression complete!")
        st.success(f"Successfully processed {len(compressed_results)} PDF files!")

        # Results Summary Table
        st.table(compressed_results)

        # Download ZIP
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
    st.subheader("💬 Ask PDF — Semantic RAG Search")
    st.write("Perform RAG vector search over the text content of any uploaded PDF file using FAISS vector indexing.")

    rag_pdf_file = st.file_uploader("Upload a PDF to query", type=["pdf"], key="rag_pdf_uploader")
    
    # Allow fallback to active file from tab 1 if available
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

                with st.spinner("Building vector index and querying PDF..."):
                    results = query_pdf_content(tmp_pdf_path, user_query, top_k=4)

                if not results:
                    st.warning("⚠️ No relevant text passages found in this document (or document contains no extractable text).")
                else:
                    st.success(f"Found {len(results)} relevant passages!")
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
    This application features a multi-tiered **Hybrid RAG System**:
    
    1. **PyMuPDF Content Inspection**: Analyzes page density, image streams, font structures, and text lengths.
    2. **Deterministic Rule Engine**: Instantly matches confident heuristics (e.g. Scanned PDFs, text-heavy PDFs).
    3. **Strategy RAG Engine**: For ambiguous mixed-media documents, uses `sentence-transformers` vector search (`all-MiniLM-L6-v2`) against a FAISS vector index of PDF optimization strategies.
    4. **Document Content RAG Assistant**: Splits PDF text into overlapping chunks, computes embeddings, builds in-memory FAISS indices, and retrieves exact page passages matching user search prompts.
    5. **PyMuPDF Object Stream Pre-Cleaning**: Removes unused objects (`garbage=4`) and cleans stream tables safely.
    6. **Ghostscript Rebuild**: Re-encodes and downsamples color channels using `pdfwrite` without corrupting transparency or producing black images.
    """)
