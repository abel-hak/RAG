"""RAG: retrieve relevant chunks and generate answer with citations."""
from app_config import (
    GEMINI_API_KEY,
    GEMINI_CHAT_MODEL,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    OLLAMA_CHAT_MODEL,
    USE_GEMINI,
    USE_OLLAMA,
)
from store import query as store_query


SYSTEM_PROMPT = """You answer questions using only the provided context. If the context does not contain enough information, say so. Always cite the source (e.g. "According to [source]..."). Do not make up facts or sources."""


def _chat_gemini(user_message: str) -> str:
    import time
    from google.genai import Client
    from google.genai import types
    client = Client(api_key=GEMINI_API_KEY)
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=GEMINI_CHAT_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )
            return (response.text or "").strip()
        except Exception as e:
            err_msg = str(e).upper()
            if attempt == 0 and ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "QUOTA" in err_msg):
                time.sleep(50)
                continue
            raise
    return ""


def _chat_openai(user_message: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def _chat_ollama(user_message: str) -> str:
    import ollama
    resp = ollama.chat(
        model=OLLAMA_CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return (resp.get("message", {}).get("content") or "").strip()


def rag_query(question: str, top_k: int = 5) -> tuple[str, list[dict]]:
    """
    Run RAG: retrieve chunks, build context, call LLM. Returns (answer, list of sources).
    """
    if not USE_GEMINI and not USE_OLLAMA and not OPENAI_API_KEY:
        raise ValueError("Set GEMINI_API_KEY+USE_GEMINI=true, or USE_OLLAMA=true, or OPENAI_API_KEY in .env")

    chunks = store_query(question, top_k=top_k)
    if not chunks:
        return (
            "No documents have been indexed yet. Add PDFs or markdown files to the `data` folder and run **Index documents** in the sidebar.",
            [],
        )

    context = "\n\n---\n\n".join(
        f'[Source: {c["source"]}]\n{c["content"]}' for c in chunks
    )
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    if USE_GEMINI:
        answer = _chat_gemini(user_message)
    elif USE_OLLAMA:
        answer = _chat_ollama(user_message)
    else:
        answer = _chat_openai(user_message)

    sources = [{"source": c["source"], "metadata": c.get("metadata", {})} for c in chunks]
    return answer, sources
