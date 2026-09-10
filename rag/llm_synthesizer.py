import os

def synthesize_rag_answer(query, passages):
    """
    Synthesizes a clear, concise natural language answer based on retrieved PDF passages.
    Uses OpenAI API if OPENAI_API_KEY environment variable is set, otherwise provides structured text synthesis.
    
    Args:
        query (str): The search query / prompt
        passages (list): List of retrieved passage dictionaries (with 'page', 'text', 'similarity')
        
    Returns:
        str: Synthesized answer text.
    """
    if not passages:
        return "No relevant passages were found in the document to answer your query."

    context_str = "\n\n".join([f"[Page {p['page']} | Relevance: {p['similarity']*100:.1f}%]: {p['text']}" for p in passages])

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import urllib.request
            import json

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            prompt = (
                f"You are an expert PDF RAG Assistant. Based strictly on the following context extracted from the PDF, "
                f"answer the user query concisely and cite the relevant page numbers.\n\n"
                f"Context:\n{context_str}\n\n"
                f"User Query: {query}\n"
                f"Answer:"
            )
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    # Structured local synthesis fallback
    top_match = passages[0]
    bullets = "\n".join([f"• Page {p['page']}: \"{p['text'][:120]}...\"" for p in passages[:3]])
    
    synthesis = (
        f"Based on the highest matching passage from Page {top_match['page']} (Relevance Score: {top_match['similarity']*100:.1f}%):\n\n"
        f"\"{top_match['text']}\"\n\n"
        f"Key Evidence Passages:\n{bullets}"
    )
    return synthesis
