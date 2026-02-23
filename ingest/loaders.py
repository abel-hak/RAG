"""Load documents from PDF, Markdown, and GitHub."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from app_config import DATA_DIR


@dataclass
class Document:
    """A document with content and source metadata for citations."""
    content: str
    source: str
    meta: dict | None = None

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}


def _ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


# --- PDF ---
def load_pdf(path: Path) -> Iterator[Document]:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Install pypdf: pip install pypdf")
    reader = PdfReader(path)
    source = str(path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            yield Document(content=text.strip(), source=source, meta={"page": i + 1})


# --- Markdown / plain text ---
def load_text(path: Path) -> Iterator[Document]:
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    for enc in encodings:
        try:
            text = path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        return
    if text.strip():
        yield Document(content=text.strip(), source=str(path), meta={})


# --- GitHub ---
def load_github_repo(owner: str, repo: str, branch: str = "main", token: str | None = None) -> Iterator[Document]:
    """Load markdown/text files from a GitHub repo (e.g. README, .md files)."""
    try:
        from github import Github
    except ImportError:
        raise ImportError("Install PyGithub: pip install PyGithub")
    g = Github(token) if token else Github()
    r = g.get_repo(f"{owner}/{repo}")
    try:
        contents = r.get_contents("", ref=branch)
    except Exception:
        contents = r.get_contents("", ref="main")
    stack = list(contents)
    seen = set()
    while stack:
        entry = stack.pop()
        path = entry.path
        if path in seen:
            continue
        seen.add(path)
        if entry.type == "dir":
            try:
                stack.extend(r.get_contents(path, ref=branch or "main"))
            except Exception:
                stack.extend(r.get_contents(path, ref="main"))
            continue
        if not path.endswith((".md", ".markdown", ".txt", ".rst", ".py", ".js", ".ts", ".tsx", ".jsx")):
            continue
        try:
            raw = entry.decoded_content.decode("utf-8", errors="replace")
        except Exception:
            continue
        if raw.strip():
            source = f"github.com/{owner}/{repo}/blob/{branch or 'main'}/{path}"
            yield Document(content=raw.strip(), source=source, meta={"path": path})


def load_documents(
    *,
    data_dir: Path | None = None,
    github: str | None = None,
    github_token: str | None = None,
) -> list[Document]:
    """
    Load all documents from local data dir and optionally one GitHub repo.

    - data_dir: folder with PDF/md/txt files (default: config.DATA_DIR)
    - github: "owner/repo" or "owner/repo:branch"
    - github_token: optional token for private repos / higher rate limit
    """
    out: list[Document] = []
    data_dir = data_dir or _ensure_data_dir()

    for path in data_dir.rglob("*"):
        if not path.is_file():
            continue
        suf = path.suffix.lower()
        try:
            if suf == ".pdf":
                out.extend(load_pdf(path))
            elif suf in (".md", ".markdown", ".txt", ".rst"):
                out.extend(load_text(path))
        except Exception:
            continue

    if github:
        parts = github.strip().split(":", 1)
        owner_repo = parts[0].strip()
        branch = parts[1].strip() if len(parts) > 1 else "main"
        if "/" in owner_repo:
            owner, repo = owner_repo.split("/", 1)
            out.extend(load_github_repo(owner, repo, branch=branch, token=github_token))

    return out
