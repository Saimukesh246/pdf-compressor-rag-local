import faiss
from rag.embedder import embed

def build_index(knowledge):
    vectors = embed(knowledge)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index, vectors
