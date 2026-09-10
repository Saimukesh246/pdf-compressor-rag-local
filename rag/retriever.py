import numpy as np
from rag.embedder import embed

def retrieve(query, index, knowledge, top_k=1, return_details=False):
    """
    Retrieves top_k nearest strategy documents from the FAISS index for a given query.
    
    Args:
        query (str): The search query text
        index (faiss.Index): FAISS vector index
        knowledge (list): Knowledge base strings
        top_k (int): Number of top matches to retrieve
        return_details (bool): If True, returns detailed match dicts including distances and similarity scores.
        
    Returns:
        str or list: Top match string (if return_details=False and top_k=1) or list of match dicts.
    """
    q_vec = embed([query])
    distances, indices = index.search(q_vec, min(top_k, len(knowledge)))

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= 0 and idx < len(knowledge):
            text = knowledge[idx]
            # Convert L2 distance to percentage similarity score
            similarity = float(1.0 / (1.0 + float(dist)))
            results.append({
                "text": text,
                "distance": float(dist),
                "similarity": similarity,
                "index": int(idx)
            })

    if not return_details:
        return results[0]["text"] if results else ""

    return results
