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
st.title("📚 Personal Knowledge Base Chat")
st.caption("Ask questions over your notes, PDFs, and GitHub repos. Answers include source citations.")

# Sidebar: index controls
with st.sidebar:
    st.header("Index documents")
    st.markdown("Add files to the `data` folder (PDF, .md, .txt), then click **Index**.")
    github_repo = st.text_input("GitHub repo (owner/repo or owner/repo:branch)", placeholder="e.g. facebook/react")
    github_token = st.text_input("GitHub token (optional)", type="password", help="For private repos or higher rate limit")
    if st.button("Index documents", type="primary"):
        with st.spinner("Loading and embedding documents..."):
            try:
                docs = load_documents(data_dir=DATA_DIR, github=github_repo or None, github_token=github_token or None)
                if not docs:
                    st.warning("No documents found. Add files to the `data` folder or specify a GitHub repo.")
                else:
                    n = add_documents(docs)
                    st.success(f"Indexed {n} chunks from {len(docs)} document(s).")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.markdown("---")
    st.markdown("**Sources:** `data/` folder + optional GitHub repo.")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.code(s["source"], language=None)

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
                            st.code(s["source"], language=None)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })
            except Exception as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": str(e), "sources": []})
