"""FastAPI backend for the RAG document Q&A portal.

Endpoints:
- GET    /health              -> simple health check
- GET    /documents           -> list indexed local documents under DATA_DIR
- POST   /upload              -> upload a file into DATA_DIR and re-index all docs
- DELETE /documents/{filename} -> delete a document and re-index
- POST   /ask                 -> run RAG over indexed docs and return answer + sources
"""
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app_config import DATA_DIR
from chat import rag_query
from ingest import Document, load_documents
from store import add_documents


app = FastAPI(title="RAG Document Q&A API")


# Allow local React dev server by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Source(BaseModel):
    source: str
    metadata: dict[str, Any] | None = None


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]


class DocumentInfo(BaseModel):
    name: str
    path: str
    size: int
    modified_ts: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/documents", response_model=List[DocumentInfo])
def list_documents() -> List[DocumentInfo]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    docs: List[DocumentInfo] = []
    for path in DATA_DIR.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        docs.append(
            DocumentInfo(
                name=path.name,
                path=str(path.relative_to(DATA_DIR)),
                size=stat.st_size,
                modified_ts=stat.st_mtime,
            )
        )
    return docs


def _save_uploaded_file(file: UploadFile) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "uploaded").name
    dest = DATA_DIR / safe_name
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    dest.write_bytes(content)
    return dest


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    """Upload a file into DATA_DIR and re-index all local documents."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")
    try:
        # Save uploaded file
        _save_uploaded_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        await file.close()

    # Re-load and index all documents under DATA_DIR
    try:
        docs = load_documents(data_dir=DATA_DIR)
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found after upload.")
        chunks = add_documents(docs)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index documents: {e}")

    return {"message": "Document uploaded and indexed.", "documents_indexed": len(docs), "chunks_added": chunks}


def _reindex() -> int:
    """Re-load and re-index all documents under DATA_DIR. Returns chunk count."""
    docs = load_documents(data_dir=DATA_DIR)
    if not docs:
        return 0
    return add_documents(docs)


@app.delete("/documents/{filename}")
def delete_document(filename: str) -> dict:
    """Delete a document from DATA_DIR and re-index remaining documents."""
    safe_name = Path(filename).name
    target = DATA_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Document '{safe_name}' not found.")
    try:
        target.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {e}")

    try:
        chunks = _reindex()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-index after deletion: {e}")

    return {"message": f"'{safe_name}' deleted.", "chunks_remaining": chunks}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        answer, sources = rag_query(question)
    except ValueError as e:
        # Likely no API key / provider configured
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")

    out_sources: List[Source] = []
    for s in sources or []:
        out_sources.append(
            Source(
                source=str(s.get("source", "")),
                metadata=s.get("metadata") or {},
            )
        )

    return AskResponse(answer=answer, sources=out_sources)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

