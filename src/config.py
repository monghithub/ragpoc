"""Configuración central del RAG POC."""

import os

# Lemonade Server
LEMONADE_BASE_URL = os.getenv("LEMONADE_BASE_URL", "http://localhost:8000/api/v1")
LEMONADE_API_KEY = os.getenv("LEMONADE_API_KEY", "lemonade")
LEMONADE_MODEL_DEV = "Qwen3-8B-GGUF"
LEMONADE_MODEL_PROD = "Qwen3-Next-80B-A3B-Instruct-GGUF"
LEMONADE_MODEL = os.getenv("LEMONADE_MODEL", LEMONADE_MODEL_DEV)

# Embeddings
EMBEDDING_MODEL = "BAAI/bge-m3"

# ChromaDB
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
CHROMA_COLLECTION = "ragpoc"

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "5"))

# System prompt para RAG
RAG_SYSTEM_PROMPT = """Eres un asistente que responde preguntas basándose en el contexto proporcionado.
Si la respuesta no está en el contexto, di claramente que no tienes esa información.
Responde en el mismo idioma en que se hace la pregunta."""
