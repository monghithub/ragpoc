"""Prueba de humo del ciclo RAG completo."""

import sys
import time
import json

sys.path.insert(0, ".")
from src.chunking import process_file
from src.vectorstore import ingest_chunks, search, get_stats
from src.rag import query_rag


def ingest_test_docs():
    """Ingesta los documentos de prueba."""
    docs = [
        "data/ejemplo-arquitectura.md",
        "data/ejemplo-lemonade.txt",
        "data/ejemplo-hardware.txt",
    ]

    total = 0
    for doc in docs:
        chunks = process_file(doc)
        count = ingest_chunks(chunks)
        print(f"  {doc}: {count} chunks")
        total += count

    stats = get_stats()
    print(f"  Total chunks en vector store: {stats['total_chunks']}")
    return total


def test_query_in_corpus(model):
    """Consulta con respuesta en los documentos."""
    query = "¿Cuántos CUs tiene la GPU Radeon 8060S?"
    print(f"  Query: {query}")

    start = time.time()
    result = query_rag(query, model=model)
    elapsed = time.time() - start

    print(f"  Respuesta: {result['answer'][:200]}")
    print(f"  Fuentes: {[s['source'] for s in result['sources']]}")
    print(f"  Latencia: {elapsed:.1f}s")
    if result["usage"]:
        print(f"  Tokens: {result['usage']['total_tokens']}")
    return result, elapsed


def test_query_ambiguous(model):
    """Consulta ambigua."""
    query = "¿Qué modelo es mejor?"
    print(f"  Query: {query}")

    start = time.time()
    result = query_rag(query, model=model)
    elapsed = time.time() - start

    print(f"  Respuesta: {result['answer'][:200]}")
    print(f"  Fuentes: {[s['source'] for s in result['sources']]}")
    print(f"  Latencia: {elapsed:.1f}s")
    if result["usage"]:
        print(f"  Tokens: {result['usage']['total_tokens']}")
    return result, elapsed


def test_query_out_of_corpus(model):
    """Consulta fuera del corpus."""
    query = "¿Cuál es la receta de paella valenciana?"
    print(f"  Query: {query}")

    start = time.time()
    result = query_rag(query, model=model)
    elapsed = time.time() - start

    print(f"  Respuesta: {result['answer'][:200]}")
    print(f"  Fuentes: {[s['source'] for s in result['sources']]}")
    print(f"  Latencia: {elapsed:.1f}s")
    if result["usage"]:
        print(f"  Tokens: {result['usage']['total_tokens']}")
    return result, elapsed


if __name__ == "__main__":
    from src.config import LEMONADE_MODEL

    model = LEMONADE_MODEL
    print(f"=== Prueba de humo RAG (modelo: {model}) ===\n")

    print("1. Ingesta de documentos de prueba")
    ingest_test_docs()
    print()

    print("2. Consulta con respuesta en los docs")
    r1, t1 = test_query_in_corpus(model)
    print()

    print("3. Consulta ambigua")
    r2, t2 = test_query_ambiguous(model)
    print()

    print("4. Consulta fuera del corpus")
    r3, t3 = test_query_out_of_corpus(model)
    print()

    print("=== Resumen ===")
    print(f"  Latencia promedio: {(t1 + t2 + t3) / 3:.1f}s")
    total_tokens = sum(
        r["usage"]["total_tokens"]
        for r in [r1, r2, r3]
        if r["usage"]
    )
    print(f"  Tokens totales consumidos: {total_tokens}")
    print(f"  Modelo usado: {model}")
    print("=== Prueba de humo completa ===")
