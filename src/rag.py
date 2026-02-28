"""Pipeline RAG: query → retrieve → prompt → LLM."""

import time

from openai import OpenAI

from .config import LEMONADE_BASE_URL, LEMONADE_API_KEY, LEMONADE_MODEL, RAG_SYSTEM_PROMPT, TOP_K
from .vectorstore import search


def _build_prompt(query: str, context_chunks: list[dict]) -> list[dict]:
    """Construye el prompt con contexto inyectado."""
    if context_chunks:
        context_text = "\n\n---\n\n".join(
            f"[Fuente: {c['metadata']['source']}, chunk {c['metadata']['chunk_index']}]\n{c['text']}"
            for c in context_chunks
        )
        user_content = f"""Contexto recuperado de los documentos:

{context_text}

---

Pregunta: {query}"""
    else:
        user_content = f"""No se encontró contexto relevante en los documentos.

Pregunta: {query}"""

    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def query_rag(query: str, top_k: int = TOP_K, model: str | None = None) -> dict:
    """Ejecuta el pipeline RAG completo."""
    # 1. Retrieve
    chunks = search(query, top_k=top_k)

    # 2. Build prompt
    messages = _build_prompt(query, chunks)

    # 3. Call LLM (con reintentos por si Lemonade está cargando el modelo)
    client = OpenAI(base_url=LEMONADE_BASE_URL, api_key=LEMONADE_API_KEY)
    answer = None
    usage = None

    for attempt in range(3):
        response = client.chat.completions.create(
            model=model or LEMONADE_MODEL,
            messages=messages,
        )
        if response.choices:
            answer = response.choices[0].message.content
            usage = response.usage
            if answer is not None:
                break
        time.sleep(5)

    if answer is None:
        answer = "(Lemonade no devolvió respuesta — el modelo puede estar cargándose)"

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "source": c["metadata"]["source"],
                "chunk_index": c["metadata"]["chunk_index"],
                "distance": c["distance"],
                "preview": c["text"][:200],
            }
            for c in chunks
        ],
        "usage": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        } if usage else None,
        "model": model or LEMONADE_MODEL,
    }
