"""
Personal Knowledge Base Chatbot — Chat with your notes, PDFs, and GitHub repos.
Run: streamlit run app.py
"""
import os
import sys
from pathlib import Path

# Ensure project root is on path (Streamlit can run with a different cwd)
_root = Path(__file__).resolve().parent
_cwd = Path(os.getcwd())
for _p in (_root, _cwd):
    _p = str(_p)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

from app_config import DATA_DIR
from ingest import load_documents
from store import add_documents
from chat import rag_query


st.set_page_config(page_title="Knowledge Base Chat", page_icon="📚", layout="centered")

# Dark mode toggle (persisted in session)
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Inject theme: dark if enabled
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        [data-testid="stHeader"] { background: rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Personal Knowledge Base Chat")
st.caption("Ask questions over your notes, PDFs, GitHub, Notion & Google Drive. Answers include source citations.")

# Sidebar: index controls
with st.sidebar:
    st.header("Index documents")
    st.markdown("Add files to the `data` folder (PDF, .md, .txt), then optionally add sources below.")
    github_repo = st.text_input("GitHub repo (owner/repo or owner/repo:branch)", placeholder="e.g. facebook/react")
    github_token = st.text_input("GitHub token (optional)", type="password", help="For private repos or higher rate limit")

    st.markdown("**Notion** (optional)")
    notion_api_key = st.text_input("Notion API key", type="password", key="notion_key", help="From notion.so/my-integrations")
    notion_database_id = st.text_input("Notion database ID", placeholder="Leave empty to use page IDs", key="notion_db")

    st.markdown("**Google Drive** (optional)")
    gdrive_folder_id = st.text_input("Drive folder ID", placeholder="From folder URL", key="gdrive_folder")
    gdrive_creds = st.text_input("Path to credentials.json", placeholder="e.g. credentials.json", key="gdrive_creds")

    if st.button("Index documents", type="primary"):
        with st.spinner("Loading and embedding documents..."):
            try:
                docs = load_documents(
                    data_dir=DATA_DIR,
                    github=github_repo or None,
                    github_token=github_token or None,
                    notion_api_key=notion_api_key or None,
                    notion_database_id=notion_database_id or None,
                    gdrive_credentials_path=gdrive_creds or None,
                    gdrive_folder_id=gdrive_folder_id or None,
                )
                if not docs:
                    st.warning("No documents found. Add files to the `data` folder or configure a source above.")
                else:
                    n = add_documents(docs)
                    st.success(f"Indexed {n} chunks from {len(docs)} document(s).")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.session_state.dark_mode = st.toggle("Dark mode", value=st.session_state.dark_mode, help="Switch theme")
    if st.button("🗑️ Clear chat", help="Remove all messages and start over"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Sources:** `data/` + GitHub + Notion + Drive")

# Chat
def _render_source(source: str) -> str:
    """Return markdown for a source: clickable link if URL-like, else inline code."""
    s = (source or "").strip()
    if not s:
        return ""
    if s.startswith("http"):
        url = s
    elif "github.com/" in s or "notion.so/" in s or "drive.google.com/" in s:
        url = "https://" + s
    else:
        return f"`{s}`"
    label = s[:80] + ("..." if len(s) > 80 else "")
    return f"[{label}]({url})"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Cited sources"):
                for s in msg["sources"]:
                    src = s.get("source", "")
                    st.markdown(_render_source(src))

if prompt := st.chat_input("Ask something about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching and answering..."):
            try:
                answer, sources = rag_query(prompt)
                st.markdown(answer)
                if sources:
                    with st.expander("Cited sources"):
                        for s in sources:
                            st.markdown(_render_source(s.get("source", "")))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })
            except Exception as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": str(e), "sources": []})
