"""App configuration from environment (named app_config to avoid clash with streamlit.config)."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
DATA_DIR = BASE_DIR / "data"  # local files (PDFs, markdown) go here

# Provider: "gemini" (free cloud), "ollama" (local), or "openai" (paid)
USE_GEMINI = os.getenv("USE_GEMINI", "").lower() in ("1", "true", "yes")
USE_OLLAMA = os.getenv("USE_OLLAMA", "").lower() in ("1", "true", "yes")

# Google Gemini (free tier; get key at https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash-lite")

# OpenAI (used when neither Gemini nor Ollama)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# Ollama (local; run "ollama pull nomic-embed-text" and "ollama pull llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")

# RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5

# Collection name in Chroma
COLLECTION_NAME = "knowledge_base"
