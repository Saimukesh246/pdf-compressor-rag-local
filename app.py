from analyzer.pdf_analyzer import analyze_pdf
from rag.indexer import build_index
from rag.retriever import retrieve
from compressor.pdf_optimizer import compress_pdf

with open("data/knowledge_base.txt") as f:
    knowledge = f.readlines()

index, _ = build_index(knowledge)

from decision.hybrid_decider import decide_strategy

metrics = analyze_pdf(input_path)

strategy, decision_type = decide_strategy(metrics, index, knowledge)


strategy = retrieve(pdf_type, index, knowledge)

print("PDF Type:", pdf_type)
print("Chosen Strategy:", strategy)

compress_pdf(pdf_path, "compressed.pdf")
print("Compression complete!")
