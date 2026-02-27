"""Vector store con ChromaDB (modo embedded, persistente)."""

import chromadb

from .config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, TOP_K
from .embeddings import embed_texts, embed_query


_client = None
_collection = None


def get_collection() -> chromadb.Collection:
    """Obtiene la colección de ChromaDB (singleton)."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def ingest_chunks(chunks: list[dict]) -> int:
    """Ingesta chunks en ChromaDB. Retorna cantidad de chunks añadidos."""
    if not chunks:
        return 0

    collection = get_collection()
    existing = collection.count()

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [f"doc_{existing + i}" for i in range(len(chunks))]
    embeddings = embed_texts(texts)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    """Busca los chunks más relevantes para una query."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "text": doc,
            "metadata": meta,
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def get_stats() -> dict:
    """Retorna estadísticas de la colección."""
    collection = get_collection()
    return {
        "total_chunks": collection.count(),
        "collection_name": CHROMA_COLLECTION,
        "persist_dir": CHROMA_PERSIST_DIR,
    }
