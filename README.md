# DocuMind AI

**AI-powered document Q&A portal** — upload PDFs, markdown, and text files, then ask questions and get accurate answers with source citations.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.133-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_store-FF6F00)

---

## Features

- **Document upload** — drag-and-drop or click to upload PDF, Markdown, TXT, and RST files
- **AI-powered Q&A** — ask natural language questions about your documents
- **Source citations** — every answer links back to the exact source documents
- **Multiple LLM providers** — supports Google Gemini (free tier), OpenAI, and Ollama (local)
- **Vector search** — uses ChromaDB for fast semantic retrieval over document chunks
- **Document management** — view, upload, and delete documents from the sidebar
- **Modern UI** — dark theme, glassmorphism effects, smooth animations, fully responsive
- **Mobile friendly** — collapsible sidebar with overlay for mobile devices

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Vector DB** | ChromaDB (persistent local storage) |
| **LLM** | Google Gemini / OpenAI GPT / Ollama (configurable) |
| **Embeddings** | Gemini Embedding / OpenAI text-embedding-3-small / Nomic Embed Text |
| **Document Parsing** | pypdf, custom markdown/text loaders |

## Architecture

```
┌─────────────────┐     HTTP/REST     ┌──────────────────────┐
│  React Frontend │  ◄──────────────► │   FastAPI Backend     │
│  (Vite + TS)    │                   │                      │
└─────────────────┘                   │  ┌────────────────┐  │
                                      │  │ Document Loader │  │
                                      │  │ (PDF/MD/TXT)   │  │
                                      │  └───────┬────────┘  │
                                      │          │           │
                                      │  ┌───────▼────────┐  │
                                      │  │   Chunker      │  │
                                      │  │ (800 char,     │  │
                                      │  │  150 overlap)  │  │
                                      │  └───────┬────────┘  │
                                      │          │           │
                                      │  ┌───────▼────────┐  │
                                      │  │   ChromaDB     │  │
                                      │  │ (Embeddings +  │  │
                                      │  │  Vector Store) │  │
                                      │  └───────┬────────┘  │
                                      │          │           │
                                      │  ┌───────▼────────┐  │
                                      │  │   LLM (RAG)    │  │
                                      │  │ (Gemini/GPT/   │  │
                                      │  │  Ollama)       │  │
                                      │  └────────────────┘  │
                                      └──────────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- An API key for **Google Gemini** (free) or **OpenAI**, or a local **Ollama** installation

### 1. Clone and set up the backend

```bash
git clone <your-repo-url>
cd documind

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your API key:

```bash
cp .env.example .env
```

Choose one provider:

| Provider | Env vars to set |
|----------|----------------|
| **Gemini** (free) | `USE_GEMINI=true`, `GEMINI_API_KEY=your-key` |
| **OpenAI** | `OPENAI_API_KEY=your-key` |
| **Ollama** (local) | `USE_OLLAMA=true` (run `ollama pull llama3.2` and `ollama pull nomic-embed-text` first) |

### 3. Start the backend

```bash
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Check `http://localhost:8000/docs` for the interactive Swagger docs.

### 4. Start the frontend

```bash
cd frontend
npm install
npx vite
```

Open `http://localhost:3000` in your browser.

### 5. Use it

1. **Upload** a PDF, markdown, or text file using the sidebar
2. **Ask** a question in the chat panel
3. **View** the AI-generated answer with source citations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/documents` | List all indexed documents |
| `POST` | `/upload` | Upload and index a document (multipart form) |
| `DELETE` | `/documents/{filename}` | Delete a document and re-index |
| `POST` | `/ask` | Ask a question (JSON body: `{ "question": "..." }`) |

## Screenshots

> Add screenshots of your running app here for your portfolio.
>
> Suggested screenshots:
> 1. Empty state with upload prompt
> 2. Documents uploaded in sidebar
> 3. Q&A conversation with citations

## License

MIT
