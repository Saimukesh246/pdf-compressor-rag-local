import os
import sys
import argparse
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from analyzer.pdf_analyzer import analyze_pdf
from rag.indexer import build_index
from rag.pdf_rag import query_pdf_content
from rag.llm_synthesizer import synthesize_rag_answer
from decision.hybrid_decider import decide_strategy
from compressor.pdf_optimizer import compress_pdf, find_ghostscript

def load_rag_knowledge():
    kb_path = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.txt")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            knowledge = [line.strip() for line in f if line.strip()]
    else:
        knowledge = [
            "Image-heavy PDF: Downscale images to 150 DPI and apply lossy JPEG compression.",
            "Text-heavy PDF: Remove unused font subsets and optimize object streams.",
            "Scanned PDF: Downsample background images and retain text layers."
        ]
    index, _ = build_index(knowledge)
    return knowledge, index

def process_single_pdf(input_path, output_path, level, knowledge, rag_index, password=None, strip_metadata=False):
    print(f"\nProcessing: {input_path}")
    start_time = time.time()
    
    # 1. Analyze PDF
    metrics = analyze_pdf(input_path, password=password)
    print(f"  * Pages: {metrics['page_count']} | Images: {metrics['image_count']} | Text chars: {metrics['text_length']} | Scanned: {metrics['is_scanned']}")
    print(f"  * Original Size: {metrics['file_size_kb']:.2f} KB")

    # 2. Hybrid Decision Strategy
    strategy, decision_mode, rag_details = decide_strategy(metrics, rag_index, knowledge)
    print(f"  * Decision Mode: [{decision_mode}]")
    print(f"  * Strategy: {strategy.replace(chr(10), ' | ')}")

    if decision_mode == "RAG" and rag_details:
        print("  * Top RAG Matches:")
        for idx, match in enumerate(rag_details, 1):
            print(f"    [{idx}] (Similarity: {match['similarity']*100:.1f}%, Distance: {match['distance']:.3f}) {match['text'].replace(chr(10), ' ')}")

    # 3. Compress PDF
    stats = compress_pdf(input_path, output_path, level=level, password=password, strip_metadata=strip_metadata)
    elapsed = time.time() - start_time

    print(f"  [SUCCESS] Compressed Size: {stats['compressed_size_kb']:.2f} KB")
    print(f"  [SUCCESS] Size Reduction: {stats['reduction_percent']:.2f}%")
    print(f"  [SUCCESS] Quality Metrics -> PSNR: {stats['psnr_db']} dB | SSIM: {stats['ssim_percent']}%")
    print(f"  [SUCCESS] Time Elapsed: {elapsed:.2f}s")
    print(f"  [SUCCESS] Output saved to: {output_path}")

def handle_pdf_ask_query(pdf_path, query):
    print(f"\n💬 Querying PDF: {pdf_path}")
    print(f"❓ Prompt: \"{query}\"")
    results = query_pdf_content(pdf_path, query, top_k=3)
    if not results:
        print("⚠️ No text passages found in PDF or failed to build RAG index.")
        return

    synthesized_answer = synthesize_rag_answer(query, results)
    print("\n🧠 Synthesized RAG Answer:")
    print(synthesized_answer)

    print("\n🔍 Evidence Passages:")
    for idx, match in enumerate(results, 1):
        print(f"\n--- Match [{idx}] | Page {match['page']} | Similarity: {match['similarity']*100:.1f}% ---")
        print(match['text'])

def main():
    parser = argparse.ArgumentParser(description="PDF Compressor & RAG Assistant CLI")
    parser.add_argument("-i", "--input", required=True, help="Input PDF file or directory path")
    parser.add_argument("-o", "--output", help="Output PDF file or directory path (default: <input>_compressed.pdf)")
    parser.add_argument("-l", "--level", choices=["low", "medium", "high"], default="medium", help="Compression level (default: medium)")
    parser.add_argument("-p", "--password", help="Password for encrypted PDF files")
    parser.add_argument("--strip-metadata", action="store_true", help="Purge PDF title, author, and annotations")
    parser.add_argument("-b", "--batch", action="store_true", help="Process directory of PDF files in batch mode")
    parser.add_argument("-a", "--ask", help="Ask a semantic question about the PDF document content using RAG")

    args = parser.parse_args()

    if args.ask:
        if not os.path.isfile(args.input):
            print(f"Error: PDF file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        handle_pdf_ask_query(args.input, args.ask)
        return

    gs_path = find_ghostscript()
    if not gs_path:
        print("Error: Ghostscript executable not found. Please install Ghostscript.", file=sys.stderr)
        sys.exit(1)

    print("Initializing RAG Knowledge Base...")
    knowledge, rag_index = load_rag_knowledge()

    if args.batch or os.path.isdir(args.input):
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a valid directory for batch processing.", file=sys.stderr)
            sys.exit(1)

        output_dir = args.output if args.output else os.path.join(args.input, "compressed_output")
        os.makedirs(output_dir, exist_ok=True)

        pdf_files = [f for f in os.listdir(args.input) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"Warning: No PDF files found in directory {args.input}")
            return

        print(f"Batch processing {len(pdf_files)} PDF files into directory: {output_dir}")
        for pdf_file in pdf_files:
            in_file = os.path.join(args.input, pdf_file)
            out_file = os.path.join(output_dir, f"compressed_{pdf_file}")
            try:
                process_single_pdf(in_file, out_file, args.level, knowledge, rag_index, password=args.password, strip_metadata=args.strip_metadata)
            except Exception as e:
                print(f"Failed to compress {pdf_file}: {e}")

    else:
        if not os.path.isfile(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        output_path = args.output
        if not output_path:
            base, ext = os.path.splitext(args.input)
            output_path = f"{base}_compressed{ext}"

        process_single_pdf(args.input, output_path, args.level, knowledge, rag_index, password=args.password, strip_metadata=args.strip_metadata)

if __name__ == "__main__":
    main()
