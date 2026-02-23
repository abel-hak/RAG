"""Split documents into overlapping chunks for embedding."""
from typing import Iterator

from app_config import CHUNK_SIZE, CHUNK_OVERLAP
from ingest import Document


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by character count."""
    if not text or len(text) <= chunk_size:
        return [text] if text and text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at sentence or line boundary
        if end < len(text):
            for sep in ("\n\n", "\n", ". ", " "):
                last = chunk.rfind(sep)
                if last > chunk_size // 2:
                    chunk = chunk[: last + len(sep)]
                    end = start + len(chunk)
                    break
        chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def chunk_document(doc: Document, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterator[tuple[str, dict]]:
    """Yield (text, metadata) for each chunk of a document."""
    chunks = chunk_text(doc.content, chunk_size, overlap)
    for i, text in enumerate(chunks):
        meta = {**(doc.meta or {}), "source": doc.source}
        if len(chunks) > 1:
            meta["chunk_index"] = i
        yield text, meta
