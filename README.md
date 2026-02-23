# Personal Knowledge Base Chatbot

Chat with your own data: **notes**, **PDFs**, and **GitHub repos**. Answers are grounded in your documents and include **source citations**.

## Features

- **Local files**: PDF, Markdown (`.md`), and text (`.txt`) from a `data/` folder
- **GitHub**: Index a repo (e.g. README and code/docs) by entering `owner/repo` or `owner/repo:branch`
- **RAG pipeline**: Chunking → embeddings (OpenAI) → Chroma vector store → retrieval → LLM answer with citations
- **Streamlit UI**: Chat interface + sidebar to (re-)index documents

## Setup

1. **Clone or open this project**, then create a virtual environment and install dependencies:

   ```bash
   cd RAG1
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key** (required for embeddings and chat):

   - Copy `.env.example` to `.env`
   - Add your key: `OPENAI_API_KEY=sk-your-key-here`
   - Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

3. **Optional**: Add documents to index:
   - Create a `data` folder in the project root and put PDFs or `.md`/`.txt` files there, or
   - Use the sidebar in the app to index a **GitHub repo** (e.g. `facebook/react`).

## Run the app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501). Use the sidebar to **Index documents**, then ask questions in the chat. Answers will show cited sources.

## Project structure

```
RAG1/
  app.py           # Streamlit chat UI
  config.py        # Settings (paths, models, chunk size)
  chunk.py         # Text chunking for RAG
  store.py         # Chroma embeddings + similarity search
  chat.py          # RAG: retrieve + LLM with citations
  ingest/
    loaders.py     # Load PDF, Markdown, GitHub
  data/            # Put your PDFs and notes here (created on first run)
  chroma_db/       # Vector DB (created on first index)
  .env             # OPENAI_API_KEY (create from .env.example)
  requirements.txt
```

## Optional: GitHub token

For **private repos** or higher rate limits, create a [GitHub Personal Access Token](https://github.com/settings/tokens) and enter it in the sidebar when indexing a repo.

## Tech stack (for CV / interviews)

- **RAG**: Chunking, OpenAI embeddings, vector search (Chroma), retrieval-augmented generation
- **Integrations**: Local files (PDF, Markdown), GitHub API (PyGithub)
- **Stack**: Python, Streamlit, OpenAI API, ChromaDB

You can extend this with **Notion** or **Google Drive** by adding loaders in `ingest/loaders.py` and wiring them in `load_documents()`.
