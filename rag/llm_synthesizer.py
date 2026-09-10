import os
from rag.pdf_rag import extract_pdf_chunks

def synthesize_rag_answer(query, passages):
    """
    Synthesizes a clear, concise natural language answer based on retrieved PDF passages.
    Uses OpenAI API if OPENAI_API_KEY environment variable is set, otherwise provides structured text synthesis.
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


def generate_pdf_mindmap(pdf_path):
    """
    Generates an executive summary and a Mermaid.js Mindmap representation of a PDF document.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Containing 'summary_text' and 'mermaid_code'.
    """
    chunks = extract_pdf_chunks(pdf_path, max_chars=500)
    if not chunks:
        return {
            "summary_text": "No extractable text found in this PDF document.",
            "mermaid_code": "mindmap\n  root((Empty Document))"
        }

    # Extract key sentences from initial chunks for local mindmap building
    topics = []
    for c in chunks[:5]:
        text_snippet = c["text"].replace("\n", " ").strip()
        words = [w.strip(".,;:()") for w in text_snippet.split() if len(w) > 4]
        if words:
            topics.append((c["page"], words[:3]))

    summary_bullets = [f"• Page {c['page']}: {c['text'][:140]}..." for c in chunks[:4]]
    summary_text = f"Executive Document Overview ({len(chunks)} text sections extracted):\n\n" + "\n".join(summary_bullets)

    # Construct Mermaid Mindmap string
    mermaid_lines = ["mindmap", "  root((PDF Overview))"]
    for idx, (page_num, key_words) in enumerate(topics, 1):
        topic_name = " ".join(key_words).title() if key_words else f"Section {idx}"
        mermaid_lines.append(f"    Page {page_num}: {topic_name}")
        for w in key_words:
            mermaid_lines.append(f"      {w.capitalize()}")

    mermaid_code = "\n".join(mermaid_lines)

    return {
        "summary_text": summary_text,
        "mermaid_code": mermaid_code
    }
