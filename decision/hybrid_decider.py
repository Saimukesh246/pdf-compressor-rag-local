from decision.rule_engine import rule_based_strategy
from rag.retriever import retrieve

CONFIDENCE_THRESHOLD = 0.7

def decide_strategy(metrics, rag_index, knowledge):
    # Step 1: Fast rule-based decision
    strategy, confidence = rule_based_strategy(
        metrics["image_count"],
        metrics["text_length"]
    )

    if confidence >= CONFIDENCE_THRESHOLD:
        return strategy, "RULE-BASED"

    # Step 2: Fall back to RAG
    query = "Image-heavy PDF" if metrics["image_count"] > metrics["text_length"] else "Text-heavy PDF"
    strategy = retrieve(query, rag_index, knowledge)
    return strategy, "RAG"
