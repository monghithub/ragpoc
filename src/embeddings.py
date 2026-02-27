"""Pipeline de embeddings con sentence-transformers (bge-m3)."""

from sentence_transformers import SentenceTransformer

from .config import EMBEDDING_MODEL

_model = None


def get_model() -> SentenceTransformer:
    """Carga el modelo de embeddings (singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Genera embedding para una query."""
    return embed_texts([query])[0]
