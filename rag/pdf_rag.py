import fitz
import faiss
import numpy as np
from rag.embedder import embed

def extract_pdf_chunks(pdf_path, max_chars=400, overlap=80):
    """
    Extracts text chunks from a PDF file with page metadata.
    
    Args:
        pdf_path (str): Path to the PDF file
        max_chars (int): Maximum character length per chunk
        overlap (int): Overlap characters between chunks
        
    Returns:
        list of dict: List containing chunk dictionaries with keys ('text', 'page', 'chunk_id')
    """
    doc = fitz.open(pdf_path)
    chunks = []
    chunk_counter = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if not text:
            continue

        # Split text into overlapping windows
        start = 0
        while start < len(text):
            end = start + max_chars
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_counter,
                    "page": page_num + 1,
                    "text": chunk_text
                })
                chunk_counter += 1
            start += (max_chars - overlap)

    doc.close()
    return chunks


def build_pdf_index(pdf_path):
    """
    Extracts text chunks from a PDF and builds an in-memory FAISS vector index.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        tuple: (faiss_index, chunks_list)
    """
    chunks = extract_pdf_chunks(pdf_path)
    if not chunks:
        return None, []

    texts = [c["text"] for c in chunks]
    vectors = embed(texts)
    
    # FAISS L2 flat index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    
    return index, chunks


def query_pdf_content(pdf_or_index, query, top_k=3):
    """
    Queries a PDF document semantically using FAISS vector search.
    
    Args:
        pdf_or_index (str or tuple): Path to PDF or pre-built (index, chunks) tuple.
        query (str): The search prompt / query string
        top_k (int): Number of top matches to retrieve
        
    Returns:
        list of dict: Retrieved passages with page numbers, text, and similarity scores.
    """
    if isinstance(pdf_or_index, str):
        index, chunks = build_pdf_index(pdf_or_index)
    else:
        index, chunks = pdf_or_index

    if not index or not chunks:
        return []

    q_vec = embed([query])
    distances, indices = index.search(q_vec, min(top_k, len(chunks)))

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= 0 and idx < len(chunks):
            chunk = chunks[idx]
            similarity = float(1.0 / (1.0 + float(dist)))
            results.append({
                "chunk_id": chunk["chunk_id"],
                "page": chunk["page"],
                "text": chunk["text"],
                "distance": float(dist),
                "similarity": similarity
            })

    return results
