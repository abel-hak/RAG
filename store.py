"""Chroma vector store: embed chunks and run similarity search."""
import hashlib
from typing import Any

import chromadb
from chromadb.config import Settings

from app_config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    GEMINI_EMBED_MODEL,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OLLAMA_EMBED_MODEL,
    TOP_K,
    USE_GEMINI,
    USE_OLLAMA,
)
from ingest import Document
from chunk import chunk_document


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    from google.genai import Client
    client = Client(api_key=GEMINI_API_KEY)
    contents = texts[0] if len(texts) == 1 else texts
    result = client.models.embed_content(model=GEMINI_EMBED_MODEL, contents=contents)
    embs = result.embeddings
    if not isinstance(embs, list):
        embs = [embs]
    out = []
    for e in embs:
        vec = e.values if hasattr(e, "values") else e
        out.append(list(vec))
    return out


def _embed_openai(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    out = client.embeddings.create(input=texts, model=OPENAI_EMBEDDING_MODEL)
    return [d.embedding for d in out.data]


def _embed_ollama(texts: list[str]) -> list[list[float]]:
    import ollama
    out = []
    for t in texts:
        r = ollama.embeddings(model=OLLAMA_EMBED_MODEL, prompt=t)
        out.append(r["embedding"])
    return out


def _embed(texts: list[str]) -> list[list[float]]:
    if USE_GEMINI:
        return _embed_gemini(texts)
    if USE_OLLAMA:
        return _embed_ollama(texts)
    if not OPENAI_API_KEY:
        raise ValueError("Set GEMINI_API_KEY + USE_GEMINI=true, or USE_OLLAMA=true, or OPENAI_API_KEY in .env")
    return _embed_openai(texts)


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))


def _make_id(source: str, chunk_index: int, text_preview: str) -> str:
    raw = f"{source}:{chunk_index}:{text_preview[:50]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def add_documents(docs: list[Document], collection_name: str = COLLECTION_NAME, clear_first: bool = True) -> int:
    """Chunk documents, embed, and add to Chroma. Returns number of chunks added."""
    chroma = get_chroma_client()
    if clear_first:
        try:
            chroma.delete_collection(name=collection_name)
        except Exception:
            pass
    coll = chroma.get_or_create_collection(name=collection_name, metadata={"description": "RAG knowledge base"})

    ids: list[str] = []
    texts: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for doc in docs:
        for i, (text, meta) in enumerate(chunk_document(doc)):
            doc_id = _make_id(doc.source, i, text)
            ids.append(doc_id)
            texts.append(text)
            clean_meta = {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in meta.items()}
            metadatas.append(clean_meta)

    if not texts:
        return 0

    batch_size = 1 if USE_OLLAMA else 100
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_embeddings.extend(_embed(batch))

    coll.add(ids=ids, embeddings=all_embeddings, documents=texts, metadatas=metadatas)
    return len(ids)


def query(
    question: str,
    top_k: int = TOP_K,
    collection_name: str = COLLECTION_NAME,
) -> list[dict[str, Any]]:
    """Return top_k relevant chunks with content and source."""
    if not USE_GEMINI and not USE_OLLAMA and not OPENAI_API_KEY:
        raise ValueError("Set GEMINI_API_KEY+USE_GEMINI=true, or USE_OLLAMA=true, or OPENAI_API_KEY in .env")
    chroma = get_chroma_client()
    try:
        coll = chroma.get_collection(name=collection_name)
    except Exception:
        return []

    [q_embed] = _embed([question])
    results = coll.query(query_embeddings=[q_embed], n_results=top_k, include=["documents", "metadatas"])

    out = []
    docs = results["documents"][0] if results["documents"] else []
    metas = results["metadatas"][0] if results["metadatas"] else []
    for doc, meta in zip(docs, metas):
        out.append({"content": doc, "source": meta.get("source", ""), "metadata": meta or {}})
    return out
