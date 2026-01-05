from rag.embedder import embed

def retrieve(query, index, knowledge):
    q_vec = embed([query])
    _, idx = index.search(q_vec, 1)
    return knowledge[idx[0][0]]
