from decision.rule_engine import rule_based_strategy
from rag.retriever import retrieve

def decide_strategy(metrics, rag_index, knowledge_base):
    """
    Decides the optimal PDF compression strategy using a hybrid approach:
    First evaluates rule-based heuristics. If confidence is low, falls back to RAG vector search.
    
    Args:
        metrics (dict): Output from analyze_pdf
        rag_index: FAISS index
        knowledge_base (list): List of knowledge base lines/documents
        
    Returns:
        tuple: (strategy_text, decision_mode, rag_details)
               where rag_details is a list of top matched candidates with similarity scores.
    """
    image_count = metrics.get("image_count", 0)
    text_length = metrics.get("text_length", 0)
    is_scanned = metrics.get("is_scanned", False)
    page_count = metrics.get("page_count", 1)

    strategy, confidence = rule_based_strategy(
        image_count=image_count,
        text_length=text_length,
        is_scanned=is_scanned,
        page_count=page_count
    )

    if strategy is not None and confidence >= 0.7:
        rule_details = [{
            "text": strategy,
            "confidence": confidence,
            "similarity": confidence,
            "rule": "Rule-based heuristic matched with high confidence"
        }]
        return strategy, "RULE-BASED", rule_details

    # RAG fallback for ambiguous/mixed documents
    if is_scanned:
        query = "Scanned PDF with low or extracted text"
    elif image_count > text_length / 100:
        query = "Image-heavy PDF document with embedded pictures"
    elif text_length > 5000:
        query = "Text-heavy PDF document with font optimization"
    else:
        query = f"Mixed content PDF with {image_count} images and {text_length} text characters"

    rag_matches = retrieve(query, rag_index, knowledge_base, top_k=3, return_details=True)
    top_strategy = rag_matches[0]["text"] if rag_matches else "Default compression strategy"

    return top_strategy, "RAG", rag_matches
