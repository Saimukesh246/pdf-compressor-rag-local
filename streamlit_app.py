import streamlit as st
import os
import tempfile
import time
import subprocess
import shutil

from analyzer.pdf_analyzer import analyze_pdf
from decision.rule_engine import rule_based_strategy
from rag.indexer import build_index
from rag.retriever import retrieve
from compressor.pdf_optimizer import safe_optimize_pdf


# =========================================================
# Session State Init (IMPORTANT)
# =========================================================
if "compressed_bytes" not in st.session_state:
    st.session_state.compressed_bytes = None
    st.session_state.stats = None


# =========================================================
# Find Ghostscript (Windows-safe)
# =========================================================
def find_ghostscript():
    for exe in ["gswin64c.exe", "gs.exe"]:
        path = shutil.which(exe)
        if path:
            return path

    common_dirs = [
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs"
    ]

    for base in common_dirs:
        if os.path.exists(base):
            for folder in os.listdir(base):
                exe_path = os.path.join(base, folder, "bin", "gswin64c.exe")
                if os.path.exists(exe_path):
                    return exe_path

    return None


GS_PATH = find_ghostscript()


# =========================================================
# Ghostscript Compression
# =========================================================
def compress_with_ghostscript(input_pdf, output_pdf, level):
    if not GS_PATH:
        raise RuntimeError("Ghostscript not found")

    cmd = [
        GS_PATH,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{level}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]

    subprocess.run(cmd, check=True)


# =========================================================
# Load RAG (cached)
# =========================================================
@st.cache_resource
def load_rag():
    with open("data/knowledge_base.txt") as f:
        knowledge = [line.strip() for line in f if line.strip()]
    index, _ = build_index(knowledge)
    return knowledge, index


knowledge, rag_index = load_rag()


# =========================================================
# Streamlit UI
# =========================================================
st.set_page_config(
    page_title="PDF Compressor (Hybrid Safe)",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF Compressor — Hybrid & Safe")
st.caption("⚡ Rules → 🧠 RAG → 🛡️ Ghostscript (no black images)")

if not GS_PATH:
    st.error(
        "❌ Ghostscript not found.\n\n"
        "Please install Ghostscript from:\n"
        "https://www.ghostscript.com/releases/gsdnld.html"
    )
    st.stop()

st.success(f"✅ Ghostscript detected:\n{GS_PATH}")
st.divider()


# =========================================================
# Compression Level
# =========================================================
compression_level = st.selectbox(
    "Compression Level",
    [
        "Low (Best Quality)",
        "Medium (Recommended)",
        "High (Smallest Size)"
    ]
)

GS_LEVEL_MAP = {
    "Low (Best Quality)": "printer",
    "Medium (Recommended)": "ebook",
    "High (Smallest Size)": "screen"
}

gs_level = GS_LEVEL_MAP[compression_level]


# =========================================================
# Upload PDF
# =========================================================
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, "input.pdf")
        clean_pdf = os.path.join(tmpdir, "clean.pdf")
        output_pdf = os.path.join(tmpdir, "compressed.pdf")

        with open(input_pdf, "wb") as f:
            f.write(uploaded_file.read())

        original_size = os.path.getsize(input_pdf) / 1024  # KB

        if st.button("🔽 Compress PDF"):
            start_time = time.time()

            try:
                # ---------------------------------
                # Analyze PDF
                # ---------------------------------
                metrics = analyze_pdf(input_pdf)
                image_count = metrics["image_count"]
                text_length = metrics["text_length"]

                # ---------------------------------
                # Rule-based decision
                # ---------------------------------
                strategy, confidence = rule_based_strategy(
                    image_count, text_length
                )

                # ---------------------------------
                # RAG fallback
                # ---------------------------------
                if strategy is None or confidence < 0.7:
                    decision_mode = "RAG"
                    query = (
                        "Image-heavy PDF"
                        if image_count > text_length
                        else "Text-heavy PDF"
                    )
                    strategy = retrieve(query, rag_index, knowledge)
                else:
                    decision_mode = "RULE-BASED"

                # ---------------------------------
                # Safe Compression
                # ---------------------------------
                safe_optimize_pdf(input_pdf, clean_pdf)
                compress_with_ghostscript(clean_pdf, output_pdf, gs_level)

                compressed_size = os.path.getsize(output_pdf) / 1024
                elapsed = time.time() - start_time

                # ---------------------------------
                # Store result in memory (IMPORTANT)
                # ---------------------------------
                with open(output_pdf, "rb") as f:
                    st.session_state.compressed_bytes = f.read()

                st.session_state.stats = {
                    "decision_mode": decision_mode,
                    "strategy": strategy,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "elapsed": elapsed
                }

                st.success("✅ Compression completed successfully!")

            except Exception as e:
                st.error(f"❌ Compression failed: {e}")


# =========================================================
# Results + Download (SAFE & STABLE)
# =========================================================
if st.session_state.compressed_bytes and st.session_state.stats:
    stats = st.session_state.stats

    st.divider()
    st.subheader("🧠 Decision Engine")
    st.write(f"**Decision Mode:** {stats['decision_mode']}")
    st.write(f"**Strategy:** {stats['strategy']}")

    st.subheader("📊 Compression Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Original Size (KB)", f"{stats['original_size']:.2f}")
    col2.metric("Compressed Size (KB)", f"{stats['compressed_size']:.2f}")

    reduction = (
        (stats["original_size"] - stats["compressed_size"])
        / stats["original_size"]
        * 100
    )
    col3.metric("Reduction (%)", f"{reduction:.2f}")

    st.caption(f"⏱️ Processing time: {stats['elapsed']:.2f} seconds")

    st.download_button(
        label="⬇️ Download Compressed PDF",
        data=st.session_state.compressed_bytes,
        file_name="compressed.pdf",
        mime="application/pdf"
    )
