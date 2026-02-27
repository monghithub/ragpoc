# Fase 1 — Decisiones de arquitectura

> Este documento se completará tras la Fase 0 de reconocimiento.

## Componentes a evaluar

### Vector store

Opciones:
- **ChromaDB** (local, sin servidor) — persistencia + facilidad de ingesta + metadata filtering
- **Qdrant** (Docker) — más features pero requiere contenedor
- **FAISS** (in-memory) — rápido pero sin persistencia nativa

### Embeddings

Opciones:
- `all-MiniLM-L6-v2` — ligero, rápido
- `bge-m3` — multilingüe, mejor para datos mixtos español/inglés

### UI web

Opciones:
- **Open WebUI** — investigar compatibilidad con embedding model externo
- **AnythingLLM** — integración nativa con backends OpenAI-compatible
- **Streamlit / FastAPI** — implementación Python mínima, máximo control

### Orquestación RAG

Opciones:
- **LlamaIndex** — abstracción limpia sobre vector stores
- **LangChain** — ecosistema amplio pero más complejo
- **Implementación directa** — mínimas dependencias, máximo control

## Decisiones tomadas

(pendiente)

## Justificación

(pendiente)
