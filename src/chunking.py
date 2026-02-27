"""Chunking de documentos con soporte para múltiples formatos."""

from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument

from .config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text(file_path: str | Path) -> str:
    """Extrae texto de un archivo según su extensión."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif suffix in (".txt", ".md", ".py", ".js", ".ts", ".java", ".go", ".rs", ".c", ".cpp", ".h"):
        return path.read_text(encoding="utf-8")
    else:
        return path.read_text(encoding="utf-8")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide texto en chunks con overlap."""
    if not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def process_file(file_path: str | Path) -> list[dict]:
    """Procesa un archivo: extrae texto, hace chunking, retorna chunks con metadata."""
    path = Path(file_path)
    text = extract_text(path)
    chunks = chunk_text(text)

    return [
        {
            "text": chunk,
            "metadata": {
                "source": path.name,
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        }
        for i, chunk in enumerate(chunks)
    ]
