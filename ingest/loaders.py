"""Load documents from PDF, Markdown, GitHub, Notion, and Google Drive."""
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


# --- Notion ---
def load_notion(api_key: str, database_id: str | None = None, page_ids: list[str] | None = None) -> Iterator[Document]:
    """Load pages from a Notion database or specific page IDs. Requires: pip install notion-client"""
    try:
        from notion_client import Client
    except ImportError:
        raise ImportError("Install notion-client: pip install notion-client")
    client = Client(auth=api_key)
    page_ids = list(page_ids or [])

    if database_id:
        resp = client.databases.query(database_id=database_id)
        page_ids.extend(p["id"] for p in resp.get("results", []))

    for page_id in page_ids:
        try:
            blocks = client.blocks.children.list(block_id=page_id)
            parts = []
            for block in blocks.get("results", []):
                b = block.get(block["type"], {})
                if "rich_text" in b:
                    for rt in b["rich_text"]:
                        if "plain_text" in rt:
                            parts.append(rt["plain_text"])
            if parts:
                source = f"notion.so/page/{page_id}"
                yield Document(content="\n".join(parts).strip(), source=source, meta={"page_id": page_id})
        except Exception:
            continue


# --- Google Drive ---
def load_google_drive(credentials_path: str, folder_id: str) -> Iterator[Document]:
    """Load Google Docs (exported as text) from a Drive folder. Requires: pip install google-api-python-client google-auth"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError("Install: pip install google-api-python-client google-auth")
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)

    result = service.files().list(
        q=f"'{folder_id}' in parents",
        pageSize=100,
        fields="files(id, name, mimeType)",
    ).execute()
    for f in result.get("files", []):
        mime = f.get("mimeType", "")
        if mime != "application/vnd.google-apps.document":
            continue
        try:
            content = service.files().export(fileId=f["id"], mimeType="text/plain").execute()
            text = content.decode("utf-8", errors="replace").strip()
            if text:
                source = f"drive.google.com/file/d/{f['id']}"
                yield Document(content=text, source=source, meta={"name": f.get("name", "")})
        except Exception:
            continue


def load_documents(
    *,
    data_dir: Path | None = None,
    github: str | None = None,
    github_token: str | None = None,
    notion_api_key: str | None = None,
    notion_database_id: str | None = None,
    notion_page_ids: list[str] | None = None,
    gdrive_credentials_path: str | None = None,
    gdrive_folder_id: str | None = None,
) -> list[Document]:
    """
    Load documents from local data dir, GitHub, Notion, and/or Google Drive.

    - data_dir: folder with PDF/md/txt files (default: app_config.DATA_DIR)
    - github: "owner/repo" or "owner/repo:branch"
    - github_token: optional token for private repos
    - notion_*: Notion integration (api_key + database_id or page_ids)
    - gdrive_*: Google Drive folder (credentials JSON path + folder_id)
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

    if notion_api_key and (notion_database_id or notion_page_ids):
        try:
            out.extend(load_notion(notion_api_key, database_id=notion_database_id, page_ids=notion_page_ids))
        except Exception:
            pass

    if gdrive_credentials_path and gdrive_folder_id:
        try:
            out.extend(load_google_drive(gdrive_credentials_path, gdrive_folder_id))
        except Exception:
            pass

    return out
